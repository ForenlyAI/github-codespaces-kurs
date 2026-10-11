#!/usr/bin/env python3
"""Hafta 1 · Git Temelleri — Ders 1.1–1.4. Yalnız yerel git; internet ve GitHub hesabı gerekmez.

  python hafta1.py                 → alistirmalar/calisma/siparis-ozeti (sıfırdan), alistirmalar/cikti/1.x/*.txt
  python hafta1.py --cakismada-dur → Ders 1.3'teki çakışmada durur (Claude Code denemesi için aynı durum)

Yazar ve commit saatleri sabit (ortak.YEREL_KIMLIK): commit kimlikleri her makinede aynı çıkar.
Fırın siparişleri ve KDV oranları ÖRNEKTİR."""

import datetime
import pathlib
import shutil
import sys

from ortak import CALISMA, YEREL_KIMLIK, Oturum, dosya, kayit

DEPO = CALISMA / "siparis-ozeti"
BASLA = datetime.datetime(2026, 10, 5, 9, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=3)))
VERI = (
    (pathlib.Path(__file__).resolve().parents[1] / "veri" / "siparisler.csv")
    .read_text(encoding="utf-8")
    .splitlines()
)

OZET_V1 = '''"""Fırın sipariş özeti (ÖRNEK veri)."""
import csv
import sys
from decimal import Decimal


def oku(yol):
    with open(yol, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def toplam(satirlar):
    return sum(int(s["adet"]) * Decimal(s["birim_fiyat"]) for s in satirlar)


if __name__ == "__main__":
    satirlar = oku(sys.argv[1])
    print(f"Satır: {len(satirlar)}")
    print(f"Toplam: {toplam(satirlar)} TL")
'''
KDV_FONK = """

def kdv(satirlar):
    return sum(int(s["adet"]) * Decimal(s["birim_fiyat"]) * Decimal(s["kdv_orani"]) / 100 for s in satirlar)
"""
TEST = """from decimal import Decimal

from ozet import kdv, oku, toplam


def test_toplam():
    assert toplam(oku("siparisler.csv")) == Decimal("12608.50")


def test_kdv():
    assert round(kdv(oku("siparisler.csv")), 2) == Decimal("1094.80")
"""
README_V1 = (
    "# Sipariş özeti\n\nKüçük bir fırının günlük siparişlerinden toplam tutarı hesaplar (ÖRNEK veri).\n"
)
README_V2 = README_V1 + "\nKullanım: `python ozet.py siparisler.csv`\n"
GITIGNORE = "__pycache__/\n.pytest_cache/\n.venv/\n"
TOPLAM_SATIRI = '    print(f"Toplam: {toplam(satirlar)} TL")\n'


def oku_ozet():
    return (DEPO / "ozet.py").read_text(encoding="utf-8")


def degistir(eski, yeni):
    s = oku_ozet()
    assert eski in s, eski
    dosya(DEPO, "ozet.py", s.replace(eski, yeni))


def main(cakismada_dur=False):
    if DEPO.exists():
        shutil.rmtree(DEPO)
    DEPO.mkdir(parents=True)
    saat = BASLA

    # ---------- Ders 1.1 · Depo ve Commit ----------
    o = Oturum("1.1", "ilk-commit", DEPO, YEREL_KIMLIK, saat)
    dosya(DEPO, "README.md", README_V1)
    dosya(DEPO, "ozet.py", OZET_V1)
    dosya(DEPO, "siparisler.csv", "\n".join(VERI[:11]) + "\n")
    o.k("git init -b main")
    o.k("git status --short")
    o.k("git add README.md ozet.py siparisler.csv")
    o.k("git status --short")
    out = o.k('git commit -m "Sipariş özeti: ilk sürüm"')
    o.k("git log --oneline")
    o.k("python ozet.py siparisler.csv")
    o.yaz()
    ilk_hash = o.k("git rev-parse --short HEAD", goster=False)
    kayit(
        d1_1_git_surum=o.k("git --version", goster=False).split()[-1],
        d1_1_izsiz=3,
        d1_1_ilk_commit_dosya=int(out.split(" file")[0].split()[-1]),
        d1_1_ilk_commit_satir=int(out.split("insertions")[0].split()[-1]),
        d1_1_ilk_hash=ilk_hash,
        d1_1_ilk_satir=10,
        d1_1_ilk_toplam=o.k("python ozet.py siparisler.csv", goster=False).splitlines()[1],
    )

    o2 = Oturum("1.1", "ikinci-commit", DEPO, YEREL_KIMLIK, o.saat)
    dosya(DEPO, "siparisler.csv", "\n".join(VERI) + "\n")
    o2.k("git status --short")
    o2.k("git diff --stat")
    o2.k("git add siparisler.csv")
    o2.k('git commit -m "7 Ekim siparişleri eklendi"')
    o2.k("git log --oneline")
    o2.k("python ozet.py siparisler.csv")
    o2.yaz()
    kayit(
        d1_1_ikinci_ekleme=5,
        d1_1_commit=2,
        d1_1_son_toplam=o2.k("python ozet.py siparisler.csv", goster=False).splitlines()[1],
    )

    # ---------- Ders 1.2 · Dal ve Birleştirme ----------
    o = Oturum("1.2", "hizli-ileri", DEPO, YEREL_KIMLIK, o2.saat)
    o.k("git switch -c kdv")
    dosya(DEPO, "ozet.py", oku_ozet().replace("\n\nif __name__", KDV_FONK + "\n\nif __name__"))
    degistir(TOPLAM_SATIRI, TOPLAM_SATIRI + '    print(f"KDV: {kdv(satirlar):.2f} TL")\n')
    o.k('git commit -am "KDV hesabı eklendi"')
    o.k("git switch main")
    o.k("git merge kdv")
    o.k("git branch")
    o.k("python ozet.py siparisler.csv")
    o.yaz()
    kayit(d1_2_kdv=o.k("python ozet.py siparisler.csv", goster=False).splitlines()[2])

    o2 = Oturum("1.2", "birlestirme-commit", DEPO, YEREL_KIMLIK, o.saat)
    o2.k("git switch -c test-ekle")
    dosya(DEPO, "test_ozet.py", TEST)
    o2.k("git add test_ozet.py")
    o2.k('git commit -m "Toplam ve KDV için test"')
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
    degistir(TOPLAM_SATIRI, '    print(f"Toplam: {toplam(satirlar):,.2f} TL")\n')
    o.k('git commit -am "Toplamda binlik ayırıcı"')
    o.k("git switch main")
    degistir(TOPLAM_SATIRI, '    print(f"Ara toplam: {toplam(satirlar)} TL")\n')
    o.k('git commit -am "Toplam satırının adı: ara toplam"')
    o.k("git merge bicim", beklenen_kod=1)
    o.k("git status --short")
    o.k("grep -n -A4 '<<<<<<<' ozet.py")
    o.yaz()
    s = oku_ozet()
    kayit(
        d1_3_cakisan_dosya=1,
        d1_3_isaret=sum(s.count(m) for m in ("<<<<<<<", "=======", ">>>>>>>")),
        d1_3_merge_cikis=1,
    )
    if cakismada_dur:
        print("çakışmada durdu:", DEPO)
        return

    o2 = Oturum("1.3", "cozum", DEPO, YEREL_KIMLIK, o.saat)
    bas, son = s.index("<<<<<<<"), s.index(">>>>>>>")
    son = s.index("\n", son) + 1
    dosya(DEPO, "ozet.py", s[:bas] + '    print(f"Ara toplam: {toplam(satirlar):,.2f} TL")\n' + s[son:])
    o2.k("grep -c -E '^(<<<<<<<|=======|>>>>>>>)' ozet.py", beklenen_kod=1)
    o2.k("git diff --check")
    o2.k("python -m pytest -q -p no:cacheprovider")
    o2.k("python ozet.py siparisler.csv")
    o2.k("git add ozet.py")
    o2.k("git commit --no-edit")
    o2.k("git log --oneline --graph -6")
    o2.yaz()
    kayit(d1_3_cozum_satiri=o2.k("python ozet.py siparisler.csv", goster=False).splitlines()[1])

    # ---------- Ders 1.4 · Geçmiş ve Geri Alma ----------
    o = Oturum("1.4", "geri-alma", DEPO, YEREL_KIMLIK, o2.saat)
    degistir("/ 100 for s", "/ 10 for s")
    o.k('git commit -am "KDV hesabını sadeleştir"')
    o.k("python -m pytest -q -p no:cacheprovider --tb=no -rf", beklenen_kod=1)
    kotu_kdv = o.k("python ozet.py siparisler.csv", goster=False).splitlines()[2]
    o.k("git log --oneline -3")
    o.k("git show --stat --format='%h %s' HEAD")
    o.k("git revert --no-edit HEAD", gizle=r"^ Date:")
    o.k("python -m pytest -q -p no:cacheprovider")
    o.k("git log --oneline -3")
    o.yaz()
    kayit(
        d1_4_kotu_kdv=kotu_kdv,
        d1_4_dogru_kdv=o.k("python ozet.py siparisler.csv", goster=False).splitlines()[2],
    )

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
