"""Synthetic detector/guard regressions. No manga pixels or publication are edited."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image

SPEC = importlib.util.spec_from_file_location('fidelity', Path(__file__).with_name('check-source-fidelity.py'))
F = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(F)
CAL_SPEC = importlib.util.spec_from_file_location('calibration', Path(__file__).with_name('calibrate-source-fidelity.py'))
C = importlib.util.module_from_spec(CAL_SPEC)
CAL_SPEC.loader.exec_module(C)


def drawing():
    image = np.full((160, 200, 3), 255, dtype=np.uint8)
    cv2.rectangle(image, (15, 15), (185, 145), (0, 0, 0), 2)
    cv2.line(image, (45, 40), (45, 110), (0, 0, 0), 1)
    cv2.line(image, (45, 70), (90, 70), (0, 0, 0), 1)
    cv2.ellipse(image, (130, 70), (22, 12), 0, 0, 360, (0, 0, 0), 1)
    return image


class DetectorTests(unittest.TestCase):
    def test_identical_edges_have_exact_support(self):
        source = drawing()
        stats, maps = F.mode_analysis(source, source.copy(), F.MODES[0])
        self.assertGreater(stats['sourceToCandidate']['edgePixels'], 0)
        self.assertEqual(stats['sourceToCandidate']['beyond2Fraction'], 0)
        self.assertEqual(int(maps['sourceOrientationMismatch'].sum()), 0)

    def test_flat_pigment_change_does_not_look_like_translation(self):
        source = drawing()
        colored = np.where(source == 255, np.array([225, 210, 180], dtype=np.uint8), source)
        stats, _ = F.mode_analysis(source, colored, F.MODES[0])
        self.assertLess(stats['sourceToCandidate']['beyond2Fraction'], 0.01)

    def test_translation_is_not_registered_away(self):
        source = drawing()
        shifted = np.full_like(source, 255)
        shifted[5:, 6:] = source[:-5, :-6]
        stats, _ = F.mode_analysis(source, shifted, F.MODES[0])
        self.assertGreater(stats['sourceToCandidate']['beyond2Fraction'], 0.5)

    def test_small_missing_stroke_is_located_despite_good_page_average(self):
        source = drawing()
        missing = source.copy()
        missing[69:72, 65:91] = 255
        _, maps = F.mode_analysis(source, missing, F.MODES[0])
        region = F.window_stats(maps, [62, 65, 95, 77])
        self.assertGreater(region['missingProxyPixelsBeyond2'], 10)
        self.assertLess(np.mean(maps['missingProxy']), 0.01)

    def test_one_pixel_translation_stays_visible_in_exact_map_and_tiles(self):
        source = drawing()
        shifted = np.full_like(source, 255)
        shifted[:, 1:] = source[:, :-1]
        _, maps = F.mode_analysis(source, shifted, F.MODES[0])
        stats = F.window_stats(maps, [0, 0, source.shape[1], source.shape[0]])
        self.assertGreater(stats['sourceExactUnmatchedPixels'], 50)
        diagnostic = F.diagnostic_map(maps)
        self.assertTrue(np.any(np.all(diagnostic == [244, 160, 175], axis=2)))

    def test_added_stroke_uses_reverse_direction(self):
        source = drawing()
        added = source.copy()
        cv2.line(added, (105, 105), (150, 110), (0, 0, 0), 1)
        _, maps = F.mode_analysis(source, added, F.MODES[0])
        region = F.window_stats(maps, [100, 100, 155, 115])
        self.assertGreater(region['addedProxyPixelsBeyond2'], 30)

    def test_blank_and_missing_all_edges_are_not_divide_by_zero_or_perfect_match(self):
        blank = np.full_like(drawing(), 255)
        stats, _ = F.mode_analysis(drawing(), blank, F.MODES[0])
        self.assertEqual(stats['sourceToCandidate']['beyond2Fraction'], 1)
        self.assertGreater(stats['sourceToCandidate']['unboundedDistancePixels'], 0)
        self.assertIsNone(stats['candidateToSource']['withinPixels'])
        json.dumps(stats, allow_nan=False)

    def test_orientation_disagrees_even_when_edges_are_near(self):
        query = np.zeros((9, 9), dtype=bool)
        query[4, 4] = True
        target = query.copy()
        qa = np.zeros(query.shape, dtype=np.float32)
        ta = np.full(query.shape, np.pi / 2, dtype=np.float32)
        self.assertTrue(F.oriented_unmatched(query, target, qa, ta)[4, 4])


class CalibrationTests(unittest.TestCase):
    def test_accepted_upper_envelope_has_headroom_instead_of_zero_pixel_rule(self):
        rows = {str(i): {'globalMissingBeyond2': 0.10, 'globalAddedBeyond2': 0.05,
                          'localMissingP95': 0.30, 'localAddedP95': 0.20} for i in range(12)}
        limits = C.fit_thresholds(rows)
        self.assertGreater(limits['globalMissingBeyond2']['threshold'], 0.10)
        self.assertGreater(limits['globalAddedBeyond2']['threshold'], 0.05)
        self.assertGreaterEqual(limits['localMissingP95']['threshold'], 0.35)

    def test_sparse_reference_set_cannot_establish_a_threshold(self):
        with self.assertRaisesRegex(ValueError, 'eight'):
            C.fit_thresholds({'one': {'globalMissingBeyond2': 0.1}})

    def test_extreme_held_out_values_do_not_tune_calibration(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / 'report.json').write_text('{}')
            (base / 'summary.json').write_text('{}')
            files = {'source': {'sha256': 'source'}, 'candidate': {'sha256': 'candidate'}}
            cases, rows = [], {}
            for i in range(9):
                identifier = str(i)
                cases.append({'id': identifier, **files,
                              'historicalLabel': 'user_designated_accepted_chapter_reference',
                              'referenceSplit': 'held_out_validation' if i == 8 else 'calibration'})
                rows[identifier] = {'id': identifier, 'files': files, '_directory': base,
                                    'geometryMatchesDeclaration': True,
                                    'test_values': {'globalMissingBeyond2': 0.95 if i == 8 else 0.10}}
            plan = base / 'plan.json'
            plan.write_text(json.dumps({'cases': cases}))
            summary = {'planSha256': C.binding(plan)['sha256'], 'scriptSha256': 'detector', 'dependencies': {}}
            evaluation = {'candidate': {**rows['0'], 'id': 'candidate'}}
            with patch.object(C, 'load_run', side_effect=[(summary, rows), (summary, evaluation)]), \
                    patch.object(C, 'measurements', side_effect=lambda report: report['test_values']):
                result = C.run(plan, base, base, base / 'calibration')
            self.assertEqual(result['thresholds']['globalMissingBeyond2']['acceptedMaximum'], 0.10)
            self.assertEqual(result['heldOutWithinReferenceRange'], 0)
            candidate = result['candidateResults'][0]
            self.assertEqual(candidate['referenceRangeStatus'], 'within_accepted_reference_range')
            self.assertFalse(candidate['automaticArtisticPass'])
            self.assertFalse(candidate['userApproved'])

    def test_threshold_never_exceeds_a_fraction(self):
        rows = {str(i): {'localMissingP95': 0.95} for i in range(8)}
        self.assertEqual(C.fit_thresholds(rows)['localMissingP95']['threshold'], 1)


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.source = self.base / 'source.png'
        Image.fromarray(drawing()).save(self.source)
        self.case = {'id': 'test', 'source': self.binding(self.source),
                     'candidate': self.binding(self.source), 'padding': [0, 0, 0, 0]}

    def tearDown(self):
        self.tmp.cleanup()

    def binding(self, path):
        return {'path': str(path), 'sha256': F.sha(path.read_bytes())}

    def test_bad_sha_writes_nothing(self):
        self.case['source']['sha256'] = '0' * 64
        plan = self.base / 'plan.json'
        plan.write_text(json.dumps({'schema': 1, 'cases': [self.case]}))
        out = self.base / 'inspection'
        with self.assertRaisesRegex(ValueError, 'SHA mismatch'):
            F.run(plan, out)
        self.assertFalse(out.exists())

    def test_unexplained_dimensions_reject_without_resizing(self):
        candidate = self.base / 'smaller.png'
        Image.fromarray(drawing()[:-1]).save(candidate)
        self.case['candidate'] = self.binding(candidate)
        result = F.analyze_case(self.case, self.base, self.base / 'inspection')
        self.assertEqual(result['automaticDecision'], 'reject_geometry')
        self.assertFalse(result['eligibleForPublication'])

    def test_padding_requires_real_original_preparation(self):
        self.case['padding'] = [0, 0, 0, 4]
        with self.assertRaisesRegex(ValueError, 'requires original preparation'):
            F.prepare_case(self.case, self.base)

    def test_declared_padding_verifies_decoded_original_then_detects_corruption(self):
        prepared = self.base / 'prepared.png'
        padded = np.pad(drawing(), ((0, 4), (0, 0), (0, 0)), constant_values=255)
        Image.fromarray(padded).save(prepared)
        metadata = self.base / 'input.json'
        metadata.write_text(json.dumps({'originalSha256': self.case['source']['sha256'],
                                       'padding': {'left': 0, 'top': 0, 'right': 0, 'bottom': 4},
                                       'scaledContent': {'width': 200, 'height': 160}}))
        self.case.update({'padding': [0, 0, 0, 4], 'candidate': self.binding(prepared),
                          'preparation': {'image': self.binding(prepared), 'metadata': self.binding(metadata)}})
        result, source, candidate = F.prepare_case(self.case, self.base)
        self.assertTrue(result['preparedContentPixelsEqual'])
        self.assertTrue(np.array_equal(source, candidate))
        padded[50, 50] = 0
        Image.fromarray(padded).save(prepared)
        self.case['preparation']['image'] = self.binding(prepared)
        self.case['candidate'] = self.binding(prepared)
        with self.assertRaisesRegex(ValueError, 'content pixels differ'):
            F.prepare_case(self.case, self.base)

    def test_out_of_bounds_locator_rejected(self):
        self.case['criticalRegions'] = [{'id': 'bad', 'box': [190, 150, 220, 200]}]
        with self.assertRaisesRegex(ValueError, 'in-bounds'):
            F.prepare_case(self.case, self.base)

    def test_run_never_auto_approves_or_overwrites(self):
        plan = self.base / 'plan.json'
        plan.write_text(json.dumps({'schema': 1, 'cases': [self.case]}))
        out = self.base / 'inspection'
        result = F.run(plan, out)
        self.assertFalse(result['automaticQualityPassSupported'])
        self.assertFalse(result['cases'][0]['eligibleForPublication'])
        self.assertEqual(result['cases'][0]['automaticDecision'], 'unverified')
        self.assertEqual(self.binding(self.source), self.case['source'])
        with self.assertRaisesRegex(ValueError, 'new directory'):
            F.run(plan, out)


if __name__ == '__main__':
    cv2.setNumThreads(2)
    unittest.main()
