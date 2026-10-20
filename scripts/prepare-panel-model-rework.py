"""Pack source-bound complete monochrome panels; never paint or recolor objects."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def pointer(value, address):
    if address == '':
        return value
    if not address.startswith('/'):
        raise ValueError('Ledger pointer must be an RFC 6901 JSON pointer')
    for token in address[1:].split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def prepare(packet_path, out):
    packet_path, out = packet_path.resolve(), out.resolve()
    packet = json.loads(packet_path.read_bytes())
    dependencies = {}

    def lock(path, expected=None):
        path = (packet_path.parent / path).resolve()
        actual = sha(path)
        if expected is not None and expected != actual:
            raise ValueError('Dependency SHA differs: ' + str(path))
        dependencies[str(path)] = actual
        return path

    lock(packet_path)
    lock(__file__)
    if not isinstance(packet.get('slots'), list) or not packet['slots']:
        raise ValueError('At least one complete panel slot is required')
    registry = {s['id']: s for s in json.loads(lock(packet['sourceRegistry']).read_bytes())}
    feedback = json.loads(lock(packet['mergedFeedback']).read_bytes())['pages']
    canvas = Image.new('RGB', tuple(packet['canvas']), 'white')
    rectangles = []
    prompt = [packet['task']]
    for slot in packet['slots']:
        if slot['scope'] not in ('complete-panel', 'complete-panel-group') or not slot['boundaryReview']:
            raise ValueError('Complete panels and explicit boundary review required')
        source = registry[slot['sourceId']]
        original = Image.open(lock(source['path'], slot['originalSha256'])).convert('RGB')
        if source['sha256'] != slot['originalSha256']:
            raise ValueError('Registered original differs')
        # JPEG noise is allowed; an actual colored edit target is not.
        for a, b in ((0, 1), (1, 2)):
            if ImageChops.difference(original.getchannel(a), original.getchannel(b)).getextrema()[1] > 12:
                raise ValueError('Target is not monochrome original art')
        x0, y0, x1, y1 = slot['sourceBox']
        x, y = slot['destination']
        w, h = x1 - x0, y1 - y0
        if not (0 <= x0 < x1 <= original.width and 0 <= y0 < y1 <= original.height and
                0 <= x and 0 <= y and x + w <= canvas.width and y + h <= canvas.height):
            raise ValueError('Panel rectangle is out of bounds')
        rect = (x, y, x + w, y + h)
        if any(max(x, a) < min(x+w, c) and max(y, b) < min(y+h, d) for a,b,c,d in rectangles):
            raise ValueError('Montage panels overlap')
        rectangles.append(rect)
        panel = original.crop((x0, y0, x1, y1))
        canvas.paste(panel, (x, y))
        if ImageChops.difference(canvas.crop(rect), panel).getbbox():
            raise ValueError('Copied source pixels differ')
        annotations = feedback[str(int(source['page'].split('.')[0]))]['annotations']
        applicable = []
        for annotation in annotations:
            box = annotation['sourcePixels']
            if max(x0, box['x']) < min(x1, box['x']+box['width']) and max(y0, box['y']) < min(y1, box['y']+box['height']):
                applicable.append(annotation['id'])
        if set(slot['feedbackIds']) != set(applicable):
            raise ValueError('Panel feedback coverage differs')
        facts = []
        for fact in slot['facts']:
            value = pointer(json.loads(lock(fact['ledger']).read_bytes()), fact['pointer'])
            if not isinstance(value, list) or len(value) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in value):
                raise ValueError('Invalid RGB ledger entry: ' + fact['label'])
            facts.append(f"{fact['label']} RGB{tuple(value)}")
        if not facts or slot.get('unresolvedRequired'):
            raise ValueError('Missing facts or unresolved required semantics')
        prompt.append(slot['promptRole'] + '：' + '；'.join(facts) + '。' + slot['preservation'])
    if out.exists():
        raise ValueError('Refusing to overwrite request directory')
    out.mkdir(parents=True)
    canvas.save(out / 'target-prepared.png')
    (out / 'prompt.txt').write_text('\n'.join(prompt) + '\n')
    write(out / 'input.json', packet)
    plan = dict(source=dict(id=packet['batchId'], kind='original-panel-montage', slots=packet['slots']),
                model='gpt-image-2', timeoutMs=900000,
                canvas=dict(width=canvas.width, height=canvas.height),
                referenceMode='source-only', additionalReferences=[],
                targetPreparedSha256=sha(out / 'target-prepared.png'), promptSha256=sha(out / 'prompt.txt'))
    write(out / 'plan.json', plan)
    for name in ('target-prepared.png', 'prompt.txt', 'input.json', 'plan.json'):
        lock(out / name)
    write(out / 'request-readiness.json', dict(schema='manga-request-readiness-v1',
          sourceId=packet['batchId'], promptSha256=plan['promptSha256'],
          dependencies=[dict(path=p, sha256=s) for p,s in sorted(dependencies.items())],
          limits='Source and fact consistency only; complete panel semantics require visual review.', providerCalls=0))
    return plan


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.packet, args.out)
    print(json.dumps(dict(status='prepared', providerCalls=0)))
