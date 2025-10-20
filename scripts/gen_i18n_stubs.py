from __future__ import annotations

from infra.i18n.manage import DEFAULT_REGISTRY_PATH, DEFAULT_STUB_PATH, generate_stub, load_registry


def main() -> None:
    keys = load_registry(DEFAULT_REGISTRY_PATH)
    generate_stub(keys, DEFAULT_STUB_PATH)
    print(f"Generated stub file with {len(keys)} keys at {DEFAULT_STUB_PATH}")


if __name__ == "__main__":
    main()
