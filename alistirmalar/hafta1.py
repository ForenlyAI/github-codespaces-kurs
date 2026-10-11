#!/usr/bin/env python3
"""Hafta 1 · Git Temelleri — Ders 1.1–1.4. Yalnız yerel git; internet ve GitHub hesabı gerekmez.

  python hafta1.py                 → alistirmalar/calisma/vardiya-raporu (sıfırdan), alistirmalar/cikti/1.x/*.txt
  python hafta1.py --cakismada-dur → Ders 1.3'teki çakışmada durur (Claude Code denemesi için aynı durum)

Yazar ve commit saatleri sabit (ortak.YEREL_KIMLIK): commit kimlikleri her makinede aynı çıkar.
Robot görev kaydı (kafede çay servisi yapan insansı robot, bir vardiya) ÖRNEKTİR."""

import datetime
import pathlib
import shutil
import sys

from ortak import CALISMA, YEREL_KIMLIK, Oturum, dosya, kayit

DEPO = CALISMA / "vardiya-raporu"
BASLA = datetime.datetime(2026, 10, 7, 11, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=3)))
VERI = (
    (pathlib.Path(__file__).resolve().parents[1] / "veri" / "gorevler.jsonl")
    .read_text(encoding="utf-8")
    .splitlines()
)
ILK = 14  # ilk commit'teki görev sayısı; kalan satırlar ikinci commit'te gelir

RAPOR_V1 = '''"""Robot vardiya raporu (ÖRNEK veri)."""
import json
import sys
from datetime import datetime


def oku(yol):
    with open(yol, encoding="utf-8") as f:
        return [json.loads(s) for s in f if s.strip()]


def sure_dk(g):
    fark = datetime.fromisoformat(g["bitis"]) - datetime.fromisoformat(g["baslangic"])
    return fark.total_seconds() / 60


def toplam_sure(gorevler):
    return sum(sure_dk(g) for g in gorevler)


if __name__ == "__main__":
    gorevler = oku(sys.argv[1])
    print(f"Görev: {len(gorevler)}")
    print(f"Çalışma süresi: {toplam_sure(gorevler)} dk")
'''
BASARI_FONK = """

def basari(gorevler):
    isler = [g for g in gorevler if g["tur"] != "sarj"]
    return 100 * sum(g["sonuc"] == "tamam" for g in isler) / len(isler)
"""
TEST = """from rapor import basari, oku, toplam_sure


def test_toplam_sure():
    assert round(toplam_sure(oku("gorevler.jsonl")), 1) == 103.4


def test_basari():
    assert round(basari(oku("gorevler.jsonl")), 1) == 80.0
"""
README_V1 = "# Vardiya raporu\n\nKafede çay servisi yapan insansı robotun görev kaydından vardiya raporu çıkarır (ÖRNEK veri).\n"
README_V2 = README_V1 + "\nKullanım: `python rapor.py gorevler.jsonl`\n"
GITIGNORE = "__pycache__/\n.pytest_cache/\n.venv/\n"
SURE_SATIRI = '    print(f"Çalışma süresi: {toplam_sure(gorevler)} dk")\n'
CALISTIR = "python rapor.py gorevler.jsonl"


def oku_rapor():
    return (DEPO / "rapor.py").read_text(encoding="utf-8")


def degistir(eski, yeni):
    s = oku_rapor()
    assert eski in s, eski
    dosya(DEPO, "rapor.py", s.replace(eski, yeni))


def main(cakismada_dur=False):
    if DEPO.exists():
        shutil.rmtree(DEPO)
    DEPO.mkdir(parents=True)

    # ---------- Ders 1.1 · Depo ve Commit ----------
    o = Oturum("1.1", "ilk-commit", DEPO, YEREL_KIMLIK, BASLA)
    dosya(DEPO, "README.md", README_V1)
    dosya(DEPO, "rapor.py", RAPOR_V1)
    dosya(DEPO, "gorevler.jsonl", "\n".join(VERI[:ILK]) + "\n")
    o.k("git init -b main")
    o.k("git status --short")
    o.k("git add README.md rapor.py gorevler.jsonl")
    o.k("git status --short")
    out = o.k('git commit -m "Vardiya raporu: ilk sürüm"')
    o.k("git log --oneline")
    o.k(CALISTIR)
    o.yaz()
    ilk = o.k(CALISTIR, goster=False).splitlines()
    kayit(
        d1_1_git_surum=o.k("git --version", goster=False).split()[-1],
        d1_1_izsiz=3,
        d1_1_ilk_commit_dosya=int(out.split(" file")[0].split()[-1]),
        d1_1_ilk_commit_satir=int(out.split("insertions")[0].split()[-1]),
        d1_1_ilk_hash=o.k("git rev-parse --short HEAD", goster=False),
        d1_1_ilk_gorev=ilk[0],
        d1_1_ilk_sure=ilk[1],
    )

    o2 = Oturum("1.1", "ikinci-commit", DEPO, YEREL_KIMLIK, o.saat)
    dosya(DEPO, "gorevler.jsonl", "\n".join(VERI) + "\n")
    o2.k("git status --short")
    o2.k("git diff --stat")
    o2.k("git add gorevler.jsonl")
    o2.k(f'git commit -m "Vardiyanın son {len(VERI) - ILK} görevi eklendi"')
    o2.k("git log --oneline")
    o2.k(CALISTIR)
    o2.yaz()
    son = o2.k(CALISTIR, goster=False).splitlines()
    kayit(d1_1_ikinci_ekleme=len(VERI) - ILK, d1_1_commit=2, d1_1_son_gorev=son[0], d1_1_son_sure=son[1])

    # ---------- Ders 1.2 · Dal ve Birleştirme ----------
    o = Oturum("1.2", "hizli-ileri", DEPO, YEREL_KIMLIK, o2.saat)
    o.k("git switch -c basari")
    dosya(DEPO, "rapor.py", oku_rapor().replace("\n\nif __name__", BASARI_FONK + "\n\nif __name__"))
    degistir(SURE_SATIRI, SURE_SATIRI + '    print(f"Başarı: %{basari(gorevler):.1f}")\n')
    o.k('git commit -am "Başarı oranı eklendi"')
    o.k("git switch main")
    o.k("git merge basari")
    o.k("git branch")
    o.k(CALISTIR)
    o.yaz()
    kayit(d1_2_basari=o.k(CALISTIR, goster=False).splitlines()[2])

    o2 = Oturum("1.2", "birlestirme-commit", DEPO, YEREL_KIMLIK, o.saat)
    o2.k("git switch -c test-ekle")
    dosya(DEPO, "test_rapor.py", TEST)
    o2.k("git add test_rapor.py")
    o2.k('git commit -m "Süre ve başarı için test"')
    o2.k("git switch main")
    dosya(DEPO, "README.md", README_V2)
    o2.k('git commit -am "README: kullanım satırı"')
    o2.k("git merge --no-edit test-ekle")
    o2.k("git log --oneline --graph")
    o2.k("python -m pytest -q -p no:cacheprovider", gizle=r"^\s*$")
    o2.yaz()
    kayit(
        d1_2_commit=int(o2.k("git rev-list --count HEAD", goster=False)),
        d1_2_test=2,
        d1_2_dal=len(o2.k("git branch", goster=False).splitlines()),
    )

    # ---------- Ders 1.3 · Çakışma Çözme ----------
    o = Oturum("1.3", "cakisma", DEPO, YEREL_KIMLIK, o2.saat)
    o.k("git switch -c bicim")
    degistir(SURE_SATIRI, '    print(f"Çalışma süresi: {toplam_sure(gorevler):.1f} dk")\n')
    o.k('git commit -am "Süreyi tek ondalıkla yaz"')
    o.k("git switch main")
    degistir(SURE_SATIRI, '    print(f"Görev süresi toplamı: {toplam_sure(gorevler)} dk")\n')
    o.k('git commit -am "Süre satırının adı: görev süresi toplamı"')
    o.k("git merge bicim", beklenen_kod=1)
    o.k("git status --short")
    o.k("grep -n -A4 '<<<<<<<' rapor.py")
    o.yaz()
    s = oku_rapor()
    kayit(
        d1_3_cakisan_dosya=1,
        d1_3_isaret=sum(s.count(m) for m in ("<<<<<<<", "=======", ">>>>>>>")),
        d1_3_merge_cikis=1,
    )
    if cakismada_dur:
        print("çakışmada durdu:", DEPO)
        return

    o2 = Oturum("1.3", "cozum", DEPO, YEREL_KIMLIK, o.saat)
    bas, bit = s.index("<<<<<<<"), s.index(">>>>>>>")
    bit = s.index("\n", bit) + 1
    dosya(
        DEPO,
        "rapor.py",
        s[:bas] + '    print(f"Görev süresi toplamı: {toplam_sure(gorevler):.1f} dk")\n' + s[bit:],
    )
    o2.k("grep -c -E '^(<<<<<<<|=======|>>>>>>>)' rapor.py", beklenen_kod=1)
    o2.k("git diff --check")
    o2.k("python -m pytest -q -p no:cacheprovider")
    o2.k(CALISTIR)
    o2.k("git add rapor.py")
    o2.k("git commit --no-edit")
    o2.k("git log --oneline --graph -6")
    o2.yaz()
    kayit(d1_3_isaret_sonra=0, d1_3_cozum_satiri=o2.k(CALISTIR, goster=False).splitlines()[1])

    # ---------- Ders 1.4 · Geçmiş ve Geri Alma ----------
    o = Oturum("1.4", "geri-alma", DEPO, YEREL_KIMLIK, o2.saat)
    degistir('    isler = [g for g in gorevler if g["tur"] != "sarj"]\n', "    isler = gorevler\n")
    o.k('git commit -am "Başarı hesabını sadeleştir"')
    o.k("python -m pytest -q -p no:cacheprovider --tb=no -rf", beklenen_kod=1)
    kotu = o.k(CALISTIR, goster=False).splitlines()[2]
    o.k("git log --oneline -3")
    o.k("git show --stat --format='%h %s' HEAD")
    o.k("git revert --no-edit HEAD", gizle=r"^ Date:")
    o.k("python -m pytest -q -p no:cacheprovider")
    o.k("git log --oneline -3")
    o.yaz()
    kayit(d1_4_kotu_basari=kotu, d1_4_dogru_basari=o.k(CALISTIR, goster=False).splitlines()[2])

    o2 = Oturum("1.4", "gitignore", DEPO, YEREL_KIMLIK, o.saat)
    o2.k("python -m pytest -q", goster=False)  # önbellek klasörleri oluşur
    o2.k("git status --short")
    izsiz_once = len(o2.k("git status --short", goster=False).splitlines())
    dosya(DEPO, ".gitignore", GITIGNORE)
    o2.k("cat .gitignore")
    o2.k("git status --short")
    o2.k("git add .gitignore")
    o2.k('git commit -m "Önbellek klasörleri izlenmesin"')
    o2.k("git status --short")
    o2.yaz()

    o3 = Oturum("1.4", "hafta-ozeti", DEPO, YEREL_KIMLIK, o2.saat)
    o3.k("git log --oneline --graph")
    o3.k("git rev-list --count HEAD")
    o3.k("git log --merges --oneline")
    o3.yaz()
    kayit(
        d1_4_izsiz_once=izsiz_once,
        d1_4_izsiz_sonra=0,
        d1_4_commit=int(o3.k("git rev-list --count HEAD", goster=False)),
        d1_4_birlesme=len(o3.k("git log --merges --oneline", goster=False).splitlines()),
        d1_4_son_hash=o3.k("git rev-parse --short HEAD", goster=False),
    )
    print("hafta 1 tamam:", DEPO)


if __name__ == "__main__":
    main("--cakismada-dur" in sys.argv)
