"""Derive tolerant review thresholds from accepted references, never from rejected pages.

The thresholds flag candidates for source review; they do not approve image quality.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

RULE = 'accepted-upper-envelope-plus-margin-v1'


def binding(path):
    return {'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def load_run(folder):
    summary = json.loads((folder / 'summary.json').read_text())
    if not summary.get('inputFilesUnchanged'):
        raise ValueError('Incomplete or invalid diagnostic run')
    rows = {}
    for case in summary['cases']:
        file = folder / case['id'] / 'report.json'
        report = json.loads(file.read_text())
        if report['files'] != case['files']:
            raise ValueError('Report bindings differ from run summary')
        report['_directory'] = file.parent
        rows[case['id']] = report
    return summary, rows


def measurements(report):
    if not report['geometryMatchesDeclaration']:
        return None
    fine = next(m for m in report['modes'] if m['name'] == 'fine')
    tiles = json.loads((report['_directory'] / 'fine-all-tiles.json').read_text())
    # Do not let mostly blank tiles make a page look better or create unstable ratios.
    missing = [t['missingProxyFraction'] for t in tiles if t['sourceEdgePixels'] >= 64]
    added = [t['addedProxyFraction'] for t in tiles if t['candidateEdgePixels'] >= 64]
    if not missing or not added:
        return None
    return {
        'globalMissingBeyond2': fine['sourceToCandidate']['beyond2Fraction'],
        'globalAddedBeyond2': fine['candidateToSource']['beyond2Fraction'],
        'localMissingP95': float(np.quantile(missing, 0.95)),
        'localAddedP95': float(np.quantile(added, 0.95)),
    }


def fit_thresholds(calibration):
    if len(calibration) < 8:
        raise ValueError('At least eight usable accepted calibration pages required')
    limits = {}
    for feature in next(iter(calibration.values())):
        values = [m[feature] for m in calibration.values()]
        upper = max(values)
        # Predetermined tolerance: accepted upper bound plus20%, at least2pp globally
        # and5pp for the noisier tile statistic. Round upward to whole percentage points.
        margin = max(upper * 0.2, 0.05 if feature.startswith('local') else 0.02)
        threshold = min(1.0, math.ceil((upper + margin) * 100 - 1e-9) / 100)
        limits[feature] = {'acceptedMinimum': min(values), 'acceptedMaximum': upper,
                           'threshold': threshold, 'marginBeforeRounding': margin}
    return limits


def assess(report, thresholds):
    values = measurements(report)
    if not report['geometryMatchesDeclaration']:
        status, exceeding = 'reject_geometry', []
    elif values is None:
        status, exceeding = 'insufficient_evidence', []
    else:
        exceeding = [key for key, value in values.items() if value > thresholds[key]['threshold']]
        status = 'needs_source_review' if exceeding else 'within_accepted_reference_range'
    return {'id': report['id'], 'files': report['files'], 'values': values,
            'referenceRangeStatus': status, 'exceedingFeatures': exceeding,
            'userApproved': False, 'automaticArtisticPass': False,
            'criticalContentReviewRequired': True, 'report': binding(report['_directory'] / 'report.json')}


def run(reference_plan, reference_reports, evaluate, out):
    if out.exists():
        raise ValueError('Output must be a new directory')
    plan = json.loads(reference_plan.read_text())
    summary, reference_rows = load_run(reference_reports)
    if summary['planSha256'] != binding(reference_plan)['sha256']:
        raise ValueError('Reference plan differs from diagnostic run')
    calibration, validation = {}, {}
    for case in plan['cases']:
        if case['historicalLabel'] not in ['user_approved_exact_version', 'user_designated_accepted_chapter_reference']:
            raise ValueError('Only accepted references may calibrate thresholds')
        report = reference_rows[case['id']]
        for role in ['source', 'candidate']:
            if report['files'][role]['sha256'] != case[role]['sha256']:
                raise ValueError('Reference source/candidate differs from plan')
        values = measurements(report)
        if values is None:
            raise ValueError('Reference has inadequate edge or geometry evidence')
        split = case['referenceSplit']
        if split == 'calibration':
            calibration[case['id']] = values
        elif split == 'held_out_validation':
            validation[case['id']] = values
        else:
            raise ValueError('Explicit calibration/held-out split required')
    if not validation:
        raise ValueError('Held-out accepted validation pages required')
    thresholds = fit_thresholds(calibration)
    validation_results = [assess(reference_rows[key], thresholds) for key in validation]
    evaluation_summary, evaluation_rows = load_run(evaluate)
    if evaluation_summary['scriptSha256'] != summary['scriptSha256'] or evaluation_summary['dependencies'] != summary['dependencies']:
        raise ValueError('Calibration and evaluation detectors must match')
    results = [assess(report, thresholds) for report in evaluation_rows.values()]
    # No threshold adjustment from validation, negative examples, or candidate outcomes.
    profile = {
        'schema': 1, 'rule': RULE, 'scriptSha256': binding(Path(__file__))['sha256'],
        'detectorSha256': summary['scriptSha256'], 'thresholds': thresholds,
        'calibrationMeasurements': calibration, 'validationMeasurements': validation,
        'validationResults': validation_results,
        'heldOutWithinReferenceRange': sum(x['referenceRangeStatus'] == 'within_accepted_reference_range' for x in validation_results),
        'heldOutCount': len(validation_results), 'candidateResults': results,
        'evidence': [binding(reference_plan), binding(reference_reports / 'summary.json'), binding(evaluate / 'summary.json')],
        'limits': ['Same-chapter empirical review thresholds, not universal quality pass thresholds.',
                   '2px is a distance measurement band, not permission to move every stroke.',
                   'Local P95 is robust to isolated raster variation; a changed glyph or expression needs separate content review.',
                   'Color/tone changes can create false alerts, and preserved ink can hide misplaced pigment.',
                   'Within range is not user approval or automatic publication eligibility.'],
        'providerCalls': 0,
    }
    out.mkdir(parents=True)
    (out / 'profile-and-results.json').write_text(json.dumps(profile, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'thresholds': thresholds, 'heldOutWithinRange': profile['heldOutWithinReferenceRange'],
                      'heldOutCount': len(validation_results), 'candidates': [(r['id'], r['referenceRangeStatus']) for r in results]}, ensure_ascii=False))
    return profile


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-plan', type=Path, required=True)
    parser.add_argument('--reference-reports', type=Path, required=True)
    parser.add_argument('--evaluate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    try:
        run(args.reference_plan, args.reference_reports, args.evaluate, args.out)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, f'Calibration failed: {exc}\n')
