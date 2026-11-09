import Foundation
import IdentityLookup

// iOS calls this extension for eligible messages from unknown senders only.
final class MessageFilterExtension: ILMessageFilterExtension, ILMessageFilterQueryHandling {
    private let analyzer = SMSAnalyzer(bundle: .main)

    func handle(_ queryRequest: ILMessageFilterQueryRequest,
                context: ILMessageFilterExtensionContext,
                completion: @escaping (ILMessageFilterQueryResponse) -> Void) {
        let assessment = analyzer.analyze(queryRequest.messageBody ?? "")
        let response = ILMessageFilterQueryResponse()
        switch assessment.recommendation {
        case .allow: response.action = .allow
        case .promotion: response.action = .promotion
        case .junk: response.action = .junk
        }
        completion(response)
    }
}
