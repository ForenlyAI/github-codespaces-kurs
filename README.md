# GitHub ve Codespaces ile Yazılım Geliştirme · kurs deposu

Forenly AI Academy kursunun öğrenci dosyaları. Kurs boyunca küçük bir fırının günlük sipariş özetini çıkaran
komut satırı aracı üzerinde çalışırsınız: önce yerelde Git, sonra GitHub'da issue ve pull request, sonra
Codespaces'te kod olarak tanımlanmış geliştirme ortamı, en sonda GitHub Actions ile sürekli bütünleştirme.

Fırın siparişleri ve KDV oranları **ÖRNEK** veridir.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ForenlyAI/github-codespaces-kurs)

## Depoda ne var

| Yol | Ne işe yarar |
| --- | --- |
| `siparis_ozeti/` | araç: `python -m siparis_ozeti veri/siparisler.csv --tarih 2026-10-06` |
| `tests/` | pytest testleri |
| `veri/siparisler.csv` | ÖRNEK sipariş verisi (15 satır, 3 gün) |
| `.devcontainer/devcontainer.json` | Codespaces ortamı: Python 3.12, gh, Claude Code, testler için paketler |
| `.github/workflows/ci.yml` | her PR'da ruff + pytest, Python 3.11 / 3.12 / 3.13 |
| `.github/dependabot.yml` | haftalık bağımlılık güncelleme önerisi |
| `.github/pull_request_template.md` · `ISSUE_TEMPLATE/` | PR ve hata bildirimi şablonları |
| `alistirmalar/hafta1.py` | Hafta 1 alıştırması: yerel Git geçmişini sıfırdan kurar (internet gerekmez) |
| `beklenen/` | alıştırmaların ve aracın beklenen çıktıları |
| `kontrol.py` | bitirme denetimi (RUBRIK.md ölçütleri) |
| `RUBRIK.md` | bitirme işinin ölçütleri |

## Başlamak

**Codespaces ile (önerilen):** yukarıdaki düğme ya da `gh codespace create -R <sizin-deponuz> -m basicLinux32gb --idle-timeout 10m`.
Ortam açıldığında paketler kendiliğinden kurulur. Terminalde:

```bash
python -m pytest -q
python -m siparis_ozeti veri/siparisler.csv
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
gh repo create siparis-ozeti --public --template ForenlyAI/github-codespaces-kurs --clone
```

Depo herkese açık olmalı: ücretsiz planda dal koruma kuralı yalnız herkese açık depolarda açılır.

## Hafta 1 alıştırması

```bash
python alistirmalar/hafta1.py      # alistirmalar/calisma/siparis-ozeti klasöründe 12 commit'lik geçmişi kurar
python kontrol.py --hafta1          # çıktınızı beklenen/alistirmalar ile karşılaştırır
```

Yazar adı ve commit saatleri sabit olduğu için commit kimlikleri (ör. `c6d9533`) sizde de aynı çıkar.

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
