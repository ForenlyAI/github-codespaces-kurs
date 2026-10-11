"""Vardiya raporu: kafede çay servisi yapan insansı robotun görev kayıtlarından (JSON Lines) özet.

Her satır bir görev: gorev_id, baslangic, bitis (ISO 8601), tur (servis · toplama · sarj),
sonuc (tamam · yarim · hata), hata_kodu. Örnek veri ÖRNEKTİR.
Başarı oranı yalnız iş görevlerinden (servis + toplama) hesaplanır; şarj iş görevi sayılmaz.
"""

import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

IS_TURLERI = ("servis", "toplama")


@dataclass(frozen=True)
class Gorev:
    gorev_id: str
    baslangic: datetime
    bitis: datetime
    tur: str
    sonuc: str
    hata_kodu: str | None

    @property
    def sure_sn(self) -> float:
        return (self.bitis - self.baslangic).total_seconds()


def oku(yol: str | Path) -> list[Gorev]:
    """JSON Lines dosyasını okur, her satırı bir Gorev yapar.

    Okunamayan satır (ör. elektrik kesintisinde yarım yazılmış) atlanır, numarası stderr'e uyarı olarak yazılır.
    """
    gorevler = []
    with open(yol, encoding="utf-8") as f:
        for no, satir in enumerate(f, start=1):
            if not satir.strip():
                continue
            try:
                k = json.loads(satir)
                gorev = Gorev(
                    gorev_id=k["gorev_id"],
                    baslangic=datetime.fromisoformat(k["baslangic"]),
                    bitis=datetime.fromisoformat(k["bitis"]),
                    tur=k["tur"],
                    sonuc=k["sonuc"],
                    hata_kodu=k.get("hata_kodu"),
                )
            except (ValueError, KeyError, TypeError):
                print(f"Uyarı: {no}. satır bozuk, atlandı", file=sys.stderr)
                continue
            gorevler.append(gorev)
    return gorevler


def rapor(gorevler: list[Gorev], tur: str | None = None) -> dict:
    """Görev sayısı, başarı oranı, ortalama ve en uzun süre, hata dağılımı, şarj süresi payı."""
    secilen = [g for g in gorevler if tur is None or g.tur == tur]
    isler = [g for g in secilen if g.tur in IS_TURLERI]
    toplam_sn = sum(g.sure_sn for g in secilen)
    sarj_sn = sum(g.sure_sn for g in secilen if g.tur == "sarj")
    en_uzun = max(isler, key=lambda g: g.sure_sn) if isler else None
    return {
        "gorev": len(secilen),
        "is_gorevi": len(isler),
        "tamam": sum(g.sonuc == "tamam" for g in isler),
        "basari_yuzde": round(100 * sum(g.sonuc == "tamam" for g in isler) / len(isler), 1) if isler else 0.0,
        "ort_sure_sn": round(sum(g.sure_sn for g in isler) / len(isler), 1) if isler else 0.0,
        "en_uzun": (en_uzun.gorev_id, en_uzun.sure_sn) if en_uzun else ("-", 0.0),
        "hatalar": dict(Counter(g.hata_kodu for g in secilen if g.hata_kodu).most_common()),
        "sarj_payi_yuzde": round(100 * sarj_sn / toplam_sn, 1) if toplam_sn else 0.0,
    }


def sayi(x: float) -> str:
    """Türkçe ondalık: 85.7 -> '85,7'."""
    return f"{x:.1f}".replace(".", ",")


def yazi(r: dict, tur: str | None = None) -> str:
    """Raporu ekrana yazılacak metne çevirir."""
    gid, sn = r["en_uzun"]
    hatalar = ", ".join(f"{k} × {v}" for k, v in r["hatalar"].items()) or "yok"
    return "\n".join(
        [
            f"Vardiya raporu: {tur or 'bütün görevler'}",
            f"Görev: {r['gorev']} (iş görevi {r['is_gorevi']})",
            f"Başarı: %{sayi(r['basari_yuzde'])} ({r['tamam']} / {r['is_gorevi']})",
            f"Ortalama süre: {sayi(r['ort_sure_sn'])} sn",
            f"En uzun görev: {gid} ({sayi(sn)} sn)",
            f"Hatalar: {hatalar}",
            f"Şarj payı: %{sayi(r['sarj_payi_yuzde'])}",
        ]
    )
