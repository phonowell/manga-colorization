"""Compile ledger-selected coloring inputs; prepare or verify, never call a provider."""

import argparse
import copy
import hashlib
import json
from io import BytesIO
from pathlib import Path

from PIL import Image


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pointer(value, address):
    if address == "":
        return value
    if not address.startswith("/"):
        raise ValueError("Ledger pointer must be an RFC 6901 JSON pointer")
    for token in address[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def prepare(packet_path, out):
    packet = json.loads(packet_path.read_bytes())
    dependencies = {}

    def locked(path, expected=None):
        path = (packet_path.parent / path).resolve()
        data = path.read_bytes()
        if expected and digest(data) != expected:
            raise ValueError(f"Artifact differs from its recorded version: {path.name}")
        dependencies[str(path)] = digest(data)
        return data

    locked(packet_path)
    locked(Path(__file__).resolve())
    prepared = (packet_path.parent / packet["preparedDirectory"]).resolve()
    plan = json.loads(locked(prepared / "plan.json"))
    inp = json.loads(locked(prepared / "input.json"))
    source_bytes = locked(plan["source"]["path"], plan["source"]["sha256"])
    locked(inp["originalPath"], inp["originalSha256"])
    if (packet_path.parent / inp["originalPath"]).resolve() != (packet_path.parent / plan["source"]["path"]).resolve() or inp["originalSha256"] != plan["source"]["sha256"]:
        raise ValueError("The structural target must bind the original source, never a colored candidate")
    source_id = plan["source"]["id"]
    prefix, page = source_id.rsplit("/", 1)
    previous_id = f"{prefix}/{int(Path(page).stem) - 1:04d}{Path(page).suffix}"
    refs = plan["additionalReferences"]
    reference_mode = packet.get("referenceMode", "previous-page")
    if reference_mode not in ("previous-page", "source-only") or plan.get("referenceMode", "previous-page") != reference_mode:
        raise ValueError("Unknown or inconsistent reference mode")
    source_only = reference_mode == "source-only"
    if source_only and (refs or plan.get("referencePreparedSha256") or not packet.get("coverageNotes", "").strip()):
        raise ValueError("Source-only requests require no reference images and explicit palette coverage notes")
    previous = [r for r in refs if r["file"] == "previous-page.png"]
    if not source_only and (len(previous) != 1 or previous[0]["sourceId"] != previous_id):
        raise ValueError("Actual immediately previous page binding is missing or wrong")
    if not source_only:
        previous = previous[0]
        locked(previous["usedPath"], previous["usedFileSha256"])
    if packet.get("currentImagesPath"):
        current = json.loads(locked(packet["currentImagesPath"]))
        matches = [e for e in current["entries"] + current.get("retainedSelections", []) if e["sourceId"] == previous_id]
        if not source_only and len(matches) != 1:
            raise ValueError("Exactly one explicit current version is required for previous page")
        if not source_only and (Path(matches[0]["path"]).resolve() != Path(previous["usedPath"]).resolve() or matches[0].get("sha256") != previous["usedFileSha256"]):
            raise ValueError("Prepared reference is older than current previous page")
    if packet.get("mergedFeedback"):
        feedback = packet["mergedFeedback"]
        locked(feedback["path"], feedback["sha256"])

    ledgers = {}
    phrases = []
    selections = packet["selections"]
    ids = [fact["id"] for fact in selections]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate selected fact ID")
    missing = set(packet["requiredFactIds"]) - set(ids)
    if missing:
        raise ValueError("Required ledger facts omitted: " + ", ".join(sorted(missing)))
    if set(packet.get("unresolvedRequired", [])):
        raise ValueError("Required region interpretation is unresolved")
    for fact in selections:
        ledger_path = str((packet_path.parent / fact["ledger"]).resolve())
        if ledger_path not in ledgers:
            ledgers[ledger_path] = json.loads(locked(ledger_path))
        value = pointer(ledgers[ledger_path], fact["pointer"])
        if fact["kind"] == "palette":
            if not isinstance(value, list) or len(value) != 3 or any(type(v) is not int or not 0 <= v <= 255 for v in value):
                raise ValueError(f"Invalid RGB ledger entry: {fact['id']}")
            phrases.append(f"{fact['label']} RGB({value[0]},{value[1]},{value[2]})。")
        elif fact["kind"] == "region":
            if value.get("status") not in ("verified", "user-confirmed"):
                raise ValueError(f"Region is not verified or has been withdrawn: {fact['id']}")
            if not isinstance(value.get("note"), str) or not value["note"].strip():
                raise ValueError(f"Region has no verified instruction: {fact['id']}")
            phrases.append(value["note"].strip())
        else:
            raise ValueError("Unknown ledger selection kind")

    roles = ["只为 Image 1 上色，保留原画线形、分格、构图、姿态、表情和眼睛状态。"]
    if not source_only:
        roles.append("Image 2 提供原作色彩和纸质笔触参考。")
    for index, ref in enumerate(refs, 3):
        role = "紧邻上一页的连续性参考" if ref["file"] == "previous-page.png" else ref["role"]
        roles.append(f"Image {index} 是{role}。")
    prompt = "".join(roles) + packet["style"].strip() + "".join(phrases) + "\n"
    payload = {"input.json": locked(prepared / "input.json"), "prompt.txt": prompt.encode()}
    files = [("target-prepared.png", plan["targetPreparedSha256"])]
    if not source_only:
        files.append(("reference-collage.png", plan["referencePreparedSha256"]))
    files.extend((ref["file"], ref["preparedSha256"]) for ref in refs)
    for name, expected in files:
        if Path(name).name != name or name in (".", ".."):
            raise ValueError("Prepared artifact names must be plain filenames")
        payload[name] = locked(prepared / name, expected)
    with Image.open(prepared / "target-prepared.png") as image:
        content = inp["scaledContent"]
        pad = inp["padding"]
        if image.size != (plan["canvas"]["width"], plan["canvas"]["height"]) or image.size != (content["width"] + pad["left"] + pad["right"], content["height"] + pad["top"] + pad["bottom"]):
            raise ValueError("Prepared target dimensions disagree with its transform")
        if any(type(v) is not int or v < 0 for v in pad.values()):
            raise ValueError("Padding must contain nonnegative integers")
        with Image.open(BytesIO(source_bytes)) as source:
            source = source.convert("RGB")
            if source.size != (content["width"], content["height"]):
                raise ValueError("Prepared target must preserve original dimensions without rescaling")
            box = (pad["left"], pad["top"], pad["left"] + source.width, pad["top"] + source.height)
            if image.convert("RGB").crop(box).tobytes() != source.tobytes():
                raise ValueError("Prepared target changed original content pixels")
    plan = copy.deepcopy(plan)
    plan.pop("authorization", None)
    plan["referenceMode"] = reference_mode
    plan["status"] = "prepared inputs; not generated or reviewed"
    plan["promptSha256"] = digest(payload["prompt.txt"])
    payload["plan.json"] = (json.dumps(plan, ensure_ascii=False, indent=2) + "\n").encode()
    for name, data in payload.items():
        dependencies[str((out / name).resolve())] = digest(data)
    readiness = {
        "schema": "manga-request-readiness-v1",
        "sourceId": source_id,
        "promptSha256": plan["promptSha256"],
        "selectedFactIds": ids,
        "dependencies": [{"path": path, "sha256": sha} for path, sha in sorted(dependencies.items())],
        "limits": "Input consistency only. Declared fact coverage and source semantics still require human/host visual review; not artistic approval or permission to call a provider.",
        "providerCalls": 0,
    }
    out.mkdir(parents=True, exist_ok=False)
    for name, data in payload.items():
        (out / name).write_bytes(data)
    (out / "request-readiness.json").write_text(json.dumps(readiness, ensure_ascii=False, indent=2) + "\n")
    return readiness


def verify(root):
    readiness = json.loads((root / "request-readiness.json").read_bytes())
    plan = json.loads((root / "plan.json").read_bytes())
    if readiness["schema"] != "manga-request-readiness-v1" or readiness["sourceId"] != plan["source"]["id"] or readiness["promptSha256"] != plan["promptSha256"]:
        raise ValueError("Readiness does not bind this plan")
    if not isinstance(readiness.get("dependencies"), list) or not readiness["dependencies"]:
        raise ValueError("Readiness has no locked dependencies; rebuild it")
    for entry in readiness["dependencies"]:
        if digest(Path(entry["path"]).read_bytes()) != entry["sha256"]:
            raise ValueError("Prepared inputs or live ledger changed; rebuild readiness")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--packet", type=Path, required=True)
    prep.add_argument("--out", type=Path, required=True)
    check = sub.add_parser("verify")
    check.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            if args.out.exists():
                raise ValueError("Refusing to overwrite an existing request directory")
            ready = prepare(args.packet.resolve(), args.out.resolve())
            result = {"status": "prepared", "sourceId": ready["sourceId"], "selectedFactIds": ready["selectedFactIds"]}
        else:
            verify(args.root.resolve())
            result = {"status": "verified"}
    except (ValueError, OSError, KeyError, TypeError, AttributeError, IndexError) as error:
        parser.exit(2, f"Input preparation refused: {error}\n")
    print(json.dumps(dict(result, providerCalls=0), ensure_ascii=False))


if __name__ == "__main__":
    main()
