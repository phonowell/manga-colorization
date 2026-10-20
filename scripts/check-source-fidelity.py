"""Read-only original-coordinate diagnostics; never edits or approves artwork.

Usage: .venv/bin/python scripts/check-source-fidelity.py --plan PLAN --out NEW_DIR
Requires the existing NumPy, OpenCV and Pillow environment. No model/network calls.
"""

import argparse
import hashlib
import io
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

VERSION = 'source-fidelity-diagnostics-v1'
MODES = [('fine', 0.6, 45, 100), ('sensitive', 0.6, 20, 50), ('coarse', 1.2, 30, 75)]
TILE_SIZE = 64


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_binding(binding, base):
    path = (base / binding['path']).resolve()
    raw = path.read_bytes()
    if sha(raw) != binding['sha256']:
        raise ValueError(f'SHA mismatch: {path}')
    return path, raw


def decode(raw):
    with Image.open(io.BytesIO(raw)) as image:
        if image.getexif().get(274, 1) != 1:
            raise ValueError('EXIF orientation must be resolved explicitly, not auto-applied')
        if 'A' in image.getbands() and image.getchannel('A').getextrema() != (255, 255):
            raise ValueError('Transparent images need an explicit interpretation')
        return np.array(image.convert('RGB'))


def prepare_case(case, base):
    paths = {}
    arrays = {}
    for role in ('source', 'candidate'):
        path, raw = load_binding(case[role], base)
        paths[role] = {'path': str(path), 'sha256': sha(raw)}
        arrays[role] = decode(raw)
    source, candidate = arrays['source'], arrays['candidate']
    height, width = source.shape[:2]
    padding = case.get('padding', [0, 0, 0, 0])
    if len(padding) != 4 or any(type(x) is not int or x < 0 for x in padding):
        raise ValueError('Padding must be nonnegative integers: left, top, right, bottom')
    left, top, right, bottom = padding
    preparation = case.get('preparation')
    if any(padding) and not preparation:
        raise ValueError('Nonzero padding requires original preparation evidence')
    if preparation:
        for role in ('image', 'metadata'):
            path, raw = load_binding(preparation[role], base)
            paths['preparation_' + role] = {'path': str(path), 'sha256': sha(raw)}
            if role == 'image':
                prepared = decode(raw)
            else:
                metadata = json.loads(raw)
        expected_padding = dict(zip(('left', 'top', 'right', 'bottom'), padding))
        if metadata.get('originalSha256') != paths['source']['sha256']:
            raise ValueError('Preparation does not bind this original')
        if metadata.get('padding') != expected_padding:
            raise ValueError('Padding differs from preparation evidence')
        if metadata.get('scaledContent') != {'width': width, 'height': height}:
            raise ValueError('Prepared content size differs from original')
        if prepared.shape[:2] != (height + top + bottom, width + left + right):
            raise ValueError('Prepared canvas differs from declared padding')
        if not np.array_equal(source, prepared[top:top + height, left:left + width]):
            raise ValueError('Prepared content pixels differ from original')
    expected = (height + top + bottom, width + left + right)
    geometry_ok = candidate.shape[:2] == expected
    regions = case.get('criticalRegions', [])
    for region in regions:
        box = region['box']
        if (len(box) != 4 or any(type(x) is not int for x in box)
                or not (0 <= box[0] < box[2] <= width and 0 <= box[1] < box[3] <= height)):
            raise ValueError('Critical locator must be an in-bounds original-pixel box')
    binding = {
        'id': case['id'], 'files': paths, 'sourceSize': [width, height],
        'candidateSize': [candidate.shape[1], candidate.shape[0]],
        'paddingLTRB': padding, 'geometryMatchesDeclaration': geometry_ok,
        'preparedContentPixelsEqual': True if preparation else None,
        'sourceContentBoxInCandidate': [left, top, left + width, top + height],
        'historicalLabel': case.get('historicalLabel', 'unknown'),
    }
    return binding, source, candidate[top:top + height, left:left + width] if geometry_ok else None


def features(rgb, sigma, low, high):
    # Contrast edges are proxies, not a semantic separation of ink and pigment.
    light = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[:, :, 0]
    smooth = cv2.GaussianBlur(light, (0, 0), sigma)
    edges = cv2.Canny(smooth, low, high, L2gradient=True) != 0
    gx = cv2.Sobel(smooth, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(smooth, cv2.CV_32F, 0, 1, ksize=3)
    return edges, np.arctan2(gy, gx)


def edge_distances(query, target):
    if not target.any():
        return np.full(query.shape, np.inf, dtype=np.float32)
    return cv2.distanceTransform((~target).astype(np.uint8), cv2.DIST_L2, cv2.DIST_MASK_PRECISE)


def distance_stats(mask, distances):
    values = distances[mask]
    count = int(values.size)
    if not count:
        return {'edgePixels': 0, 'coverage': 'no_query_edges', 'withinPixels': None,
                'quantilesPixels': None}
    finite = values[np.isfinite(values)]
    return {
        'edgePixels': count, 'unboundedDistancePixels': int(count - finite.size),
        'withinPixels': {str(r): int(np.count_nonzero(values <= r)) for r in (0, 1, 2, 4, 8)},
        'beyond2Fraction': float(np.count_nonzero(values > 2) / count),
        'quantilesPixels': {str(q): float(np.quantile(finite, q)) if finite.size else None
                            for q in (0.5, 0.9, 0.95, 0.99)},
    }


def oriented_unmatched(query, target, query_angle, target_angle, radius=2):
    """No image transform: test local edge support with compatible orientation."""
    ys, xs = np.nonzero(query)
    unmatched = np.ones(ys.size, dtype=bool)
    angles = query_angle[ys, xs]
    height, width = query.shape
    offsets = [(dx, dy) for dy in range(-radius, radius + 1)
               for dx in range(-radius, radius + 1) if dx * dx + dy * dy <= radius * radius]
    for dx, dy in offsets:
        tx, ty = xs + dx, ys + dy
        valid = (tx >= 0) & (tx < width) & (ty >= 0) & (ty < height) & unmatched
        at = np.flatnonzero(valid)
        tx, ty = tx[at], ty[at]
        # Absolute cosine identifies orientation modulo pi, not gradient sign.
        compatible = np.abs(np.cos(angles[at] - target_angle[ty, tx])) >= math.cos(math.pi / 6)
        unmatched[at[target[ty, tx] & compatible]] = False
    result = np.zeros(query.shape, dtype=bool)
    result[ys[unmatched], xs[unmatched]] = True
    return result


def mode_analysis(source, candidate, mode):
    name, sigma, low, high = mode
    se, sa = features(source, sigma, low, high)
    ce, ca = features(candidate, sigma, low, high)
    sd, cd = edge_distances(se, ce), edge_distances(ce, se)
    sm, cm = se & (sd > 2), ce & (cd > 2)
    so = oriented_unmatched(se, ce, sa, ca)
    co = oriented_unmatched(ce, se, ca, sa)
    stats = {
        'name': name, 'sigma': sigma, 'cannyThresholds': [low, high],
        'sourceToCandidate': distance_stats(se, sd),
        'candidateToSource': distance_stats(ce, cd),
        'sourceOrientationUnmatchedWithin2': int(so.sum()),
        'candidateOrientationUnmatchedWithin2': int(co.sum()),
        'orientationToleranceDegrees': 30,
    }
    return stats, {'sourceEdges': se, 'candidateEdges': ce, 'missingProxy': sm,
                   'addedProxy': cm, 'sourceOrientationMismatch': so,
                   'candidateOrientationMismatch': co, 'sourceDistances': sd, 'candidateDistances': cd}


def window_stats(maps, box):
    x0, y0, x1, y1 = box
    view = {k: v[y0:y1, x0:x1] for k, v in maps.items()}
    source_n, candidate_n = int(view['sourceEdges'].sum()), int(view['candidateEdges'].sum())
    missing, added = int(view['missingProxy'].sum()), int(view['addedProxy'].sum())
    return {
        'box': box, 'sourceEdgePixels': source_n, 'candidateEdgePixels': candidate_n,
        'missingProxyPixelsBeyond2': missing, 'addedProxyPixelsBeyond2': added,
        'sourceExactUnmatchedPixels': int((view['sourceEdges'] & (view['sourceDistances'] > 0)).sum()),
        'candidateExactUnmatchedPixels': int((view['candidateEdges'] & (view['candidateDistances'] > 0)).sum()),
        'sourceUnmatchedBeyond1': int((view['sourceEdges'] & (view['sourceDistances'] > 1)).sum()),
        'candidateUnmatchedBeyond1': int((view['candidateEdges'] & (view['candidateDistances'] > 1)).sum()),
        'sourceOrientationUnmatchedWithin2': int(view['sourceOrientationMismatch'].sum()),
        'candidateOrientationUnmatchedWithin2': int(view['candidateOrientationMismatch'].sum()),
        'missingProxyFraction': missing / source_n if source_n else None,
        'addedProxyFraction': added / candidate_n if candidate_n else None,
        'rankingOnlyMismatchCount': missing + added,
    }


def diagnostic_map(maps):
    height, width = maps['sourceEdges'].shape
    result = np.full((height, width, 3), 255, dtype=np.uint8)
    result[maps['sourceEdges'] | maps['candidateEdges']] = [155, 155, 155]
    # Expose even one-pixel disagreements; the distance2 band is not an exemption.
    result[maps['sourceEdges'] & ~maps['candidateEdges']] = [244, 160, 175]
    result[maps['candidateEdges'] & ~maps['sourceEdges']] = [135, 192, 245]
    result[maps['sourceOrientationMismatch'] | maps['candidateOrientationMismatch']] = [198, 142, 0]
    result[maps['missingProxy']] = [220, 30, 65]
    result[maps['addedProxy']] = [0, 115, 220]
    return result


def inspection_strip(source, candidate, diagnostic, box, title):
    x0, y0, x1, y1 = box
    width, height = x1 - x0, y1 - y0
    sheet = Image.new('RGB', (width * 3, height + 64), '#eeeeee')
    draw = ImageDraw.Draw(sheet)
    draw.text((8, 5), 'INSPECTION ONLY - NOT ARTWORK / ' + title, fill='black')
    for i, (label, rgb) in enumerate([('Original', source), ('Raw candidate', candidate), ('Edge proxies', diagnostic)]):
        draw.text((i * width + 8, 28), label, fill='black')
        sheet.paste(Image.fromarray(rgb[y0:y1, x0:x1]), (i * width, 64))
    return sheet


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def analyze_case(case, base, out):
    binding, source, candidate = prepare_case(case, base)
    report = {**binding, 'automaticDecision': 'unverified', 'eligibleForPublication': False,
              'humanDecision': None, 'semanticClassificationPerformed': False,
              'criticalCoverageComplete': False, 'registrationApplied': False,
              'limitations': ['Contrast edges can be ink, hatching, tone or pigment boundaries.',
                             'Diagnostic distances and orientation support do not certify stroke identity.',
                             'Critical locators are partial original-coordinate inspection windows, not migrated feedback.',
                             'No automatic quality pass threshold is calibrated.']}
    out.mkdir()
    if candidate is None:
        report['automaticDecision'] = 'reject_geometry'
        write_json(out / 'report.json', report)
        return report
    height, width = source.shape[:2]
    modes = []
    critical = [{**r, 'modes': {}} for r in case.get('criticalRegions', [])]
    for mode in MODES:
        stats, maps = mode_analysis(source, candidate, mode)
        tiles = [window_stats(maps, [x, y, min(x + TILE_SIZE, width), min(y + TILE_SIZE, height)])
                 for y in range(0, height, TILE_SIZE) for x in range(0, width, TILE_SIZE)]
        stats['tileCount'] = len(tiles)
        stats['worstTilesByCount'] = sorted(tiles, key=lambda t: t['rankingOnlyMismatchCount'], reverse=True)[:20]
        # Fraction ranking also exposes tiny, locally complete losses.
        stats['worstTilesByFraction'] = sorted(
            (t for t in tiles if t['rankingOnlyMismatchCount']),
            key=lambda t: max(t['missingProxyFraction'] or 0, t['addedProxyFraction'] or 0), reverse=True)[:20]
        write_json(out / (mode[0] + '-all-tiles.json'), tiles)
        for r in critical:
            r['modes'][mode[0]] = window_stats(maps, r['box'])
        if mode[0] == 'fine':
            diagnostic = diagnostic_map(maps)
            full = inspection_strip(source, candidate, diagnostic, [0, 0, width, height], 'FULL PAGE / gray=exact overlap; pink/blue=disagreement; strong=>2px; gold=orientation')
            full.thumbnail((1800, 1300))
            full.save(out / 'overview-inspection.png')
            diag = inspection_strip(diagnostic, diagnostic, diagnostic, [0, 0, width, height], 'DIAGNOSTIC MAP')
            # Only one map column; keep the inspection header on this full-resolution evidence.
            diag.crop((0, 0, width, height + 64)).save(out / 'edge-proxies-inspection.png')
            locators = [(r['id'], r['box']) for r in critical]
            for i, t in enumerate(stats['worstTilesByCount'][:6]):
                x0, y0, x1, y1 = t['box']
                locators.append((f'worst-count-{i + 1}', [max(0, x0 - 48), max(0, y0 - 48), min(width, x1 + 48), min(height, y1 + 48)]))
            for i, (label, box) in enumerate(locators):
                filename = f'native-inspection-{i + 1:02d}.png'
                inspection_strip(source, candidate, diagnostic, box, label).save(out / filename)
                if i < len(critical):
                    critical[i]['nativeInspection'] = filename
            # Merge nearby suspicious pixels for locators, never for editing artwork.
            suspect = maps['missingProxy'] | maps['addedProxy']
            joined = cv2.dilate(suspect.astype(np.uint8), np.ones((5, 5), np.uint8))
            count, labels, components, _ = cv2.connectedComponentsWithStats(joined, 8)
            pixels = np.bincount(labels[suspect], minlength=count)
            regions = []
            for i in np.argsort(pixels[1:])[::-1][:30] + 1:
                x, y, w, h, _ = components[i]
                regions.append({'box': [int(x), int(y), int(x + w), int(y + h)], 'mismatchProxyPixels': int(pixels[i])})
            report['connectedMismatchLocators'] = regions
        modes.append(stats)
    report.update({'modes': modes, 'criticalRegions': critical, 'tileSize': TILE_SIZE,
                   'pixelCoverage': width * height, 'allPixelsCoveredByTiles': True,
                   'decodedRgbEqualFractionDiagnosticOnly': float(np.mean(np.all(source == candidate, axis=2)))})
    write_json(out / 'report.json', report)
    return report


def run(plan_path, out):
    plan_path, out = Path(plan_path).resolve(), Path(out).resolve()
    if out.exists():
        raise ValueError('Output must be a new directory')
    plan_raw = plan_path.read_bytes()
    plan = json.loads(plan_raw)
    if plan.get('schema') != 1 or not plan.get('cases'):
        raise ValueError('Expected schema1 and nonempty cases')
    identifiers = [c['id'] for c in plan['cases']]
    if len(set(identifiers)) != len(identifiers) or any(
            not i or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in i)
            for i in identifiers):
        raise ValueError('Case IDs must be unique safe directory names')
    # Validate every binding before any report directory is created.
    for case in plan['cases']:
        prepare_case(case, plan_path.parent)
    out.mkdir(parents=True)
    (out / 'plan.json').write_bytes(plan_raw)
    reports = []
    for case in plan['cases']:
        report = analyze_case(case, plan_path.parent, out / case['id'])
        reports.append({k: report[k] for k in ['id', 'files', 'historicalLabel', 'automaticDecision', 'eligibleForPublication']})
        print(json.dumps({'id': case['id'], 'status': report['automaticDecision']}, ensure_ascii=False), flush=True)
    # A second hash check detects a concurrent source/candidate/evidence write.
    for report in reports:
        for binding in report['files'].values():
            if sha(Path(binding['path']).read_bytes()) != binding['sha256']:
                raise ValueError('Input changed during inspection; this run is invalid')
    summary = {
        'version': VERSION, 'scriptSha256': sha(Path(__file__).read_bytes()),
        'planPath': str(plan_path), 'planSha256': sha(plan_raw),
        'dependencies': {'opencv': cv2.__version__, 'numpy': np.__version__},
        'cases': reports, 'providerCalls': 0, 'inputFilesUnchanged': True,
        'automaticQualityPassSupported': False, 'numericPassThresholdCalibrated': False,
    }
    write_json(out / 'summary.json', summary)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        cv2.setNumThreads(2)
        run(args.plan, args.out)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, f'Inspection failed: {exc}\n')
