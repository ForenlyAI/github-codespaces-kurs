#!/usr/bin/env python3
"""Bitirme denetimi: deponuzun RUBRIK.md ölçütlerini karşılayıp karşılamadığını söyler.

  python kontrol.py            → dosya ölçütleri + testler (internet gerekmez)
  python kontrol.py --github   → ek olarak GitHub'daki durum: korumalı ana dal, incelenmiş PR, yeşil CI (gh CLI ile)
  python kontrol.py --hafta1   → alistirmalar/cikti ile beklenen/alistirmalar karşılaştırması (Hafta 1 alıştırması)

Her satır YETERLİ ya da EKSİK yazar; EKSİK satırın yanında ne yapmanız gerektiği yazar.
"""

import json
import pathlib
import re
import subprocess
import sys

KOK = pathlib.Path(__file__).resolve().parent
sonuc = []


def satir(ad, tamam, neden=""):
    sonuc.append(tamam)
    print(f"{'YETERLİ' if tamam else 'EKSİK  '}  {ad}" + ("" if tamam or not neden else f"  → {neden}"))


def jsonc(yol):
    """devcontainer.json yorum satırı içerebilir (JSON with Comments): // yorumları atıp okur."""
    metin = re.sub(r"(?m)^\s*//.*$", "", yol.read_text(encoding="utf-8"))
    return json.loads(metin)


def kos(*komut):
    r = subprocess.run(komut, cwd=KOK, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def dosya_olcutleri():
    dc = KOK / ".devcontainer" / "devcontainer.json"
    if not dc.exists():
        satir("1 · Geliştirme ortamı kod olarak", False, ".devcontainer/devcontainer.json yok")
    else:
        try:
            d = jsonc(dc)
            ok = ("image" in d or "build" in d) and any(
                k in d for k in ("postCreateCommand", "onCreateCommand")
            )
            satir("1 · Geliştirme ortamı kod olarak", ok, "image (ya da build) ve postCreateCommand gerekli")
        except json.JSONDecodeError as e:
            satir("1 · Geliştirme ortamı kod olarak", False, f"devcontainer.json okunamadı: {e}")
    akislar = list((KOK / ".github" / "workflows").glob("*.y*ml"))
    metin = "\n".join(a.read_text(encoding="utf-8") for a in akislar)
    ok = bool(akislar) and "pull_request" in metin and "pytest" in metin
    satir(
        "2 · Sürekli bütünleştirme dosyası",
        ok,
        "pull_request ile tetiklenen ve pytest koşan bir iş akışı gerekli",
    )
    kod, cikti = kos(sys.executable, "-m", "pytest", "-q")
    ozet = cikti.strip().splitlines()[-1] if cikti.strip() else ""
    satir(f"2 · Testler yerelde geçiyor ({ozet})", kod == 0, "python -m pytest -q çıktısına bakın")
    sablon = KOK / ".github" / "pull_request_template.md"
    satir(
        "5 · PR şablonunda yapay zekâ beyanı",
        sablon.exists() and "Yapay zekâ" in sablon.read_text(encoding="utf-8"),
        ".github/pull_request_template.md içinde 'Yapay zekâ kullanıldıysa' bölümü olmalı",
    )


def github_olcutleri():
    kod, depo = kos("gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    if kod != 0:
        satir("GitHub bağlantısı", False, "gh auth login yapın ve depo klasöründe çalıştırın")
        return
    depo = depo.strip()
    kod, k = kos("gh", "api", f"repos/{depo}/branches/main/protection")
    if kod == 0:
        k = json.loads(k)
        ok = bool(k.get("required_pull_request_reviews")) and not k.get("allow_force_pushes", {}).get(
            "enabled", True
        )
        satir("3 · Korumalı ana dal", ok, "PR zorunlu ve zorla gönderme kapalı olmalı")
    else:
        satir(
            "3 · Korumalı ana dal",
            False,
            "main için dal koruma kuralı yok (depo herkese açık olmalı ya da ücretli plan)",
        )
    kod, p = kos(
        "gh", "pr", "list", "--state", "merged", "--json", "number,reviews,comments,body", "--limit", "50"
    )
    prler = json.loads(p) if kod == 0 else []
    incelenen = [x for x in prler if x["reviews"] or x["comments"]]
    satir(
        f"4 · İncelenmiş ve birleşmiş PR ({len(incelenen)} adet)",
        bool(incelenen),
        "en az bir PR'da inceleme yorumu olmalı ve PR birleşmiş olmalı",
    )
    bagli = [x for x in incelenen if re.search(r"(?i)\b(closes|fixes|resolves) #\d+", x.get("body") or "")]
    satir("4 · PR bir issue'yu kapatıyor", bool(bagli), "PR açıklamasına 'Closes #<issue no>' yazın")
    kod, r = kos("gh", "run", "list", "--branch", "main", "--limit", "1", "--json", "conclusion,name")
    son = json.loads(r)[0] if kod == 0 and json.loads(r) else {}
    satir(
        f"2 · Ana dalda son CI koşusu ({son.get('conclusion', 'yok')})",
        son.get("conclusion") == "success",
        "Actions sekmesinde ana dalın son koşusu yeşil olmalı",
    )


def hafta1():
    cikti, beklenen = KOK / "alistirmalar" / "cikti", KOK / "beklenen" / "alistirmalar"
    fark = 0
    for b in sorted(beklenen.rglob("*.txt")):
        c = cikti / b.relative_to(beklenen)
        sadele = lambda m: re.sub(r" in \d+\.\d+s", " in …s", m)  # noqa: E731  (pytest süresi makineye göre değişir)
        ayni = c.exists() and sadele(c.read_text(encoding="utf-8")) == sadele(b.read_text(encoding="utf-8"))
        fark += not ayni
        satir(f"Hafta 1 · {b.relative_to(beklenen)}", ayni, "önce: python alistirmalar/hafta1.py")
    print(f"{fark} fark")


if __name__ == "__main__":
    if "--hafta1" in sys.argv:
        hafta1()
    else:
        dosya_olcutleri()
        if "--github" in sys.argv:
            github_olcutleri()
    print(f"\n{sum(sonuc)} / {len(sonuc)} ölçüt yeterli")
    sys.exit(0 if all(sonuc) else 1)
