"""Sipariş özeti: küçük bir fırının günlük siparişlerinden toplam, KDV ve en çok satan ürün.

Veri dosyası CSV: tarih, urun, adet, birim_fiyat, kdv_orani (yüzde). Örnek veri ÖRNEKTİR.
Para hesabı Decimal ile yapılır; kuruş yarım yukarı yuvarlanır.
"""

import csv
import sys
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

KURUS = Decimal("0.01")


@dataclass(frozen=True)
class Siparis:
    tarih: str
    urun: str
    adet: int
    birim_fiyat: Decimal
    kdv_orani: Decimal


def kurus(tutar: Decimal) -> Decimal:
    """Tutarı kuruşa yuvarlar (yarım yukarı)."""
    return tutar.quantize(KURUS, rounding=ROUND_HALF_UP)


def tl(tutar: Decimal) -> str:
    """Tutarı Türkçe yazımla verir: 12608.5 -> '12.608,50 TL'."""
    return f"{tutar:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".") + " TL"


def oku(yol: str | Path) -> list[Siparis]:
    """CSV dosyasını okur, her satırı bir Siparis yapar.

    Adedi tam sayı olmayan satır atlanır; dosyadaki satır numarası (başlık 1. satır) stderr'e uyarı olarak yazılır.
    """
    siparisler = []
    with open(yol, encoding="utf-8", newline="") as f:
        okuyucu = csv.DictReader(f)
        for s in okuyucu:
            try:
                adet = int(s["adet"])
            except (TypeError, ValueError):
                print(
                    f"Uyarı: {okuyucu.line_num}. satır atlandı, adet sayı değil: {s['adet']!r}",
                    file=sys.stderr,
                )
                continue
            siparisler.append(
                Siparis(
                    tarih=s["tarih"],
                    urun=s["urun"],
                    adet=adet,
                    birim_fiyat=Decimal(s["birim_fiyat"]),
                    kdv_orani=Decimal(s["kdv_orani"]),
                )
            )
    return siparisler


def ozet(siparisler: list[Siparis], tarih: str | None = None) -> dict:
    """Ara toplam, KDV, genel toplam ve en çok satan ürünü hesaplar. tarih verilirse yalnız o gün."""
    secilen = [s for s in siparisler if tarih is None or s.tarih == tarih]
    ara_toplam = sum((s.adet * s.birim_fiyat for s in secilen), Decimal("0"))
    kdv = sum((s.adet * s.birim_fiyat * s.kdv_orani / 100 for s in secilen), Decimal("0"))
    adetler: dict[str, int] = {}
    for s in secilen:
        adetler[s.urun] = adetler.get(s.urun, 0) + s.adet
    en_cok = max(adetler.items(), key=lambda kv: kv[1]) if adetler else ("-", 0)
    return {
        "satir": len(secilen),
        "ara_toplam": kurus(ara_toplam),
        "kdv": kurus(kdv),
        "genel_toplam": kurus(ara_toplam) + kurus(kdv),
        "en_cok_satan": en_cok,
    }


def yazi(o: dict, tarih: str | None = None) -> str:
    """Özeti ekrana yazılacak metne çevirir."""
    urun, adet = o["en_cok_satan"]
    return "\n".join(
        [
            f"Özet: {tarih or 'bütün günler'}",
            f"Satır: {o['satir']}",
            f"Ara toplam: {tl(o['ara_toplam'])}",
            f"KDV: {tl(o['kdv'])}",
            f"Genel toplam: {tl(o['genel_toplam'])}",
            f"En çok satan: {urun} ({adet} adet)",
        ]
    )
