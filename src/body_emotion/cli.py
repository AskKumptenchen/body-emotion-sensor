from __future__ import annotations

from .commands import legacy_cli_main


def main() -> None:
    raise SystemExit(legacy_cli_main())


if __name__ == "__main__":
    main()
