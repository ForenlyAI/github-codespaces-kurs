# GitHub ve Codespaces ile Yazılım Geliştirme · kurs deposu

Forenly AI Academy kursunun öğrenci dosyaları. Kurs boyunca kafede çay servisi yapan bir insansı robotun görev
kayıtlarından vardiya raporu çıkaran komut satırı aracı üzerinde çalışırsınız: önce yerelde Git, sonra GitHub'da issue ve pull request, sonra
Codespaces'te kod olarak tanımlanmış geliştirme ortamı, en sonda GitHub Actions ile sürekli bütünleştirme.

Görev kaydı **ÖRNEK** veridir (üretildi; servis süreleri bir çay servisinin benzetim kaydındaki süresinden esinlendi).

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ForenlyAI/github-codespaces-kurs)

## Depoda ne var

| Yol | Ne işe yarar |
| --- | --- |
| `vardiya_raporu/` | araç: `python -m vardiya_raporu veri/gorevler.jsonl --tur servis` |
| `tests/` | pytest testleri |
| `veri/gorevler.jsonl` | ÖRNEK görev kaydı (22 görev: servis, toplama, şarj; JSON Lines) |
| `.devcontainer/devcontainer.json` | Codespaces ortamı: Python 3.12, gh, Claude Code, testler için paketler |
| `.github/workflows/ci.yml` | her PR'da ruff + pytest, Python 3.11 / 3.12 / 3.13 |
| `.github/dependabot.yml` | haftalık bağımlılık güncelleme önerisi |
| `.github/pull_request_template.md` · `ISSUE_TEMPLATE/` | PR ve hata bildirimi şablonları |
| `alistirmalar/hafta1.py` | Hafta 1 alıştırması: yerel Git geçmişini sıfırdan kurar (internet gerekmez) |
| `beklenen/` | alıştırmaların ve aracın beklenen çıktıları; `beklenen/kosum-kayitlari/` Hafta 2–4'ün gerçek koşum kayıtları (gh, Codespaces, Actions) |
| `kontrol.py` | bitirme denetimi (RUBRIK.md ölçütleri) |
| `RUBRIK.md` | bitirme işinin ölçütleri |

## Rapor ne söylüyor

```
$ python -m vardiya_raporu veri/gorevler.jsonl
Vardiya raporu: bütün görevler
Görev: 22 (iş görevi 20)
Başarı: %80,0 (16 / 20)
Ortalama süre: 151,2 sn
En uzun görev: G015 (262,0 sn)
Hatalar: E21-bardak-kaydi × 2, E07-yol-kapali × 2
Şarj payı: %51,2
```

Başarı oranı yalnız iş görevlerinden (servis + toplama) hesaplanır; şarj iş görevi sayılmaz. Şarj payı, şarjda geçen
sürenin bütün görev süresine oranıdır.

## Başlamak

**Codespaces ile (önerilen):** yukarıdaki düğme ya da `gh codespace create -R <sizin-deponuz> -m basicLinux32gb --idle-timeout 10m`.
Ortam açıldığında paketler kendiliğinden kurulur. Terminalde:

```bash
python -m pytest -q
python -m vardiya_raporu veri/gorevler.jsonl
```

**Kendi bilgisayarınızda:** Python 3.11 ya da üstü ve Git yeterli.

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -q
```

## Kendi deponuzu açmak (bitirme için)

Bu depo şablondur. GitHub'da **Use this template** düğmesiyle ya da:

```bash
gh repo create vardiya-raporu --public --template ForenlyAI/github-codespaces-kurs --clone
```

Depo herkese açık olmalı: ücretsiz planda dal koruma kuralı yalnız herkese açık depolarda açılır.

## Hafta 1 alıştırması

```bash
python alistirmalar/hafta1.py      # alistirmalar/calisma/vardiya-raporu klasöründe 12 commit'lik geçmişi kurar
python kontrol.py --hafta1          # çıktınızı beklenen/alistirmalar ile karşılaştırır
```

Yazar adı ve commit saatleri sabit olduğu için commit kimlikleri (ör. `91bdf02`) sizde de aynı çıkar.

## Hafta 2–4 kayıtları

Bu haftaların işleri sizin GitHub hesabınızda yapılır, bu yüzden çıktınız birebir aynı olmaz (issue ve PR numaraları,
koşu kimlikleri, süreler). `beklenen/kosum-kayitlari/<ders>/` altındaki kayıtlar kursu hazırlarken gerçekten koşulan
komutlardır: aynı komutları kendi deponuzda koşun ve sonucun türünü (geçti / reddedildi / kaldı) karşılaştırın.

## Bitirme denetimi

```bash
python kontrol.py             # dosyalar + testler
python kontrol.py --github    # + korumalı ana dal, incelenmiş PR, yeşil CI (gh auth login gerekir)
```

## Maliyet notları (Ekim 2026)

- **Codespaces:** ücretsiz kişisel hesapta ayda 120 çekirdek-saat ve 15 GB depolama ücretsizdir. İki çekirdekli makine
  saatte iki çekirdek-saat sayılır. İşiniz bitince Codespace'i silin: `gh codespace delete -c <ad>`.
- **Actions:** herkese açık depoda standart çalıştırıcılar ücretsizdir; gizli depoda ayda 2.000 dakika ücretsizdir.
- **Copilot:** ücretsiz plan sınırlıdır; pull request kod incelemesi ve bulut ajanı ücretli planlardadır. Kurs Copilot gerektirmez.
- **Claude Code:** kendi Anthropic hesabınızla çalışır. Codespace'te kullanmak için anahtarı dosyaya değil
  Codespaces gizli değişkenine (`ANTHROPIC_API_KEY`) koyun.

## Yapay zekâ beyanı

Kursta Claude Code bir yardımcı olarak kullanılır: çakışma çözümü, PR incelemesi, `devcontainer.json` ve test yazımı.
Her yapay zekâ çıktısı test, `git diff` ve CI ile doğrulanır; doğrulanmayan öneri birleştirilmez.
Ders anlatım metinleri ve seslendirme yapay zekâ yardımıyla üretilmiştir.
