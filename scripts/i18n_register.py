from __future__ import annotations

from infra.i18n.manage import collect_error_keys, write_registry, DEFAULT_REGISTRY_PATH


def main() -> None:
    keys = collect_error_keys()
    write_registry(keys, DEFAULT_REGISTRY_PATH)
    print(f"Registered {len(keys)} i18n keys into {DEFAULT_REGISTRY_PATH}")


if __name__ == "__main__":
    main()
