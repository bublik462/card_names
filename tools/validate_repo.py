#!/usr/bin/env python3
# validate_repo.py — basic integrity checks for Testerius brand repository JSONs.
import json, re, sys, hashlib, pathlib, datetime

RE_QID = re.compile(r"^Q\d+$")
RE_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_ROOT_KEYS = {"schema", "updatedAt", "country", "items"}
REQUIRED_ITEM_KEYS = {"categoryPath", "brand", "brandKey", "brandWikidata", "aliases", "names"}

def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def die(msg: str, code: int = 2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def warn(msg: str):
    print(f"WARNING: {msg}", file=sys.stderr)

def main():
    repo = pathlib.Path(__file__).resolve().parents[1]
    index_path = repo / "index.json"
    if not index_path.exists():
        die("index.json not found. Expected repository root to contain index.json.")

    index = json.loads(index_path.read_text(encoding="utf-8"))
    if index.get("schema") != 1:
        die(f"index.schema must be 1, got {index.get('schema')!r}")
    if not isinstance(index.get("countries"), list) or not index["countries"]:
        die("index.countries must be a non-empty array")

    # Validate each country file referenced by index.json
    for c in index["countries"]:
        code = c.get("code")
        file_rel = c.get("file")
        expected_sha = c.get("sha256", "")
        expected_items = c.get("items")

        if not code or not file_rel:
            die(f"index.countries entry must contain code and file: {c}")

        file_path = (repo / file_rel).resolve()
        if not file_path.exists():
            die(f"Referenced file not found: {file_rel}")

        actual_sha = sha256_file(file_path)
        if expected_sha and actual_sha != expected_sha:
            die(f"SHA256 mismatch for {file_rel}: expected {expected_sha}, got {actual_sha}")

        data = json.loads(file_path.read_text(encoding="utf-8"))
        missing_root = REQUIRED_ROOT_KEYS - set(data.keys())
        if missing_root:
            die(f"{file_rel}: missing root keys: {sorted(missing_root)}")

        if data["schema"] != 1:
            die(f"{file_rel}: schema must be 1, got {data['schema']!r}")
        if data["country"] != code:
            die(f"{file_rel}: country must be {code}, got {data['country']!r}")

        updated_at = data["updatedAt"]
        if not isinstance(updated_at, str) or not RE_DATE.match(updated_at):
            die(f"{file_rel}: updatedAt must be YYYY-MM-DD, got {updated_at!r}")
        # Validate date is parseable
        try:
            datetime.date.fromisoformat(updated_at)
        except Exception:
            die(f"{file_rel}: updatedAt is not a valid ISO date: {updated_at!r}")

        items = data["items"]
        if not isinstance(items, list):
            die(f"{file_rel}: items must be array")
        if isinstance(expected_items, int) and len(items) != expected_items:
            warn(f"{file_rel}: items count differs from index: index={expected_items}, actual={len(items)}")

        brand_keys = set()
        for i, it in enumerate(items):
            if not isinstance(it, dict):
                die(f"{file_rel}: item #{i} is not an object")
            missing_item = REQUIRED_ITEM_KEYS - set(it.keys())
            if missing_item:
                die(f"{file_rel}: item #{i} missing keys: {sorted(missing_item)}")

            bk = it["brandKey"]
            if not isinstance(bk, str) or not bk:
                die(f"{file_rel}: item #{i} brandKey must be non-empty string")
            if bk in brand_keys:
                die(f"{file_rel}: duplicate brandKey {bk!r}")
            brand_keys.add(bk)

            bw = it["brandWikidata"]
            if bw and (not isinstance(bw, str) or not RE_QID.match(bw)):
                die(f"{file_rel}: item #{i} brandWikidata must be '' or Q123..., got {bw!r}")

            if not isinstance(it["aliases"], list) or not all(isinstance(x, str) for x in it["aliases"]):
                die(f"{file_rel}: item #{i} aliases must be array of strings")
            if not isinstance(it["names"], list) or not all(isinstance(x, str) for x in it["names"]):
                die(f"{file_rel}: item #{i} names must be array of strings")

        print(f"OK: {code} — {len(items)} items — sha256 {actual_sha}")

    print("All checks passed.")

if __name__ == "__main__":
    main()
