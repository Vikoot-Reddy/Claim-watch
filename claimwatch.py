#!/usr/bin/env python3
"""ClaimWatch: End-to-end insurance fraud risk analysis CLI."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y")


@dataclass
class ClaimData:
    claim_amount: Optional[float] = None
    claim_description: str = ""
    claim_type: str = ""
    incident_date: Optional[str] = None
    filing_date: Optional[str] = None
    behavioral_notes: str = ""
    prior_claim_count: Optional[int] = None


@dataclass
class AnalysisResult:
    summary: str
    risk_level: str
    risk_score: int
    financial_flags: List[str] = field(default_factory=list)
    behavioral_flags: List[str] = field(default_factory=list)
    context_flags: List[str] = field(default_factory=list)
    timing_flags: List[str] = field(default_factory=list)
    detailed_analysis: str = ""
    recommended_action: str = "Manual Review"

    def formatted_report(self) -> str:
        indicators = []
        for group_name, flags in [
            ("Financial red flags", self.financial_flags),
            ("Behavioral red flags", self.behavioral_flags),
            ("Context inconsistencies", self.context_flags),
            ("Timing anomalies", self.timing_flags),
        ]:
            if flags:
                indicators.extend([f"- {group_name}: {flag}" for flag in flags])

        if not indicators:
            indicators.append("- No material suspicious indicators identified from submitted data.")

        return (
            "Fraud Investigation Report\n\n"
            f"Claim Summary:\n{self.summary}\n\n"
            f"Risk Level:\n{self.risk_level}\n\n"
            f"Risk Score:\n{self.risk_score}/100\n\n"
            "Key Suspicious Indicators:\n"
            + "\n".join(indicators)
            + "\n\n"
            f"Detailed Analysis:\n{self.detailed_analysis}\n\n"
            f"Recommended Action:\n{self.recommended_action}"
        )


class ClaimAnalyzer:
    def analyze(self, claim: ClaimData) -> AnalysisResult:
        score = 10
        financial_flags: List[str] = []
        behavioral_flags: List[str] = []
        context_flags: List[str] = []
        timing_flags: List[str] = []
        missing_fields = []

        if claim.claim_amount is None:
            missing_fields.append("claim_amount")
        if not claim.claim_description.strip():
            missing_fields.append("claim_description")
        if not claim.claim_type.strip():
            missing_fields.append("claim_type")
        if not claim.incident_date:
            missing_fields.append("incident_date")
        if not claim.filing_date:
            missing_fields.append("filing_date")

        if claim.claim_amount is not None:
            if claim.claim_amount >= 50000:
                score += 20
                financial_flags.append("High claim amount compared with baseline fraud-risk thresholds.")
            elif claim.claim_amount >= 20000:
                score += 10
                financial_flags.append("Moderately high claim amount; requires stronger supporting documentation.")

        if claim.prior_claim_count is not None:
            if claim.prior_claim_count >= 3:
                score += 15
                behavioral_flags.append("Multiple prior claims in claimant history may indicate elevated risk.")
            elif claim.prior_claim_count == 2:
                score += 8
                behavioral_flags.append("Repeated claims history warrants additional validation.")

        description = claim.claim_description.lower()
        urgency_terms = ["urgent", "immediately", "asap", "right away", "today"]
        exaggeration_terms = ["total loss", "devastated", "catastrophic", "everything destroyed"]

        urgency_hits = sum(term in description for term in urgency_terms)
        exaggeration_hits = sum(term in description for term in exaggeration_terms)

        if urgency_hits:
            score += 8 + (urgency_hits - 1) * 2
            behavioral_flags.append("Language emphasizes urgent payout timing before routine verification.")

        if exaggeration_hits:
            score += 6 + (exaggeration_hits - 1) * 2
            context_flags.append("Narrative contains exaggerative language that may overstate loss severity.")

        repeated_phrase_pattern = re.compile(r"\b(\w+(?:\s+\w+){0,2})\b(?:.*\b\1\b){2,}", re.IGNORECASE)
        if claim.claim_description and repeated_phrase_pattern.search(claim.claim_description):
            score += 8
            context_flags.append("Repeated/templated phrasing detected in description text.")

        incident_dt = parse_date(claim.incident_date) if claim.incident_date else None
        filing_dt = parse_date(claim.filing_date) if claim.filing_date else None

        if claim.incident_date and not incident_dt:
            score += 6
            timing_flags.append("Incident date format is invalid or non-standard.")
        if claim.filing_date and not filing_dt:
            score += 6
            timing_flags.append("Filing date format is invalid or non-standard.")

        if incident_dt and filing_dt:
            delta_days = (filing_dt - incident_dt).days
            if delta_days < 0:
                score += 25
                timing_flags.append("Filing date occurs before incident date, creating a logical contradiction.")
            elif delta_days > 90:
                score += 12
                timing_flags.append("Unusually long delay between incident and filing may require explanation.")
            elif delta_days == 0:
                score += 4
                timing_flags.append("Same-day filing may be valid but can require identity and timeline validation.")

        notes = claim.behavioral_notes.lower()
        if any(token in notes for token in ["changed story", "inconsistent", "uncooperative", "refused"]):
            score += 14
            behavioral_flags.append("Behavioral notes indicate inconsistent or non-cooperative claimant behavior.")

        contradictions = 0
        if "stolen" in description and "parked in garage" in description and "public lot" in description:
            contradictions += 1
        if "no witnesses" in description and "several witnesses" in description:
            contradictions += 1

        if contradictions:
            score += 10 * contradictions
            context_flags.append("Narrative includes potentially contradictory statements requiring verification.")

        if missing_fields:
            score = max(score, 45)
            score = min(score + len(missing_fields) * 2, 65)
            context_flags.append(f"Critical fields missing: {', '.join(missing_fields)}.")

        score = max(0, min(100, score))

        if score >= 75:
            risk_level = "High"
            action = "Escalate to Fraud Investigation Unit"
        elif score >= 40:
            risk_level = "Medium"
            action = "Request Additional Documentation" if missing_fields else "Manual Review"
        else:
            risk_level = "Low"
            action = "Approve"

        summary = self._build_summary(claim, missing_fields)
        detailed = self._build_detailed_analysis(
            score, risk_level, missing_fields, financial_flags, behavioral_flags, context_flags, timing_flags
        )

        return AnalysisResult(
            summary=summary,
            risk_level=risk_level,
            risk_score=score,
            financial_flags=financial_flags,
            behavioral_flags=behavioral_flags,
            context_flags=context_flags,
            timing_flags=timing_flags,
            detailed_analysis=detailed,
            recommended_action=action,
        )

    @staticmethod
    def _build_summary(claim: ClaimData, missing_fields: List[str]) -> str:
        parts = []
        if claim.claim_type:
            parts.append(f"{claim.claim_type} claim")
        else:
            parts.append("Claim")

        if claim.claim_amount is not None:
            parts.append(f"for ${claim.claim_amount:,.2f}")

        if claim.incident_date and claim.filing_date:
            parts.append(f"with incident date {claim.incident_date} and filing date {claim.filing_date}")

        summary = " ".join(parts) + "."
        if missing_fields:
            summary += f" Missing inputs: {', '.join(missing_fields)}."
        return summary

    @staticmethod
    def _build_detailed_analysis(
        score: int,
        level: str,
        missing_fields: List[str],
        financial_flags: List[str],
        behavioral_flags: List[str],
        context_flags: List[str],
        timing_flags: List[str],
    ) -> str:
        factors = sum(bool(x) for x in [financial_flags, behavioral_flags, context_flags, timing_flags])
        narrative = (
            f"The claim is assessed at {level} risk with a score of {score}/100 based on evaluated financial, "
            f"behavioral, contextual, and timing dimensions."
        )
        if factors == 0:
            narrative += " No suspicious indicators were detected from the submitted inputs."
        if missing_fields:
            narrative += (
                " This result is provisional because critical fields are missing; conclusions should be "
                "revalidated after documentation is provided."
            )
        else:
            narrative += " Findings should be confirmed against policy records, invoices, and independent evidence."
        return narrative


def parse_date(value: str) -> Optional[datetime]:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def load_claim(path: str) -> ClaimData:
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    return ClaimData(
        claim_amount=payload.get("claim_amount"),
        claim_description=payload.get("claim_description", ""),
        claim_type=payload.get("claim_type", ""),
        incident_date=payload.get("incident_date"),
        filing_date=payload.get("filing_date"),
        behavioral_notes=payload.get("behavioral_notes", ""),
        prior_claim_count=payload.get("prior_claim_count"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an insurance claim for potential fraud risk.")
    parser.add_argument("--input", required=True, help="Path to JSON claim input file")
    parser.add_argument("--output", help="Optional path to write report text")
    args = parser.parse_args()

    claim = load_claim(args.input)
    result = ClaimAnalyzer().analyze(claim)
    report = result.formatted_report()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report + "\n")
    print(report)


if __name__ == "__main__":
    main()
