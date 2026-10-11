"""GitHub ve Codespaces ile Yazılım Geliştirme — alıştırma ortak araçları.

Derslerdeki her komut çıktısı burada GERÇEKTEN koşulan git / gh komutlarından gelir:
  Oturum(ders, ad, klasor)  : komutları bash'te sırayla koşar, "$ komut" + çıktıyı ekran/<ders>/<ad>.txt'ye yazar
  kayit(anahtar=değer)      : ölçümü OLCUMLER.json'a yazar (derslerdeki bütün sayılar buradan gelir)
Yerel alıştırmalarda (Hafta 1) yazar adı, e-posta ve commit saatleri sabittir; bu yüzden commit kimlikleri
(hash) her makinede aynı çıkar ve öğrenci kendi koşumunu beklenen/ klasörüyle birebir karşılaştırabilir.
Örnek veri (kafede çay servisi yapan insansı robotun görev kaydı) ÖRNEKTİR.
"""

import datetime
import json
import os
import pathlib
import re
import subprocess

LAB = pathlib.Path(__file__).resolve().parent
OLC = LAB / "cikti" / "OLCUMLER.json"
EKRAN = LAB / "cikti"
CALISMA = LAB / "calisma"

# yerel alıştırmalar için sabit kimlik (kişisel bilgi değil)
YEREL_KIMLIK = {
    "GIT_AUTHOR_NAME": "Kurs Ogrencisi",
    "GIT_AUTHOR_EMAIL": "ogrenci@example.com",
    "GIT_COMMITTER_NAME": "Kurs Ogrencisi",
    "GIT_COMMITTER_EMAIL": "ogrenci@example.com",
}
# GitHub'a gönderilen commit'ler için hesabın gizli (noreply) adresi
GITHUB_KIMLIK = {
    "GIT_AUTHOR_NAME": "Forenly AI Academy",
    "GIT_AUTHOR_EMAIL": "34220734+ForenlyAI@users.noreply.github.com",
    "GIT_COMMITTER_NAME": "Forenly AI Academy",
    "GIT_COMMITTER_EMAIL": "34220734+ForenlyAI@users.noreply.github.com",
}


def _j(v):
    if isinstance(v, float):
        return round(v, 4)
    if isinstance(v, (list, tuple)):
        return [_j(x) for x in v]
    if isinstance(v, dict):
        return {k: _j(x) for k, x in v.items()}
    return v


def kayit(**kw):
    """Ölçümleri OLCUMLER.json'a yazar (var olan anahtarı günceller)."""
    OLC.parent.mkdir(exist_ok=True)
    d = json.loads(OLC.read_text()) if OLC.exists() else {}
    d.update({k: _j(v) for k, v in kw.items()})
    OLC.write_text(json.dumps(d, ensure_ascii=False, indent=1, sort_keys=True))


def olcum(anahtar):
    return json.loads(OLC.read_text())[anahtar]


def temizle(metin, klasor=None):
    """Çıktıdan makineye özgü yolları çıkarır (ev klasörü, çalışma klasörü)."""
    if klasor:
        metin = metin.replace(str(klasor), "vardiya-raporu")
    metin = metin.replace(str(LAB), "lab").replace(str(pathlib.Path.home()), "~")
    metin = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", metin)  # renk kodları
    return metin


class Oturum:
    """Bir ders ekranı: komutlar gerçek bash'te koşulur, kayda '$ komut' ve çıktısı girer."""

    def __init__(self, ders, ad, klasor, kimlik=None, saat=None):
        self.ders, self.ad, self.klasor = ders, ad, pathlib.Path(klasor)
        self.satirlar = []
        self.kimlik = kimlik or {}
        self.saat = saat  # sabit commit saati (yerel alıştırma); None ise gerçek saat

    def _ortam(self):
        e = dict(
            os.environ,
            LANG="C.UTF-8",
            LC_ALL="C.UTF-8",
            GIT_PAGER="cat",
            PAGER="cat",
            NO_COLOR="1",
            GH_PROMPT_DISABLED="1",
            GIT_TERMINAL_PROMPT="0",
            **self.kimlik,
        )
        e.pop("GIT_DIR", None)
        if self.saat is not None:
            t = self.saat.isoformat()
            e.update(GIT_AUTHOR_DATE=t, GIT_COMMITTER_DATE=t)
        return e

    def k(self, komut, goster=True, beklenen_kod=0, gizle=None):
        """Komutu koşar; çıkış kodu beklenenden farklıysa durur. gizle: kayda girmeyecek satırlar için düzenli ifade."""
        r = subprocess.run(
            ["bash", "-c", komut], cwd=self.klasor, env=self._ortam(), capture_output=True, text=True
        )
        cikti = temizle((r.stdout + r.stderr).rstrip("\n"), self.klasor)
        if self.saat is not None and re.search(r"\bgit (commit|merge|revert)\b", komut):
            self.saat += datetime.timedelta(minutes=7)
        if beklenen_kod is not None and r.returncode != beklenen_kod:
            raise SystemExit(f"[{self.ders}/{self.ad}] beklenmeyen çıkış {r.returncode}: {komut}\n{cikti}")
        if goster:
            self.satirlar.append(f"$ {komut}")
            for s in cikti.splitlines():
                if gizle and re.search(gizle, s):
                    continue
                self.satirlar.append(s)
        self.son_kod = r.returncode
        return cikti

    def not_(self, metin):
        self.satirlar.append(f"# {metin}")

    def bos(self):
        self.satirlar.append("")

    def yaz(self, klasor=None):
        k = (klasor or EKRAN) / self.ders
        k.mkdir(parents=True, exist_ok=True)
        (k / f"{self.ad}.txt").write_text("\n".join(self.satirlar) + "\n", encoding="utf-8")
        return k / f"{self.ad}.txt"


def dosya(klasor, yol, icerik):
    """Çalışma klasörüne dosya yazar (öğrencinin düzenleyicide yaptığı değişiklik)."""
    p = pathlib.Path(klasor) / yol
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(icerik, encoding="utf-8")


CLAUDE_KAYIT = LAB / "claude-kosum"


def claude_kos(ders, ad, klasor, istem, araclar, zaman_asimi=900):
    """Claude Code'u başsız kipte (claude -p) gerçekten koşar; istem, yanıt, adım sayısı ve süre claude-kosum/<ders>-<ad>.json'a yazılır.
    Yalnız Claude Code kurulu makinede koşar (kursta: ekibin geliştirme makinesi). Ücret alanı kayda alınmaz."""
    r = subprocess.run(
        ["claude", "-p", istem, "--allowedTools", *araclar, "--output-format", "json"],
        cwd=klasor,
        capture_output=True,
        text=True,
        timeout=zaman_asimi,
        env=dict(os.environ, NO_COLOR="1"),
    )
    d = json.loads(r.stdout)
    surum = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.split()[0]
    k = {
        "ders": ders,
        "istem": istem,
        "izinli_araclar": list(araclar),
        "yanit": d.get("result"),
        "adim": d.get("num_turns"),
        "sure_s": round(d.get("duration_ms", 0) / 1000, 1),
        "hata": d.get("is_error"),
        "claude_code_surum": surum,
        "tarih": datetime.date.today().isoformat(),
    }
    CLAUDE_KAYIT.mkdir(exist_ok=True)
    (CLAUDE_KAYIT / f"{ders}-{ad}.json").write_text(json.dumps(k, ensure_ascii=False, indent=1))
    return k
