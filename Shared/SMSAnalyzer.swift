import Foundation

// Shared by the iOS app and its IdentityLookup extension. No networking, no SMS logging.
enum SMSCategory: String, CaseIterable {
    case normal, verification, banking, delivery, advertising, gambling, scam

    var title: String {
        switch self {
        case .normal: return "Normal mesaj"
        case .verification: return "Doğrulama kodu"
        case .banking: return "Banka / finans"
        case .delivery: return "Sipariş / kargo"
        case .advertising: return "Reklam / kampanya"
        case .gambling: return "Bahis / casino"
        case .scam: return "Olası dolandırıcılık"
        }
    }
    var symbol: String {
        switch self {
        case .normal: return "bubble.left"
        case .verification: return "key.fill"
        case .banking: return "creditcard.fill"
        case .delivery: return "shippingbox.fill"
        case .advertising: return "tag.fill"
        case .gambling: return "exclamationmark.shield.fill"
        case .scam: return "hand.raised.fill"
        }
    }
}

enum SMSRecommendation: String {
    case allow, promotion, junk
    var title: String {
        switch self {
        case .allow: return "Normal gelen kutusu"
        case .promotion: return "Tanıtım olarak ayır"
        case .junk: return "İstenmeyenlere ayır"
        }
    }
}

struct SMSAssessment {
    let category: SMSCategory
    let probability: Double // Indicative model output; NOT a calibrated accuracy guarantee.
    let recommendation: SMSRecommendation
    let explanation: String
}

private struct LinearModelFile: Decodable {
    let labels: [String]
    let bias: [Double]
    let weights: [String: [Double]]
}

struct SMSAnalyzer {
    private let model: LinearModelFile?

    init(bundle: Bundle) {
        if let url = bundle.url(forResource: "sms_model", withExtension: "json"),
           let bytes = try? Data(contentsOf: url),
           let parsed = try? JSONDecoder().decode(LinearModelFile.self, from: bytes),
           parsed.bias.count == parsed.labels.count {
            self.model = parsed
        } else {
            self.model = nil
        }
    }

    private static func tokens(_ text: String) -> [String] {
        let lowered = text.lowercased(with: Locale(identifier: "tr_TR"))
            .replacingOccurrences(of: "ı", with: "i")
            .replacingOccurrences(of: "i\u{0307}", with: "i")
        let folded = lowered.folding(options: [.diacriticInsensitive],
                                     locale: Locale(identifier: "en_US_POSIX"))
        var cleaned = String()
        cleaned.reserveCapacity(folded.count)
        for scalar in folded.unicodeScalars {
            let value = scalar.value
            if (97...122).contains(value) || (48...57).contains(value) {
                cleaned.append(Character(scalar))
            } else {
                cleaned.append(" ")
            }
        }
        return cleaned.split(separator: " ").map(String.init)
    }

    private static func features(from tokens: [String]) -> Set<String> {
        var result = Set<String>()
        for token in tokens {
            result.insert("w:" + token)
            let chars = Array("^" + token + "$")
            for length in [3, 4] where chars.count >= length {
                for start in 0...(chars.count - length) {
                    result.insert("c:" + String(chars[start..<(start + length)]))
                }
            }
        }
        if tokens.count >= 2 {
            for index in 0..<(tokens.count - 1) {
                result.insert("b:" + tokens[index] + "_" + tokens[index + 1])
            }
        }
        return result
    }

    func analyze(_ message: String) -> SMSAssessment {
        let words = Self.tokens(message)
        guard !words.isEmpty else {
            return SMSAssessment(category: .normal, probability: 0,
                                 recommendation: .allow, explanation: "Boş mesaj filtrelenmez.")
        }
        // Fail open: missing/unreadable model must NEVER flag messages as spam.
        guard let model = model else {
            return SMSAssessment(category: .normal, probability: 0,
                                 recommendation: .allow, explanation: "AI modeli bulunamadı; mesaj korunarak geçirildi.")
        }
        var logits = model.bias
        for feature in Self.features(from: words) {
            guard let weights = model.weights[feature], weights.count == logits.count else { continue }
            for index in logits.indices { logits[index] += weights[index] }
        }
        guard let maximum = logits.max() else {
            return SMSAssessment(category: .normal, probability: 0,
                                 recommendation: .allow, explanation: "Yetersiz veri.")
        }
        let exponentials = logits.map { exp($0 - maximum) }
        let total = exponentials.reduce(0, +)
        guard total > 0,
              let winner = logits.indices.max(by: { logits[$0] < logits[$1] }),
              let category = SMSCategory(rawValue: model.labels[winner]) else {
            return SMSAssessment(category: .normal, probability: 0,
                                 recommendation: .allow, explanation: "Model tahmini geçersiz.")
        }
        let confidence = exponentials[winner] / total
        let normalized = words.joined(separator: " ")
        let has = { (phrases: [String]) in phrases.contains { normalized.contains($0) } }
        let hasURL = has(["http", "www", "bit ly", "tinyurl", "linke", "baglanti", "tikla"])

        // Conservative safety rules. AI confidence alone is NOT enough to divert a message.
        let hasOTPContext = has(["dogrulama", "tek kullanimlik", "giris kod", "onay kod", "otp", "guvenlik kod", "sifre"])
        let hasShortCode = words.contains { word in
            (4...8).contains(word.count) && word.allSatisfy(\.isNumber)
        }
        if hasOTPContext && hasShortCode {
            return SMSAssessment(category: .verification, probability: confidence,
                                 recommendation: .allow,
                                 explanation: "Doğrulama kodlarını yanlışlıkla gizlememek için normal gelen kutusuna bırakıldı.")
        }

        let gamblingEvidence = has(["bahis", "casino", "slot", "jackpot", "cevrim sartsiz", "bahis oran", "deneme bonusu"])
        if category == .gambling && confidence >= 0.80 && gamblingEvidence {
            return SMSAssessment(category: category, probability: confidence,
                                 recommendation: .junk, explanation: "AI tahmini ve bahis göstergeleri örtüşüyor.")
        }
        let accountThreat = has(["hesabiniz bloke", "hesabiniz aski", "hesabiniz kap", "kartinizi kullanima ac", "icra dosya", "mahkeme dosya", "kimlik bilgilerinizi", "sifrenizi gir", "odeme yapmazsaniz", "ek ucret"])
        let urgency = has(["hemen", "acil", "son uyari", "tikla", "dogrula", "girmeniz", "odeme", "guncelle"])
        if category == .scam && confidence >= 0.85 && accountThreat && (hasURL || urgency) {
            return SMSAssessment(category: category, probability: confidence,
                                 recommendation: .junk, explanation: "AI tahmini ve kimlik avı/dolandırıcılık belirtileri örtüşüyor.")
        }
        let promoEvidence = has(["indirim", "kampanya", "firsat", "kupon", "magaza", "hediye", "sezon sonu"])
        if category == .advertising && confidence >= 0.85 && promoEvidence {
            return SMSAssessment(category: category, probability: confidence,
                                 recommendation: .promotion, explanation: "Reklam olduğu güçlü biçimde tahmin edildi.")
        }
        return SMSAssessment(category: category, probability: confidence,
                             recommendation: .allow,
                             explanation: "Yanlış engelleme riskini azaltmak için mesaj normal bırakıldı.")
    }
}
