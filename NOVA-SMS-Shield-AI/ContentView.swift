import SwiftUI

private struct DemoSMS {
    let title: String
    let message: String
    static let examples: [DemoSMS] = [
        .init(title: "Bahis", message: "1000 TL yatır, casino slot oyunlarında bonus kazan!"),
        .init(title: "Doğrulama", message: "Hesabınıza giriş için doğrulama kodunuz 583291. Kimseyle paylaşmayın."),
        .init(title: "Kargo", message: "Siparişiniz kargoya verildi. Bugün teslim edilecek."),
        .init(title: "Dolandırıcılık", message: "Hesabınız bloke edildi. Acilen linke tıklayıp şifrenizi girin."),
        .init(title: "Reklam", message: "Mağazamızda yüzde 50 indirim kampanyası başladı. Fırsatı kaçırmayın!"),
    ]
}

struct ContentView: View {
    @State private var bodyText = "1000 TL yatır, casino slot oyunlarında bonus kazan!"
    @State private var result: SMSAssessment?
    private let analyzer = SMSAnalyzer(bundle: .main)
    private let background = Color(red: 0.055, green: 0.074, blue: 0.12)
    private let panel = Color(red: 0.095, green: 0.12, blue: 0.19)
    private let highlight = Color(red: 0.4, green: 0.85, blue: 0.84)

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    header
                    infoPanel
                    testPanel
                    if let result = result { assessmentPanel(result) }
                    instructionsPanel
                    privacyPanel
                }
                .padding(20)
                .frame(maxWidth: 650)
                .frame(maxWidth: .infinity)
            }
            .background(background.ignoresSafeArea())
            .toolbar(.hidden, for: .navigationBar)
            .preferredColorScheme(.dark)
        }
        .onAppear { if result == nil { analyzeText() } }
    }

    private var header: some View {
        HStack(spacing: 14) {
            Image(systemName: "shield.lefthalf.filled")
                .font(.system(size: 34, weight: .medium))
                .foregroundStyle(highlight)
                .frame(width: 66, height: 66)
                .background(highlight.opacity(0.12), in: RoundedRectangle(cornerRadius: 19))
            VStack(alignment: .leading, spacing: 4) {
                Text("NOVA SMS SHIELD")
                    .font(.system(size: 20, weight: .black, design: .rounded))
                Text("AI  •  Yerel koruma  •  v0.1")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundStyle(.white.opacity(0.62))
            }
            Spacer(minLength: 0)
        }
        .padding(.top, 18)
    }

    private var infoPanel: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("Mini AI hazır", systemImage: "brain.head.profile")
                .font(.headline)
                .foregroundStyle(highlight)
            Text("7 mesaj türünü cihaz içinde sınıflandırır. İnternet, hesap veya ücretli AI servisi gerekmez.")
                .font(.subheadline)
                .foregroundStyle(.white.opacity(0.8))
            Text("İlk eğitim verileri sentetiktir. Gerçek mesajlarda kusursuz tespit garanti edilmez.")
                .font(.caption)
                .foregroundStyle(.white.opacity(0.56))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(18)
        .background(panel, in: RoundedRectangle(cornerRadius: 20))
    }

    private var testPanel: some View {
        VStack(alignment: .leading, spacing: 14) {
            Label("SMS test alanı", systemImage: "text.bubble")
                .font(.headline)
            Text("Mesajı yaz veya örneklerden birini seç. Gerçek SMS kutun burada okunmaz.")
                .font(.caption)
                .foregroundStyle(.white.opacity(0.65))
            TextEditor(text: $bodyText)
                .scrollContentBackground(.hidden)
                .font(.body)
                .frame(minHeight: 126)
                .padding(9)
                .background(background, in: RoundedRectangle(cornerRadius: 13))
                .accessibilityLabel("Test SMS metni")
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(DemoSMS.examples, id: \.title) { demo in
                        Button(demo.title) {
                            bodyText = demo.message
                            analyzeText()
                        }
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.white)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(.white.opacity(0.10), in: Capsule())
                    }
                }
            }
            Button(action: analyzeText) {
                Label("AI ile analiz et", systemImage: "sparkles")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 13)
            }
            .buttonStyle(.plain)
            .foregroundStyle(.black)
            .background(highlight, in: RoundedRectangle(cornerRadius: 13))
        }
        .padding(18)
        .background(panel, in: RoundedRectangle(cornerRadius: 20))
    }

    private func assessmentPanel(_ assessment: SMSAssessment) -> some View {
        let color: Color = assessment.recommendation == .junk ? .red :
            (assessment.recommendation == .promotion ? .orange : highlight)
        return VStack(alignment: .leading, spacing: 13) {
            HStack(spacing: 10) {
                Image(systemName: assessment.category.symbol)
                    .font(.title2)
                    .foregroundStyle(color)
                VStack(alignment: .leading, spacing: 3) {
                    Text(assessment.category.title).font(.headline)
                    Text("AI tahmin puanı: %\(Int((assessment.probability * 100).rounded()))")
                        .font(.caption)
                        .foregroundStyle(.white.opacity(0.6))
                }
                Spacer()
            }
            Divider().overlay(.white.opacity(0.06))
            HStack(spacing: 8) {
                Circle().fill(color).frame(width: 8, height: 8)
                Text(assessment.recommendation.title).font(.subheadline.weight(.semibold))
            }
            Text(assessment.explanation)
                .font(.caption)
                .foregroundStyle(.white.opacity(0.7))
            Text("Tahmin puanı, gerçek dünyadaki doğruluk oranı değildir.")
                .font(.caption2)
                .foregroundStyle(.white.opacity(0.5))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(18)
        .background(panel, in: RoundedRectangle(cornerRadius: 20))
    }

    private var instructionsPanel: some View {
        VStack(alignment: .leading, spacing: 10) {
            Label("SMS filtresini etkinleştir", systemImage: "gearshape.2.fill")
                .font(.headline)
            Text("Mesajlar → Filtreler → Filtrelemeyi Yönet → Bilinmeyen Gönderenleri Filtrele → Metin Mesajı Filtresi → NOVA SMS Shield AI.")
                .font(.subheadline)
            Text("iOS sürümüne göre menü adları değişebilir. Tek seferde yalnızca bir üçüncü taraf SMS filtresi etkin olabilir.")
                .font(.caption)
                .foregroundStyle(.white.opacity(0.58))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(18)
        .background(panel, in: RoundedRectangle(cornerRadius: 20))
    }

    private var privacyPanel: some View {
        HStack(alignment: .top, spacing: 12) {
            Image(systemName: "lock.shield")
                .foregroundStyle(highlight)
            Text("Gelen mesajlar sunucuya gönderilmez. Analiz sonucu veya mesaj içeriği uygulamada kaydedilmez. iMessage ve bilinen göndericiler bu filtreye dahil değildir.")
                .font(.caption)
                .foregroundStyle(.white.opacity(0.65))
        }
        .padding(12)
    }

    private func analyzeText() {
        result = analyzer.analyze(bodyText)
    }
}
