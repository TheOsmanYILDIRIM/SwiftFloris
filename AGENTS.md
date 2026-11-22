# Avenox fork policy

Bu depo `SysAdminDoc/SwiftFloris` upstream'inin hızlı hareket eden bir fork'udur. Amaç upstream'i yeniden yazmak değil, Avenox özelliklerini mümkün olan en ince ve yeniden uygulanabilir katman olarak taşımaktır.

## Upstream-first kuralı

- Upstream: `SysAdminDoc/SwiftFloris`, dal: `master`.
- Fork: `TheOsmanYILDIRIM/SwiftFloris`, dal: `master`.
- Upstream davranışını kopyalayan ikinci bir altyapı kurma. Mevcut SwiftFloris per-app profile, Smartbar, preference, editor ve test altyapılarını kullan.
- Geniş refactor yapma. Bir Avenox özelliği için upstream dosyasına dokunmak zorundaysan değişikliği küçük bir hook'a indir.
- Upstream'ten gelen güvenlik, gizlilik ve no-network garantilerini koru. `android.permission.INTERNET` ekleme.

## Avenox sahipliği

Yeni Avenox Kotlin kodunun varsayılan yeri:

`app/src/main/kotlin/dev/patrickgold/florisboard/avenox/`

Testlerin varsayılan yeri:

`app/src/test/kotlin/dev/patrickgold/florisboard/avenox/`

Avenox'a ait yeni kaynak dosyaları mümkün olduğunca `avenox_` öneki kullanır. Fork'a özel dokümanlar `docs/AVENOX_*`, workflow'lar `.github/workflows/avenox-*` altında yaşar.

Upstream'e ait mevcut bir dosya değiştirilecekse:

1. En küçük entegrasyon noktasını seç.
2. İlgili satırların yakınına `AVENOX-HOOK:<kisa-id>` işaretçisi koy.
3. `.avenox/overlay.json` içindeki `integration_points` listesine dosya + marker + gerekçe ekle.
4. Aynı işi ikinci bir paralel altyapıyla çözme.

`scripts/check-avenox-overlay.py` bu sınırı CI'da denetler.

## Upstream güncelleme modeli

`.github/workflows/avenox-upstream-sync.yml` upstream'i düzenli kontrol eder. Yeni commit varsa fork'un mevcut Avenox commit'lerinin üstüne merge eder, overlay guard + Android test/build kapısından geçirir ve yalnız başarılıysa `master` dalına gönderir. Merge çatışması veya test hatası otomatik olarak master'a yazılmaz.

Bu nedenle upstream kodunu vendor/kopya olarak Avenox klasörüne taşıma; merge'in çözmesi gereken değişikliği saklamış olursun.

## Avenox Keyboard ürün yönü

Prompt/mod özelliği geliştirilirken mevcut per-app profile altyapısı uygulama tanıma için yeniden kullanılmalı. Hedef yüzeyler:

- uygulama bazlı otomatik mod,
- kullanıcı düzenlenebilir hızlı cevap/node'lar,
- prefix / suffix / wrapper prompt enjeksiyonu,
- normal gönder / Avenox gönder ayrımı,
- Smartbar üzerinden hızlı mod değiştirme.

Kullanıcı promptları cihazda kalır; ağ tabanlı ek servis bu özellik için zorunlu değildir.

## Tamamlanma kapısı

Kod değişikliğinde en az:

```bash
python3 scripts/check-avenox-overlay.py --upstream-ref upstream/master
./gradlew :app:verifyNoInternetPermission :app:testDebugUnitTest :app:assembleDebug
```

çalışmalıdır. CI başarısı gerçek Android cihaz testinin yerine geçmez. UI/IME davranışı değiştiyse gerçek cihaz sonucu ayrıca doğrulanır.

Force-push, upstream geçmişini yeniden yazma veya test/güvenlik kapılarını zayıflatma yok.
