"""Komut satırı: python -m vardiya_raporu veri/gorevler.jsonl [--tur servis]"""

import argparse
import sys

from .rapor import oku, rapor, yazi


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="vardiya_raporu", description="Robot vardiya raporu")
    p.add_argument("dosya", help="görev kaydı (JSON Lines)")
    p.add_argument("--tur", help="yalnız bu görev türü (servis · toplama · sarj)")
    a = p.parse_args(argv)
    r = rapor(oku(a.dosya), a.tur)
    if r["gorev"] == 0:
        print(f"Bu türde görev yok: {a.tur}", file=sys.stderr)
        return 1
    print(yazi(r, a.tur))
    return 0


if __name__ == "__main__":
    sys.exit(main())
