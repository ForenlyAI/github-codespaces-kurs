# Bitirme işi · ölçüt çizelgesi

**İş:** Bu şablondan açtığınız kendi herkese açık deponuzda vardiya raporu aracına bir özellik eklersiniz
(örnek: saat dilimine göre görev sayısı, iki görev arasındaki boş bekleme süresi, en sık hata kodunun görev listesi). İş, geliştirme
ortamı kod olarak tanımlı, CI'si yeşil, ana dalı korumalı ve en az bir incelenmiş PR ile birleşmiş olarak teslim edilir.

Teslim: depo adresi + `python kontrol.py --github` çıktısı.

| # | Ölçüt | Yeterli | Eksik |
| --- | --- | --- | --- |
| 1 | **Geliştirme ortamı kod olarak** | `.devcontainer/devcontainer.json` depoda; Codespace bu dosyayla açılıyor ve içinde `python -m pytest -q` geçiyor | dosya yok, JSON bozuk ya da Codespace'te testler koşmuyor |
| 2 | **Sürekli bütünleştirme** | her PR'da ve ana dala gönderimde ruff + pytest koşan iş akışı; en az iki Python sürümü (matris); ana dalın son koşusu yeşil | iş akışı yok, yalnız elle koşuluyor ya da son koşu kırmızı |
| 3 | **Korumalı ana dal** | `main` için kural: birleştirmeden önce PR zorunlu, CI kontrolü zorunlu, zorla gönderme ve dal silme kapalı | kural yok ya da ana dala doğrudan gönderme mümkün |
| 4 | **İncelenmiş PR** | issue açıldı; PR açıklamasında `Closes #<no>`; PR'da en az bir inceleme yorumu ve yanıtı; CI yeşilken birleşti; issue kapandı | PR yok, inceleme yorumu yok ya da CI kırmızıyken birleşti |
| 5 | **Yapay zekâ beyanı ve doğrulama** | yapay zekâ kullandıysanız PR şablonundaki bölüm dolu: hangi araç, hangi kısım ve nasıl doğrulandı (test, elle deneme) | yapay zekâ çıktısı doğrulama adımı yazılmadan birleşmiş |

1–4 numaralı ölçütlerin hepsi yeterli olmalı; yapay zekâ kullandıysanız 5. ölçüt de. Eksik ölçütü düzeltip yeniden teslim edersiniz.
