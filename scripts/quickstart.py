"""Build a local review bundle from two images, or run a synthetic diagnostic demo.

This command never generates or colors artwork, calls a provider, or approves it.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys


def binding(path):
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(args):
    from PIL import Image, ImageDraw

    out = args.out.resolve()
    if out.exists():
        raise ValueError("Output already exists. Choose a new --out directory; evidence is never overwritten.")
    if args.demo:
        # Geometric test patterns only: this is an inspection fixture, not manga.
        source = Image.new("RGB", (320, 240), "white")
        draw = ImageDraw.Draw(source)
        draw.rectangle((24, 24, 295, 215), outline="black", width=2)
        draw.ellipse((60, 50, 135, 125), outline="black", width=2)
        draw.line((160, 60, 260, 150, 165, 185), fill="black", width=3)
        candidate = Image.new("RGB", source.size, "white")
        candidate.paste(source.crop((0, 0, 315, 240)), (5, 0))
        out.mkdir(parents=True, exist_ok=False)
        source_path, candidate_path = out / "synthetic-source.png", out / "synthetic-shifted.png"
        source.save(source_path)
        candidate.save(candidate_path)
    else:
        source_path, candidate_path = args.source.resolve(), args.candidate.resolve()
        sizes = []
        for path in (source_path, candidate_path):
            with Image.open(io.BytesIO(path.read_bytes())) as image:
                image.load()
                if image.getexif().get(274, 1) != 1:
                    raise ValueError("Resolve EXIF orientation explicitly before inspection.")
                if "A" in image.getbands() and image.getchannel("A").getextrema() != (255, 255):
                    raise ValueError("Transparent images require explicit interpretation; use opaque inputs.")
                sizes.append(image.size)
        if sizes[0] != sizes[1]:
            raise ValueError("Image dimensions differ. This quickstart never resizes or aligns; use the advanced padding plan.")
        out.mkdir(parents=True, exist_ok=False)

    source_binding, candidate_binding = binding(source_path), binding(candidate_path)
    write_json(out / "inspection-plan.json", {
        "purpose": "Synthetic drift diagnostic" if args.demo else "Source/candidate review; no automatic approval",
        "items": [
            {"label": "Original", **source_binding},
            {"label": "Synthetic shifted fixture" if args.demo else "Candidate", **candidate_binding},
        ],
    })
    write_json(out / "fidelity-plan.json", {
        "schema": 1,
        "cases": [{"id": "comparison", "source": source_binding, "candidate": candidate_binding,
                   "padding": [0, 0, 0, 0]}],
    })
    scripts = Path(__file__).resolve().parent
    for script, plan, destination in (
        ("inspect_bundle.py", "inspection-plan.json", "inspection"),
        ("check-source-fidelity.py", "fidelity-plan.json", "fidelity"),
    ):
        subprocess.run([sys.executable, str(scripts / script), "--plan", str(out / plan),
                        "--out", str(out / destination)], check=True)
    for path, original_binding in ((source_path, source_binding), (candidate_path, candidate_binding)):
        if binding(path) != original_binding:
            raise ValueError("An input changed during inspection; this bundle is invalid.")
    summary = {"demo": args.demo, "providerCalls": 0, "artworkGenerated": False,
               "userApproved": False, "source": source_binding, "candidate": candidate_binding,
               "contactSheet": "inspection/contact-sheet.png",
               "diagnostics": "fidelity/comparison/report.json",
               "nextStep": "Open the native comparisons and review content, color, continuity, and user feedback separately."}
    write_json(out / "quickstart.json", summary)
    print(f"Review bundle: {out}\nOpen: {out / 'inspection/contact-sheet.png'}")
    print("Diagnostics are unverified evidence, not artwork approval. Provider calls: 0.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Use synthetic geometric test patterns; no manga or coloring")
    parser.add_argument("--source", type=Path, help="Monochrome original image")
    parser.add_argument("--candidate", type=Path, help="Already generated candidate with the same dimensions")
    parser.add_argument("--out", type=Path, required=True, help="New output directory; never overwrites")
    args = parser.parse_args()
    if args.demo and (args.source or args.candidate):
        parser.error("--demo cannot be combined with --source or --candidate")
    if not args.demo and not (args.source and args.candidate):
        parser.error("Provide both --source and --candidate, or choose --demo")
    try:
        run(args)
    except ImportError as error:
        parser.exit(2, f"Missing dependency: {error}. Install with: python -m pip install -r requirements.txt\n")
    except subprocess.CalledProcessError:
        parser.exit(2, "A review helper failed. Keep partial evidence and retry with a new output directory after resolving the error.\n")
    except (ValueError, OSError) as error:
        parser.exit(2, f"Quickstart failed: {error}\n")


if __name__ == "__main__":
    main()
