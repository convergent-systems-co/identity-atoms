#!/usr/bin/env python3
"""Validate every atoms/<type>/*.json and identities/<id>/definition.json.

Per-atom checks:
  1. JSON Schema validation against schemas/atom-v1.json
  2. `id` matches filename stem
  3. `type` matches parent directory name

Per-composition checks:
  1. JSON Schema validation against the schema declared in the file's `schema` field
     (composition-v1 or federated-composition-v1)
  2. `id` matches the parent directory name
  3. Every `ref` resolves to a known atom or composition under atoms/ or identities/

Per-rule check (smoke):
  - Every file under rules/*.py imports without exception

Exit 0 on full pass; exit 1 on any failure.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("error: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO / "schemas"
ATOMS_DIR = REPO / "atoms"
IDENTITIES_DIR = REPO / "identities"
RULES_DIR = REPO / "rules"

ATOM_SCHEMA_URL = "https://identity-atoms.com/schemas/atom-v1.json"
COMPOSITION_SCHEMA_URL = "https://identity-atoms.com/schemas/composition-v1.json"
FEDERATED_COMPOSITION_SCHEMA_URL = "https://identity-atoms.com/schemas/federated-composition-v1.json"

SCHEMA_BY_URL = {
    ATOM_SCHEMA_URL: SCHEMAS_DIR / "atom-v1.json",
    COMPOSITION_SCHEMA_URL: SCHEMAS_DIR / "composition-v1.json",
    FEDERATED_COMPOSITION_SCHEMA_URL: SCHEMAS_DIR / "federated-composition-v1.json",
}


def _load_validators() -> dict[str, jsonschema.Draft202012Validator]:
    validators: dict[str, jsonschema.Draft202012Validator] = {}
    for url, path in SCHEMA_BY_URL.items():
        if not path.exists():
            continue
        schema = json.loads(path.read_text(encoding="utf-8"))
        validators[url] = jsonschema.Draft202012Validator(schema)
    return validators


def _collect_atom_ids() -> set[str]:
    """Return the set of refs (e.g. 'auth-method/oidc') currently present under atoms/."""
    out: set[str] = set()
    if not ATOMS_DIR.exists():
        return out
    for path in ATOMS_DIR.rglob("*.json"):
        type_dir = path.parent.name
        atom_id = path.stem
        out.add(f"{type_dir}/{atom_id}")
    return out


def _collect_composition_ids() -> set[str]:
    """Return the set of refs (e.g. 'identities/aish-work-persona') currently present."""
    out: set[str] = set()
    if not IDENTITIES_DIR.exists():
        return out
    for path in IDENTITIES_DIR.glob("*/definition.json"):
        out.add(f"identities/{path.parent.name}")
    return out


def _validate_atom(path: Path, validators: dict[str, jsonschema.Draft202012Validator]) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON ({exc})"]
    schema_url = data.get("schema")
    if schema_url != ATOM_SCHEMA_URL:
        errors.append(f"schema={schema_url!r} (atoms must use {ATOM_SCHEMA_URL!r})")
        return errors
    validator = validators.get(ATOM_SCHEMA_URL)
    if validator is None:
        return [f"no validator loaded for {ATOM_SCHEMA_URL}"]
    for err in validator.iter_errors(data):
        loc = "/".join(str(x) for x in err.absolute_path) or "<root>"
        errors.append(f"schema: {err.message} at {loc}")
    stem = path.stem
    if data.get("id") != stem:
        errors.append(f"id={data.get('id')!r} does not match filename stem {stem!r}")
    parent = path.parent.name
    if data.get("type") != parent:
        errors.append(f"type={data.get('type')!r} does not match parent dir {parent!r}")
    return errors


def _validate_composition(
    path: Path,
    validators: dict[str, jsonschema.Draft202012Validator],
    known_atoms: set[str],
    known_compositions: set[str],
) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid JSON ({exc})"]
    schema_url = data.get("schema")
    if schema_url not in (COMPOSITION_SCHEMA_URL, FEDERATED_COMPOSITION_SCHEMA_URL):
        errors.append(
            f"schema={schema_url!r} (compositions must use composition-v1 or federated-composition-v1)"
        )
        return errors
    validator = validators.get(schema_url)
    if validator is None:
        return [f"no validator loaded for {schema_url}"]
    for err in validator.iter_errors(data):
        loc = "/".join(str(x) for x in err.absolute_path) or "<root>"
        errors.append(f"schema: {err.message} at {loc}")
    composition_dirname = path.parent.name
    if data.get("id") != composition_dirname:
        errors.append(
            f"id={data.get('id')!r} does not match parent dir name {composition_dirname!r}"
        )
    # Ref resolution
    for ref in _iter_refs(data):
        if ref.startswith("identities/"):
            if ref not in known_compositions:
                errors.append(f"unresolved composition ref: {ref}")
        else:
            if ref not in known_atoms:
                errors.append(f"unresolved atom ref: {ref}")
    return errors


def _iter_refs(data: object):
    """Yield every string under a key named 'ref' (or each element of 'via' arrays)."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "ref" and isinstance(value, str):
                yield value
            elif key == "composition_ref" and isinstance(value, str):
                yield value
            elif key == "via" and isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        yield item
            else:
                yield from _iter_refs(value)
    elif isinstance(data, list):
        for item in data:
            yield from _iter_refs(item)


def _smoke_import_rules() -> list[str]:
    errors: list[str] = []
    if not RULES_DIR.exists():
        return errors
    for path in RULES_DIR.glob("*.py"):
        if path.name.startswith("_"):
            continue
        module_name = f"identity_atoms_rules_{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            errors.append(f"{path.relative_to(REPO)}: could not load spec")
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001 — smoke-test surface
            errors.append(f"{path.relative_to(REPO)}: import failed ({exc!r})")
    return errors


def main() -> int:
    validators = _load_validators()
    if ATOM_SCHEMA_URL not in validators:
        print(f"error: missing schema at {SCHEMA_BY_URL[ATOM_SCHEMA_URL]}", file=sys.stderr)
        return 2

    known_atoms = _collect_atom_ids()
    known_compositions = _collect_composition_ids()

    total_errors = 0
    total_files = 0

    # Atoms
    atom_files = sorted(ATOMS_DIR.rglob("*.json")) if ATOMS_DIR.exists() else []
    for path in atom_files:
        rel = path.relative_to(REPO)
        errs = _validate_atom(path, validators)
        total_files += 1
        if errs:
            print(f"x {rel}")
            for err in errs:
                print(f"    {err}")
            total_errors += len(errs)
        else:
            print(f"ok {rel}")

    # Compositions
    composition_files = (
        sorted(IDENTITIES_DIR.glob("*/definition.json")) if IDENTITIES_DIR.exists() else []
    )
    for path in composition_files:
        rel = path.relative_to(REPO)
        errs = _validate_composition(path, validators, known_atoms, known_compositions)
        total_files += 1
        if errs:
            print(f"x {rel}")
            for err in errs:
                print(f"    {err}")
            total_errors += len(errs)
        else:
            print(f"ok {rel}")

    # Rules smoke
    rule_errors = _smoke_import_rules()
    for err in rule_errors:
        print(f"x {err}")
    total_errors += len(rule_errors)

    if total_errors:
        print(f"\n{total_errors} error(s) across {total_files} file(s)")
        return 1

    if total_files == 0:
        print("no atoms or compositions found", file=sys.stderr)
        return 1

    print(f"\nall {total_files} file(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
