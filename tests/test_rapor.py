from datetime import datetime, timedelta
from pathlib import Path

from vardiya_raporu.__main__ import main
from vardiya_raporu.rapor import Gorev, oku, rapor, sayi, yazi

VERI = Path(__file__).resolve().parents[1] / "veri" / "gorevler.jsonl"
T0 = datetime(2026, 10, 7, 8, 0, 0)


def g(tur, sure_sn, sonuc="tamam", kod=None, no=1):
    return Gorev(f"G{no:03d}", T0, T0 + timedelta(seconds=sure_sn), tur, sonuc, kod)


def test_sure_saniye():
    assert g("servis", 114).sure_sn == 114


def test_basari_yalniz_is_gorevlerinden():
    r = rapor([g("servis", 100), g("servis", 120, "hata", "E07"), g("sarj", 1500)])
    assert r["is_gorevi"] == 2
    assert r["basari_yuzde"] == 50.0


def test_sarj_payi():
    r = rapor([g("servis", 500), g("sarj", 1500)])
    assert r["sarj_payi_yuzde"] == 75.0


def test_en_uzun_ve_ortalama():
    r = rapor([g("servis", 100, no=1), g("toplama", 250, no=2)])
    assert r["en_uzun"] == ("G002", 250.0)
    assert r["ort_sure_sn"] == 175.0


def test_hata_dagilimi():
    r = rapor(
        [g("servis", 100, "hata", "E07"), g("toplama", 200, "hata", "E07"), g("servis", 100, "yarim", "E21")]
    )
    assert r["hatalar"] == {"E07": 2, "E21": 1}


def test_ornek_dosya_okunur():
    assert len(oku(VERI)) == 22


def test_turkce_ondalik():
    assert sayi(85.7) == "85,7"
    assert "Başarı: %50,0 (1 / 2)" in yazi(rapor([g("servis", 100), g("servis", 100, "hata", "E07")]))


def test_komut_satiri_olmayan_tur(capsys):
    assert main([str(VERI), "--tur", "temizlik"]) == 1
    assert "görev yok" in capsys.readouterr().err
