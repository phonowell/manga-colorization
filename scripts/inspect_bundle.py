"""Create an immutable local inspection bundle. Requires Python 3 and Pillow."""

import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


def prepare(plan_path):
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    items = plan.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("Plan requires a nonempty items array")
    prepared = []
    for index, item in enumerate(items):
        path = (plan_path.parent / item["path"]).resolve()
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if item.get("sha256") and item["sha256"] != digest:
            raise ValueError(f"Input {index}: SHA-256 differs from reviewed version")
        with Image.open(io.BytesIO(data)) as opened:
            opened.load()
            image = opened.convert("RGB")
        bounds = item.get("crop", [0, 0, image.width, image.height])
        if (
            not isinstance(bounds, list)
            or len(bounds) != 4
            or any(type(value) is not int for value in bounds)
        ):
            raise ValueError(f"Input {index}: crop requires four integer pixel coordinates")
        left, top, right, bottom = bounds
        if not (0 <= left < right <= image.width and 0 <= top < bottom <= image.height):
            raise ValueError(f"Input {index}: crop is outside image or empty")
        crop = image.crop(bounds)
        label = str(item.get("label", f"Stage {index + 1}"))
        stage = item.get("stage", label if label.isascii() else f"Stage {index + 1}")
        if not isinstance(stage, str) or not stage.strip() or not stage.isascii():
            raise ValueError(f"Input {index}: stage must be a nonempty ASCII caption; label may be multilingual")
        record = {
            "label": label,
            "displayStage": stage,
            "path": str(path),
            "sha256": digest,
            "dimensions": [image.width, image.height],
            "crop": bounds,
            "nativeCrop": f"{index + 1:02d}-native.png",
        }
        prepared.append((record, crop))
    return plan_bytes, plan, prepared


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    plan_path = args.plan.resolve()
    try:
        if args.out.exists():
            raise ValueError("Output directory already exists; refusing to overwrite evidence")
        plan_bytes, plan, prepared = prepare(plan_path)
        columns = min(3, len(prepared))
        rows = (len(prepared) + columns - 1) // columns
        sheet = Image.new("RGB", (columns * 520, rows * 430), "#eeeeee")
        draw = ImageDraw.Draw(sheet)
        for index, (record, crop) in enumerate(prepared):
            x, y = index % columns * 520, index // columns * 430
            thumb = ImageOps.contain(crop, (500, 360), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x + (520 - thumb.width) // 2, y + 60))
            # Portable stage captions distinguish original/raw/final without
            # requiring a platform font; full multilingual labels remain saved.
            draw.text((x + 10, y + 8), f"{index + 1:02d} {record['displayStage']}"[:76], fill="black")
            draw.text((x + 10, y + 26), f"native {crop.width}x{crop.height}  {record['sha256'][:24]}", fill="black")
        args.out.mkdir(parents=True, exist_ok=False)
        (args.out / "plan.json").write_bytes(plan_bytes)
        for record, crop in prepared:
            crop.save(args.out / record["nativeCrop"])
        sheet.save(args.out / "contact-sheet.png")
        manifest = {
            "purpose": plan.get("purpose", ""),
            "planPath": str(plan_path),
            "planSha256": hashlib.sha256(plan_bytes).hexdigest(),
            "items": [record for record, _ in prepared],
            "limits": "Hashes identify bytes; crops and contact sheets do not certify semantics or artistic quality.",
            "providerCalls": 0,
        }
        (args.out / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        )
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, f"Inspection failed: {error}\n")
    print(json.dumps({"bundle": str(args.out.resolve()), "items": len(prepared), "providerCalls": 0}))


if __name__ == "__main__":
    main()
