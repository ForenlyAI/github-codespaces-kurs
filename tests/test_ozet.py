from decimal import Decimal
from pathlib import Path

from siparis_ozeti.__main__ import main
from siparis_ozeti.ozet import Siparis, kurus, oku, ozet, yazi

VERI = Path(__file__).resolve().parents[1] / "veri" / "siparisler.csv"


def s(urun, adet, fiyat, kdv="10", tarih="2026-10-05"):
    return Siparis(tarih, urun, adet, Decimal(fiyat), Decimal(kdv))


def test_kurus_yarim_yukari():
    assert kurus(Decimal("1.005")) == Decimal("1.01")
    assert kurus(Decimal("1.004")) == Decimal("1.00")


def test_iki_satirin_toplami_ve_kdv():
    o = ozet([s("simit", 2, "17.50"), s("ekmek", 3, "15.00", kdv="1")])
    assert o["ara_toplam"] == Decimal("80.00")
    assert o["kdv"] == Decimal("3.95")
    assert o["genel_toplam"] == Decimal("83.95")


def test_en_cok_satan_adede_gore():
    o = ozet([s("simit", 5, "17.50"), s("ekmek", 3, "15.00"), s("simit", 1, "17.50")])
    assert o["en_cok_satan"] == ("simit", 6)


def test_bos_liste():
    o = ozet([])
    assert o["satir"] == 0
    assert o["genel_toplam"] == Decimal("0.00")


def test_tarihe_gore_suzme():
    liste = [s("simit", 2, "17.50", tarih="2026-10-05"), s("simit", 4, "17.50", tarih="2026-10-06")]
    assert ozet(liste, "2026-10-06")["satir"] == 1


def test_ornek_dosya_okunur():
    assert len(oku(VERI)) == 15


def test_yazi_binlik_ayirac():
    metin = yazi(ozet([s("yaş pasta", 2, "640.00")]))
    assert "Genel toplam: 1.408,00 TL" in metin


def test_komut_satiri_olmayan_tarih(capsys):
    assert main([str(VERI), "--tarih", "2026-01-01"]) == 1
    assert "sipariş yok" in capsys.readouterr().err
