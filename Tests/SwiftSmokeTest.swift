import Foundation

@main
struct SwiftSmokeTest {
    static func main() {
        let analyzer = SMSAnalyzer(bundle: .main)
        let tests: [(String, SMSRecommendation)] = [
            ("1000 TL yatır casino slot bonusu kazan hemen", .junk),
            ("Hesabınız bloke edildi. Acilen linke tıklayıp şifrenizi girin.", .junk),
            ("Mağazamızda yüzde 50 indirim kampanyası başladı.", .promotion),
            ("Giriş doğrulama kodunuz 483921. Kimseyle paylaşmayın.", .allow),
            ("Kargonuz bugün dağıtıma çıkarılmıştır.", .allow),
            ("Merhaba akşam eve gelince haber ver.", .allow),
        ]
        var failed = 0
        for (message, expected) in tests {
            let predicted = analyzer.analyze(message)
            print("\(predicted.category.rawValue): \(predicted.recommendation.rawValue) [%\(Int(predicted.probability*100))] - \(message)")
            if predicted.recommendation != expected { failed += 1 }
        }
        if failed > 0 { fputs("\(failed) smoke tests failed\n", stderr); exit(1) }
    }
}
