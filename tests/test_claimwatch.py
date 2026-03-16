import unittest

from claimwatch import ClaimAnalyzer, ClaimData


class ClaimWatchTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = ClaimAnalyzer()

    def test_low_risk_claim(self):
        claim = ClaimData(
            claim_amount=3200,
            claim_type="Auto",
            claim_description="Minor vehicle collision with rear bumper damage.",
            incident_date="2026-01-05",
            filing_date="2026-01-07",
            policy_start_date="2024-01-01",
            prior_claim_count=0,
            supporting_documents=["repair_estimate.pdf", "photos.zip"],
        )
        result = self.analyzer.analyze(claim)
        self.assertEqual(result.risk_level, "Low")
        self.assertLessEqual(result.risk_score, 30)
        self.assertEqual(result.recommended_action, "Approve Claim")

    def test_medium_risk_requires_manual_review(self):
        claim = ClaimData(
            claim_amount=27500,
            claim_type="Property",
            claim_description=(
                "Water damage in house basement. Need immediate processing today due to total loss of appliances."
            ),
            incident_date="2026-02-01",
            filing_date="2026-02-28",
            policy_start_date="2025-06-01",
            prior_claim_count=2,
            supporting_documents=["photos.zip"],
        )
        result = self.analyzer.analyze(claim)
        self.assertEqual(result.risk_level, "Medium")
        self.assertGreaterEqual(result.risk_score, 31)
        self.assertLessEqual(result.risk_score, 60)
        self.assertEqual(result.recommended_action, "Manual Review Required")

    def test_high_risk_escalation(self):
        claim = ClaimData(
            claim_amount=125000,
            policy_limit=100000,
            claim_type="Auto",
            claim_description=(
                "Vehicle was stolen from public lot and parked in garage. "
                "No witnesses and several witnesses confirmed it. Urgent payout immediately ASAP."
            ),
            incident_date="2026-03-11",
            filing_date="2026-01-01",
            policy_start_date="2026-03-01",
            prior_claim_count=4,
            claimant_history="changed story twice",
            behavioral_notes="uncooperative",
            supporting_documents=[],
        )
        result = self.analyzer.analyze(claim)
        self.assertEqual(result.risk_level, "High")
        self.assertGreaterEqual(result.risk_score, 61)
        self.assertEqual(result.recommended_action, "Escalate to Fraud Investigation Unit")

    def test_missing_fields_requests_documents(self):
        claim = ClaimData(claim_description="Please process urgently")
        result = self.analyzer.analyze(claim)
        self.assertEqual(result.risk_level, "Medium")
        self.assertEqual(result.recommended_action, "Request Additional Documentation")


if __name__ == "__main__":
    unittest.main()
