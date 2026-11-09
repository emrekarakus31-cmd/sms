# NOVA SMS Shield AI — iOS v0.1 (Türkçe)

**Durum:** İlk kaynak kod sürümü / prototip. Model ve Swift analiz motoru test edildi. **Tam iOS derlemesi ve fiziksel cihaz testi yapılmadı** (bu çalışma ortamında Xcode yok).

## Neler var?

- iOS SwiftUI uygulaması: SMS örnekleri ve elle metin girerek AI sonuçlarını deneme.
- Apple `IdentityLookup` Message Filter Extension: sistem uygun bir SMS filtreleme isteği ilettiğinde gerçek mesajı yerel modelle sınıflandırıp `.allow`, `.promotion`, `.junk` yanıtı verme.
- Gerçek bir **küçük, çevrimdışı, eğitilmiş doğrusal metin sınıflandırıcısı**: `Shared/sms_model.json` (yaklaşık 217 KB), Python tarafında Logistic Regression ile **1.818 sentetik örnek** üzerinde eğitildi. Model çalışırken Python, Core ML, internete erişim veya sunucu gerekmez. Swift kodu modelin ağırlıklarını kullanarak tahmin hesaplar.
- 7 sınıf: normal, doğrulama kodu, banka, kargo, reklam, bahis, dolandırıcılık.
- Temkinli filtreleme: AI kararı **tek başına** yeterli sayılmaz. Riskli sınıf ve belirgin işaretler birlikte gerektiğinde filtrelenir. Doğrulama kodlarını koruyucu kontrol içerir.
- Mesaj saklama / analiz günlükleri / ağ trafiği **yoktur**.

> **Önemli:** Eğitim verileri sentetiktir; gerçek dünya doğruluğu ve tüm cihaz/iOS uyumluluğu kanıtlanmış değildir. İlk sürümü güvenilir filtre olarak kullanmadan önce çok daha geniş veri, insan denetimli test ve yanlış-pozitif oranı değerlendirmesi gerekir. Örnek ekranındaki yüzde, *kalibre edilmiş gerçek doğruluk oranı değil*, modelin tahmin puanıdır. Bu sürüm test amaçlıdır.

## iPhone'a kurulum

1. **Mac ile:** Güncel Xcode üzerinde doğrudan kurabilirsiniz. **Mac yoksa:** Aşağıdaki GitHub Actions + Windows Sideloadly yoluyla önce bulutta imzasız IPA oluşturabilirsiniz. Sideloadly kaynak Swift dosyalarını doğrudan derlemez.
2. `NOVA-SMS-Shield-AI.xcodeproj` dosyasını açın.
3. Xcode'da soldaki proje adını tıklayın; **iki target** göreceksiniz: `NOVASMSShieldAI` ve `MessageFilter`.
4. **İki target** için Signing & Capabilities bölümünde kendi Apple hesabınızın **Team** bilgisini seçin. `Bundle Identifier` alanlarını size özel ve birbiriyle eşleşecek şekilde değiştirin; örneğin `com.ornek.novasmsshield` ile `com.ornek.novasmsshield.MessageFilter`.
5. Çalıştırılacak şemayı `NOVASMSShieldAI` seçip iPhone'u hedef gösterin. `Product > Run` ile yükleyin. Gerekirse cihazda Geliştirici Modu ve geliştiriciye güvenme ayarlarını açın.
6. Önce uygulamadaki **SMS test alanı** ile analiz sonuçlarını deneyin.
7. Filtreyi etkinleştirmek için iOS sürümüne göre **Mesajlar > Filtreler > Filtrelemeyi Yönet > Bilinmeyen Gönderenler / Metin Mesajı Filtresi** yolunu ya da **Ayarlar > Uygulamalar > Mesajlar > Bilinmeyenler ve İstenmeyenler** yolunu izleyin. `NOVA SMS Shield` filtresini seçin. Menü adları iOS sürümü ve dile göre değişir.
8. **Gerçek cihazda**, test kontrolünüzdeki bilinmeyen bir numaradan SMS göndererek sonucun Mesajlar içindeki ilgili kategoriye ayrılıp ayrılmadığını sınayın. Uygulama içindeki test ekranı sistem uzantısını **tetiklemez**; yalnızca aynı analiz kodunu dener.

Apple docs: [Message Filter App Extension](https://developer.apple.com/documentation/identitylookup/creating-a-message-filter-app-extension), [Apple Mesaj filtreleri](https://support.apple.com/en-ie/guide/iphone/iph203ab0be4/27/ios/27).

## Sınırlamalar

- `IdentityLookup` filtreleme uzantısı bilinmeyen göndericilerden gelen, Apple tarafından uygun görülen SMS/MMS/RCS içerikleri için çağrılır; **iMessage, kişilerde kayıtlı ve artık bilinen sayılan göndericiler** bu yolla filtrelenemez.
- Mesajlar SMS ağına ulaşmadan engellenmez, silinmez; Apple'ın uygun gelen kutusuna/İstenmeyenler alanına ayrılması istenir.
- Apple uzantısı gelen kutusundaki geçmiş tüm SMS'leri tarayamaz.
- Filtreyi kullanıcı iOS ayarlarından etkinleştirmelidir. Aynı anda sadece bir üçüncü taraf filtre seçilebilir.
- Yalnızca **iPhone 16 Pro Max'te test/filtre açılması**, SIM'i iPhone 7'de olan ve başka telefona iletilen SMS'lerin kesinlikle filtreleneceğini **garanti etmez**. Test etmek gerekir. Ayrıca bu proje için minimum iOS 16 seçildiğinden iPhone 7'ye yüklenmez (iPhone 7 iOS 16 desteklemez). İleride iPhone 7 için iOS 15'e uyarlama gerekebilir.
- Yapay zekâ kullanılır ama bu bir LLM/sohbet botu değildir; küçük öğrenilmiş metin sınıflandırıcısıdır. Gerçek dünya sonuçları düzenli test edilmeden yeterli sayılmaz.
- Bu sürümde özel kelime listesi, model güncellemeleri, filtre geçmişi, uzaktan güncelleme veya ana uygulamayla paylaşılan tercihler yoktur. Çünkü bunlar için ayrı ayar paylaşımı/test gerekir.

## Proje yapısı

```
NOVA-SMS-Shield-AI.xcodeproj/       Xcode projesi (uygulama + uzantı)
NOVA-SMS-Shield-AI/
  NOVASMSShieldAIApp.swift           Uygulama giriş noktası
  ContentView.swift                  SwiftUI test ve bilgilendirme ekranı
  Info.plist
MessageFilter/
  MessageFilterExtension.swift       Apple SMS filtreleme uzantısı
  Info.plist
Shared/
  SMSAnalyzer.swift                  AI çıkarımı + koruyucu karar mekanizması
  sms_model.json                     217 KB eğitilmiş model, iki target'a dahil
Tools/
  train_model.py                     Sentetik veriler ve yeniden eğitim (isteğe bağlı)
  make_xcodeproj.py                  Xcode proje dosyasını yeniden üretir
Tests/
  SwiftSmokeTest.swift               Temel doğruluk / emniyet testleri
```

## Modeli yeniden eğitme (isteğe bağlı, bilgisayarda)

`python -m pip install scikit-learn` ardından `python Tools/train_model.py`. Model eğitimi **iPhone üzerinde yapılmaz**; iPhone yalnızca `sms_model.json` dosyasındaki öğrenilmiş ağırlıklarla çıkarım yapar. Gerçek kullanıcı SMS'lerini kullanacaksanız açık rıza, hassas verilerin anonimleştirilmesi ve yeterli veri koruma süreçleri gerekir.

Swift motorunun iOS dışında hızlı test edilmesi (macOS/Linux, Swift kuruluysa):

```
swiftc Shared/SMSAnalyzer.swift Tests/SwiftSmokeTest.swift -o Tests/nova_smoketest
cp Shared/sms_model.json Tests/sms_model.json
Tests/nova_smoketest
```

## Güvenlik yaklaşımı

Her şey cihazda analiz edilir; kullanıcı SMS içeriği günlüklenmez. Boş SMS veya model yükleme hatasında **fail-open** (`allow`) kullanılır. AI tahmini yanlış olabilir, bu nedenle otomatik İstenmeyenler kararı için ek bağlamsal kanıt aranır. Özellikle OTP mesajları `allow` olarak korunur. Mutlak dolandırıcılık tespiti veya yanlış pozitif sıfır garantisi **yoktur**.


## Windows kullanıcısı için: Mac olmadan IPA oluşturma (GitHub Actions)

Projenin bu dağıtımında `.github/workflows/build-ipa.yml` ve paylaşılmış Xcode şeması bulunmaktadır. GitHub'ın macOS derleme bilgisayarı iOS uygulamasını oluşturur. **Yerel Windows üzerinde Xcode çalışmaz.**

1. GitHub'da **yeni bir depo** oluşturun. Model dosyası ve kaynak kodlarıyla birlikte bu ZIP'in içindeki `NOVA-SMS-Shield-AI` klasörünün **içeriğini** (özellikle gizli `.github` klasörü dahil) depo köküne yükleyin. `.github` klasörü eksikse iş akışı görünmez. Windows için GitHub Desktop veya `git` kullanabilirsiniz.
2. Deponun **Actions** sekmesinde `NOVA SMS Shield AI - iOS IPA` iş akışını açın, `Run workflow` düğmesine basın.
3. Başarılı çalışmanın **Artifacts** bölümünden `NOVA-SMS-Shield-AI-unsigned-IPA` dosyasını indirin; ZIP'i çıkarın, içindeki `.ipa` dosyasını alın.
4. Windows'ta [Sideloadly](https://sideloadly.io/) uygulamasını açın, iPhone'u USB ile bağlayın. `.ipa` dosyasını seçin ve kendi Apple hesabınızla cihaz için **yeniden imzalayıp** yükleyin. **Remove Extensions** seçeneğini kullanmayın: SMS filtreleme uzantısı kalmalı.
5. Kurulum başarılıysa iPhone'da uygulamanın test arayüzünü açın. Ardından Ayarlar > Uygulamalar > Mesajlar > Bilinmeyenler ve İstenmeyenler bölümünden filtreyi etkinleştirmeyi deneyin (adlar iOS sürümüne göre değişir).

**Sınırlar / dürüst uyarılar:** İş akışı *unsigned* (imzasız) IPA üretir, doğrudan kurulabilir IPA üretmez. Sideloadly'nin uzantıyı doğru yeniden imzalaması ve iOS'un uzantıyı tanıması **henüz cihazda doğrulanmadı**. Başarısız bir derleme durumunda GitHub Actions hata günlüğü gerekir. Ücretsiz Apple ID ile Sideloadly yüklemeleri genelde 7 günde bir yeniden imzalanır; uygulama çalışmadığı dönemde filtre de çalışmaz. GitHub'ın özel depolarında macOS Actions kullanımı kota/ücretlendirmeye tabi olabilir. Güvenlik için repo özel tutulabilir, fakat kota durumunu kontrol edin. GitHub'a Apple hesabı parolanızı **yüklemeyin**; GitHub derlemesi Apple hesabı gerektirmez.

Kaynaklar: https://docs.github.com/en/actions/reference/runners/github-hosted-runners ve https://sideloadly.io/
