"""Komut satırı: python -m siparis_ozeti veri/siparisler.csv [--tarih 2026-10-06]"""

import argparse
import sys

from .ozet import oku, ozet, yazi


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="siparis_ozeti", description="Günlük sipariş özeti")
    p.add_argument("dosya", help="sipariş CSV dosyası")
    p.add_argument("--tarih", help="yalnız bu gün (YYYY-AA-GG)")
    a = p.parse_args(argv)
    o = ozet(oku(a.dosya), a.tarih)
    if o["satir"] == 0:
        print(f"Bu tarihte sipariş yok: {a.tarih}", file=sys.stderr)
        return 1
    print(yazi(o, a.tarih))
    return 0


if __name__ == "__main__":
    sys.exit(main())
