from __future__ import annotations

from .commands import legacy_bootstrap_main


def main() -> None:
    raise SystemExit(legacy_bootstrap_main())


if __name__ == "__main__":
    main()
