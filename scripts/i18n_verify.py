
from infra.i18n.manage import DEFAULT_LOCALES_DIR, verify_translations


def main() -> None:
    errors = verify_translations(DEFAULT_LOCALES_DIR)
    if errors:
        for err in errors:
            print(err)
        raise SystemExit(1)
    print("All translations are filled.")


if __name__ == "__main__":
    main()
