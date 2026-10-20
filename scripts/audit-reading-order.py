"""Create a local, hash-bound reading-order inspection bundle; never reorder by geometry."""

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reversed_pairs(items, order_key):
    """Candidates only: spanning panels and deliberate eye paths need source review."""
    hits = []
    ordered = sorted(items, key=lambda item: item[order_key])
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            x, y = a['bbox'], b['bbox']
            vo = min(x['y'] + x['h'], y['y'] + y['h']) - max(x['y'], y['y'])
            ho = min(x['x'] + x['w'], y['x'] + y['w']) - max(x['x'], y['x'])
            kind = None
            if vo > min(x['h'], y['h']) * .6 and x['x'] + x['w'] <= y['x'] + .025:
                kind = 'left_before_right'
            if ho > min(x['w'], y['w']) * .6 and x['y'] >= y['y'] + y['h'] - .025:
                kind = 'bottom_before_top'
            if kind:
                hits.append({'first': a.get('id', a[order_key]),
                             'later': b.get('id', b[order_key]), 'kind': kind})
    return hits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    ledger, out = args.ledger.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / 'before').mkdir()
    (out / 'sheets').mkdir()
    font_path = '/System/Library/Fonts/Supplemental/Arial.ttf'
    font = ImageFont.truetype(font_path, 20)
    small = ImageFont.truetype(font_path, 16)
    records, grouped = [], {}
    for path in sorted((ledger / 'pages').rglob('*.json')):
        raw = path.read_bytes()
        d = json.loads(raw)
        source, e = d['source'], d['effectiveCandidateReading']
        actual_sha = sha(Path(source['path']))
        if actual_sha != source['sha256']:
            raise ValueError('Source SHA mismatch: ' + source['id'])
        backup = out / 'before' / path.relative_to(ledger)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(raw)
        flags = [{'scope': 'panels', **h} for h in reversed_pairs(e['panels'], 'readingOrder')]
        for panel in e['panels']:
            narrative = [t for t in panel['texts'] if t['kind'] in ('dialogue', 'thought', 'narration')]
            flags += [{'scope': panel['id'] + '/texts', **h} for h in reversed_pairs(narrative, 'order')]
        if re.search(r'左到右|左至右|从左往右|left.to.right', e['readingOrderExplanation']):
            flags.append({'scope': 'explanation', 'kind': 'ltr_wording'})
        if re.search(r'两种顺序|若.*右起|未强行确定先后', e['readingOrderExplanation']):
            flags.append({'scope': 'explanation', 'kind': 'direction_uncertainty'})
        panel_orders = [p['readingOrder'] for p in e['panels']]
        if sorted(panel_orders) != list(range(1, len(panel_orders) + 1)):
            flags.append({'scope': 'panels', 'kind': 'invalid_order_numbers'})
        placeholder_texts = sum(t['bbox'] == p['bbox'] for p in e['panels'] for t in p['texts'])
        rec = {'sourceId': source['id'], 'ledgerPath': str(path),
               'ledgerSha256Before': hashlib.sha256(raw).hexdigest(), 'source': source,
               'pageType': e['pageType'], 'spread': e['spread'],
               'spreadEvidence': e['spreadEvidence'], 'explanation': e['readingOrderExplanation'],
               'flags': flags, 'placeholderTextBoxes': placeholder_texts,
               'panelCount': len(e['panels']), 'panelOverviewReviewed': False,
               'dialogueVerbatimReviewed': False,
               'panels': [{k: p[k] for k in ('id', 'readingOrder', 'bbox', 'texts',
                                             'transitionFromPreviousPanel', 'visibleAction')}
                          for p in e['panels']]}
        records.append(rec)
        grouped.setdefault((source['work'], source['chapter']), []).append((rec, d))
    sheets = []
    for (work, chapter), pages in grouped.items():
        for start in range(0, len(pages), 6):
            batch = pages[start:start + 6]
            canvas = Image.new('RGB', (1560, 1536), '#e3e3e3')
            for idx, (rec, d) in enumerate(batch):
                col, row = idx % 3, idx // 3
                ox, oy = col * 520, row * 768
                im = Image.open(rec['source']['path']).convert('RGB')
                im.thumbnail((510, 720), Image.Resampling.LANCZOS)
                px, py = ox + (520 - im.width) // 2, oy + 36
                canvas.paste(im, (px, py))
                draw = ImageDraw.Draw(canvas)
                label = f'{work}/{chapter}/{Path(rec["sourceId"]).stem}'
                draw.text((ox + 8, oy + 5), label, font=font, fill='#b00000' if rec['flags'] else 'black')
                for p in d['effectiveCandidateReading']['panels']:
                    b = p['bbox']
                    x, y = px + b['x'] * im.width, py + b['y'] * im.height
                    draw.rectangle((x, y, x + b['w'] * im.width, y + b['h'] * im.height), outline='#d41400', width=2)
                    text = f'{p["readingOrder"]}:{p["id"]}'
                    draw.rectangle((x, y, x + 14 + 8 * len(text), y + 23), fill='#fff09b')
                    draw.text((x + 2, y + 1), text, font=small, fill='#a00000')
                rec['sheet'] = f'sheets/{work}-{chapter}-{start // 6 + 1:02}.jpg'
            dest = out / batch[0][0]['sheet']
            canvas.save(dest, quality=92)
            sheets.append({'path': str(dest), 'sha256': sha(dest), 'sourceIds': [r['sourceId'] for r, _ in batch]})
    inventory = {'schema': 1, 'policy': 'Japanese RTL; geometry flags require human source review; no automatic reorder',
                 'coverage': {'pages': len(records), 'panels': sum(r['panelCount'] for r in records),
                              'flags': dict(Counter(h['kind'] for r in records for h in r['flags'])),
                              'flaggedPages': sum(bool(r['flags']) for r in records)},
                 'pages': records, 'sheets': sheets}
    (out / 'inventory.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(inventory['coverage'], ensure_ascii=False))
    print(f'{len(sheets)} contact sheets; preserved {len(records)} original ledger files in {out / "before"}')


if __name__ == '__main__':
    main()
