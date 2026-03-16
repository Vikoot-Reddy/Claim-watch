import unittest

from claimwatch import ClaimAnalyzer, ClaimData


class ClaimWatchTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = ClaimAnalyzer()

    def test_low_risk_claim(self):
        claim = ClaimData(
            claim_amount=3200,
            claim_description="Rear bumper damage from low-speed parking collision.",
            claim_type="Auto",
            incident_date="2026-01-05",
            filing_date="2026-01-07",
            behavioral_notes="cooperative",
            prior_claim_count=0,
        )
        result = self.analyzer.analyze(claim)
        self.assertEqual(result.risk_level, "Low")
        self.assertEqual(result.recommended_action, "Approve")

    def test_high_risk_with_contradictions(self):
        claim = ClaimData(
            claim_amount=80000,
            claim_description=(
                "Vehicle was stolen from public lot and parked in garage. "
                "No witnesses but several witnesses confirmed it. Urgent payout immediately."
            ),
            claim_type="Auto",
            incident_date="2026-03-11",
            filing_date="2026-01-01",
            behavioral_notes="changed story and uncooperative",
            prior_claim_count=4,
        )
        result = self.analyzer.analyze(claim)
        self.assertEqual(result.risk_level, "High")
        self.assertGreaterEqual(result.risk_score, 75)
        self.assertEqual(result.recommended_action, "Escalate to Fraud Investigation Unit")

    def test_missing_fields_is_provisional_medium(self):
        claim = ClaimData(claim_description="Please process ASAP")
        result = self.analyzer.analyze(claim)
        self.assertEqual(result.risk_level, "Medium")
        self.assertGreaterEqual(result.risk_score, 45)
        self.assertEqual(result.recommended_action, "Request Additional Documentation")


if __name__ == "__main__":
    unittest.main()
