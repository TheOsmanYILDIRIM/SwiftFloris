# Avenox upstream strategy

SwiftFloris hızlı ve agentic bir upstream olduğu için bu fork klasik "uzun yaşayan çatallı ürün" gibi yönetilmez. `master`, upstream'e mümkün olduğunca yakın tutulur; Avenox özellikleri ince bir overlay olarak eklenir.

## Neden patch dosyası kuyruğu değil?

Ham `.patch` dosyaları kodu ikinci kez depolar ve upstream sık değiştiğinde bağlamı hızla eskir. Bunun yerine Git'in kendi merge geçmişi + izole Avenox kaynakları + açık entegrasyon noktaları kullanılır. Sonuç aynı hedefi daha az kopyayla sağlar:

1. upstream kodu tek kaynak kalır,
2. Avenox kodu ayrı namespace'te yaşar,
3. upstream dosyasına gereken küçük hook'lar manifestte kayıtlıdır,
4. otomatik sync yeni upstream'i merge eder,
5. guard ve Android test/build geçmeden `master` ilerlemez.

## Dosya sahipliği

`.avenox/overlay.json` iki tür fork değişikliği tanımlar:

- `owned_prefixes` / `owned_files`: upstream'ten bağımsız Avenox dosyaları,
- `integration_points`: upstream dosyasındaki zorunlu küçük hook'lar.

Bir upstream dosyasına yeni dokunuş yapılacaksa `AVENOX-HOOK:<id>` marker'ı ve manifest kaydı zorunludur. Böylece upstream değişikliğinin bizim entegrasyon yüzeyine temas edip etmediği makine tarafından görülebilir.

## Otomatik güncelleme

`avenox-upstream-sync.yml` dört saatte bir ve elle tetiklenebilir şekilde çalışır.

Yeni upstream commit yoksa hiçbir şey yapmaz. Varsa:

1. `upstream/master` fetch edilir,
2. mevcut fork `master` üzerine normal Git merge uygulanır,
3. çatışma varsa işlem durur ve master değişmez,
4. overlay guard çalışır,
5. no-network doğrulaması, debug unit testleri ve debug APK build çalışır,
6. yalnız hepsi geçerse merge commit fork `master` dalına push edilir,
7. doğrulanan debug APK workflow artifact olarak saklanır.

Bu model upstream'in küçük ve orta değişikliklerini insan müdahalesi olmadan alır. Gerçek semantik çatışma olduğunda otomasyon kod uydurmak yerine kırmızıya düşer; bir sonraki Avenox geliştirme oturumu yalnız o entegrasyon noktasını günceller.

## Avenox Keyboard özellikleri

Prompt enjeksiyonu ve hızlı AI kontrollerinde mevcut SwiftFloris yapılarını yeniden kullanma önceliklidir:

- uygulama tanıma: mevcut per-app keyboard profiles,
- toolbar: mevcut Smartbar / quick action altyapısı,
- kalıcı ayarlar: mevcut preference altyapısı,
- yazı ekleme: mevcut editor/InputConnection katmanı.

Yeni çekirdek mantık `dev.patrickgold.florisboard.avenox` altında tutulur. Bu sayede SwiftFloris'in prediction, glide, clipboard ve tema motorları upstream'den güncel kalmaya devam eder.
