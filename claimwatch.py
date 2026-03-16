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
HIGH_RISK_TYPES = {"life", "health"}


@dataclass
class ClaimData:
    claim_amount: Optional[float] = None
    claim_type: str = ""
    claim_description: str = ""
    incident_date: Optional[str] = None
    filing_date: Optional[str] = None
    policy_start_date: Optional[str] = None
    coverage_upgrade_date: Optional[str] = None
    policy_limit: Optional[float] = None
    prior_claim_count: Optional[int] = None
    claimant_history: str = ""
    behavioral_notes: str = ""
    supporting_documents: List[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    summary: str
    risk_level: str
    risk_score: int
    financial_flags: List[str] = field(default_factory=list)
    behavioral_flags: List[str] = field(default_factory=list)
    context_flags: List[str] = field(default_factory=list)
    timing_flags: List[str] = field(default_factory=list)
    language_flags: List[str] = field(default_factory=list)
    detailed_analysis: str = ""
    recommended_action: str = "Manual Review Required"
    recommendation_justification: str = ""

    def _format_category(self, flags: List[str]) -> str:
        return "\n".join(f"- {flag}" for flag in flags) if flags else "- None identified from submitted data."

    def formatted_report(self) -> str:
        return (
            "Fraud Investigation Report\n\n"
            f"Claim Summary:\n{self.summary}\n"
            f"Risk Level:\n{self.risk_level}\n"
            f"Risk Score:\n{self.risk_score}/100\n\n"
            "Key Suspicious Indicators:\n\n"
            "Financial:\n"
            f"{self._format_category(self.financial_flags)}\n\n"
            "Behavioral:\n"
            f"{self._format_category(self.behavioral_flags)}\n\n"
            "Context:\n"
            f"{self._format_category(self.context_flags)}\n\n"
            "Timing:\n"
            f"{self._format_category(self.timing_flags)}\n\n"
            "Language Pattern Indicators:\n"
            f"{self._format_category(self.language_flags)}\n\n"
            f"Detailed Analysis:\n{self.detailed_analysis}\n\n"
            f"Recommended Action:\n{self.recommended_action}\n"
            f"Justification:\n{self.recommendation_justification}"
        )


class ClaimAnalyzer:
    def analyze(self, claim: ClaimData) -> AnalysisResult:
        score = 5
        financial_flags: List[str] = []
        behavioral_flags: List[str] = []
        context_flags: List[str] = []
        timing_flags: List[str] = []
        language_flags: List[str] = []
        missing_fields = self._missing_fields(claim)

        description = claim.claim_description.lower().strip()
        claim_type = claim.claim_type.lower().strip()

        score += self._financial_checks(claim, financial_flags)
        score += self._behavior_checks(claim, behavioral_flags)
        score += self._language_checks(description, behavioral_flags, language_flags)
        score += self._context_checks(claim_type, description, context_flags)
        score += self._timing_checks(claim, timing_flags)

        if missing_fields:
            context_flags.append(f"Missing critical input fields: {', '.join(missing_fields)}.")
            score = max(score + len(missing_fields) * 3, 38)

        score = max(0, min(100, score))
        risk_level = self._risk_level(score)
        recommendation, rec_justification = self._recommendation(risk_level, missing_fields, score)

        return AnalysisResult(
            summary=self._build_summary(claim, missing_fields),
            risk_level=risk_level,
            risk_score=score,
            financial_flags=financial_flags,
            behavioral_flags=behavioral_flags,
            context_flags=context_flags,
            timing_flags=timing_flags,
            language_flags=language_flags,
            detailed_analysis=self._detailed_analysis(
                claim, risk_level, score, missing_fields, financial_flags, behavioral_flags, context_flags, timing_flags, language_flags
            ),
            recommended_action=recommendation,
            recommendation_justification=rec_justification,
        )

    @staticmethod
    def _missing_fields(claim: ClaimData) -> List[str]:
        missing = []
        if claim.claim_amount is None:
            missing.append("claim_amount")
        if not claim.claim_type.strip():
            missing.append("claim_type")
        if not claim.claim_description.strip():
            missing.append("claim_description")
        if not claim.incident_date:
            missing.append("incident_date")
        if not claim.filing_date:
            missing.append("claim_submission_date")
        if not claim.policy_start_date:
            missing.append("policy_start_date")
        return missing

    @staticmethod
    def _financial_checks(claim: ClaimData, financial_flags: List[str]) -> int:
        points = 0
        if claim.claim_amount is None:
            return points

        if claim.claim_amount >= 100000:
            points += 25
            financial_flags.append("Claim amount is exceptionally high and should be validated with third-party evidence.")
        elif claim.claim_amount >= 50000:
            points += 16
            financial_flags.append("Claim amount is materially high relative to standard loss profiles.")
        elif claim.claim_amount >= 20000:
            points += 8
            financial_flags.append("Claim amount is moderately high and warrants enhanced verification.")

        amount_as_text = str(int(claim.claim_amount)) if float(claim.claim_amount).is_integer() else str(claim.claim_amount)
        if re.fullmatch(r"(\d)\1{2,}", amount_as_text):
            points += 5
            financial_flags.append("Claim amount uses unusual repeated digits, which can indicate synthetic inflation.")

        if claim.policy_limit and claim.claim_amount >= 0.9 * claim.policy_limit:
            points += 12
            financial_flags.append("Claim amount is close to policy limit, increasing inflation risk.")

        if claim.policy_limit and claim.claim_amount > claim.policy_limit:
            points += 20
            financial_flags.append("Claimed amount exceeds policy limit and is not contractually consistent.")

        return points

    @staticmethod
    def _behavior_checks(claim: ClaimData, behavioral_flags: List[str]) -> int:
        points = 0
        if claim.prior_claim_count is not None:
            if claim.prior_claim_count >= 4:
                points += 20
                behavioral_flags.append("Frequent prior claims indicate elevated repeat-claim exposure.")
            elif claim.prior_claim_count >= 2:
                points += 10
                behavioral_flags.append("Multiple prior claims warrant historical pattern verification.")

        notes = f"{claim.claimant_history} {claim.behavioral_notes}".lower()
        if any(token in notes for token in ["changed story", "inconsistent", "refused", "uncooperative"]):
            points += 12
            behavioral_flags.append("Claimant behavior notes indicate inconsistency or non-cooperation.")

        if not claim.supporting_documents:
            points += 8
            behavioral_flags.append("No supporting documents were provided with claim submission.")

        return points

    @staticmethod
    def _language_checks(description: str, behavioral_flags: List[str], language_flags: List[str]) -> int:
        points = 0
        urgency_terms = ["urgent", "immediately", "asap", "right away", "today"]
        exaggeration_terms = ["catastrophic", "devastated", "everything destroyed", "total loss"]

        urgency_hits = sum(term in description for term in urgency_terms)
        exaggeration_hits = sum(term in description for term in exaggeration_terms)

        if urgency_hits:
            points += 6 + urgency_hits
            behavioral_flags.append("Narrative includes urgency pressure for accelerated settlement.")
            language_flags.append("Urgency terms detected in claim narrative.")

        if exaggeration_hits:
            points += 5 + exaggeration_hits
            language_flags.append("Exaggerative wording detected that may overstate severity.")

        repeated_phrase_pattern = re.compile(r"\b(\w+(?:\s+\w+){0,2})\b(?:.*\b\1\b){2,}", re.IGNORECASE)
        if description and repeated_phrase_pattern.search(description):
            points += 8
            language_flags.append("Repeated or templated phrase structures were detected.")

        word_count = len(description.split())
        if 1 <= word_count <= 5:
            points += 5
            language_flags.append("Description is unusually brief and lacks verifiable detail.")
        elif word_count > 180:
            points += 4
            language_flags.append("Description is unusually long, potentially obscuring key facts.")

        return points

    @staticmethod
    def _context_checks(claim_type: str, description: str, context_flags: List[str]) -> int:
        points = 0
        type_keywords = {
            "auto": ["vehicle", "car", "collision", "accident", "garage"],
            "health": ["hospital", "medical", "surgery", "treatment", "injury"],
            "property": ["house", "home", "roof", "fire", "water"],
            "travel": ["flight", "luggage", "trip", "hotel"],
            "life": ["deceased", "beneficiary", "death certificate"],
        }

        if claim_type and claim_type in type_keywords:
            if not any(token in description for token in type_keywords[claim_type]):
                points += 12
                context_flags.append("Claim narrative does not align with expected terminology for claim type.")

        contradictions = 0
        if "no witnesses" in description and "several witnesses" in description:
            contradictions += 1
        if "stolen" in description and "parked in garage" in description and "public lot" in description:
            contradictions += 1

        if contradictions:
            points += contradictions * 14
            context_flags.append("Narrative contains potentially contradictory statements requiring corroboration.")

        return points

    @staticmethod
    def _timing_checks(claim: ClaimData, timing_flags: List[str]) -> int:
        points = 0
        incident_dt = parse_date(claim.incident_date) if claim.incident_date else None
        filing_dt = parse_date(claim.filing_date) if claim.filing_date else None
        policy_start_dt = parse_date(claim.policy_start_date) if claim.policy_start_date else None
        upgrade_dt = parse_date(claim.coverage_upgrade_date) if claim.coverage_upgrade_date else None

        if claim.incident_date and not incident_dt:
            points += 6
            timing_flags.append("Incident date format is invalid or non-standard.")
        if claim.filing_date and not filing_dt:
            points += 6
            timing_flags.append("Claim submission date format is invalid or non-standard.")
        if claim.policy_start_date and not policy_start_dt:
            points += 6
            timing_flags.append("Policy start date format is invalid or non-standard.")

        if incident_dt and filing_dt:
            delta = (filing_dt - incident_dt).days
            if delta < 0:
                points += 25
                timing_flags.append("Claim submission date predates incident date.")
            elif delta == 0:
                points += 5
                timing_flags.append("Same-day incident and filing can be valid but requires timeline verification.")
            elif delta > 120:
                points += 10
                timing_flags.append("Long delay between incident and submission requires supporting explanation.")


        if policy_start_dt and incident_dt:
            days_from_start = (incident_dt - policy_start_dt).days
            if 0 <= days_from_start <= 30:
                points += 14
                timing_flags.append("Incident occurred shortly after policy inception.")
            elif days_from_start < 0:
                points += 20
                timing_flags.append("Incident date occurs before policy start date.")

        if upgrade_dt and incident_dt:
            days_from_upgrade = (incident_dt - upgrade_dt).days
            if 0 <= days_from_upgrade <= 15:
                points += 12
                timing_flags.append("Incident occurred shortly after coverage upgrade.")

        return points

    @staticmethod
    def _risk_level(score: int) -> str:
        if score <= 30:
            return "Low"
        if score <= 60:
            return "Medium"
        return "High"

    @staticmethod
    def _recommendation(risk_level: str, missing_fields: List[str], score: int) -> tuple[str, str]:
        if missing_fields:
            return (
                "Request Additional Documentation",
                "Critical input fields are missing; verification cannot be completed to investigative standard.",
            )
        if risk_level == "Low":
            return (
                "Approve Claim",
                "Current evidence does not present material fraud indicators beyond routine validation thresholds.",
            )
        if risk_level == "Medium":
            return (
                "Manual Review Required",
                f"Risk score of {score}/100 indicates notable anomalies that require investigator confirmation.",
            )
        return (
            "Escalate to Fraud Investigation Unit",
            f"Risk score of {score}/100 reflects multiple converging fraud indicators requiring specialist investigation.",
        )

    @staticmethod
    def _build_summary(claim: ClaimData, missing_fields: List[str]) -> str:
        segments = [f"{claim.claim_type or 'Unspecified'} claim"]
        if claim.claim_amount is not None:
            segments.append(f"for ${claim.claim_amount:,.2f}")
        if claim.incident_date:
            segments.append(f"incident date {claim.incident_date}")
        if claim.filing_date:
            segments.append(f"submission date {claim.filing_date}")
        if claim.policy_start_date:
            segments.append(f"policy start {claim.policy_start_date}")

        summary = ", ".join(segments) + "."
        if missing_fields:
            summary += f" Missing fields: {', '.join(missing_fields)}."
        return summary

    @staticmethod
    def _detailed_analysis(
        claim: ClaimData,
        risk_level: str,
        score: int,
        missing_fields: List[str],
        financial_flags: List[str],
        behavioral_flags: List[str],
        context_flags: List[str],
        timing_flags: List[str],
        language_flags: List[str],
    ) -> str:
        evidence_count = sum(bool(group) for group in [financial_flags, behavioral_flags, context_flags, timing_flags, language_flags])
        analysis = (
            f"This assessment classifies the claim as {risk_level} risk with a score of {score}/100 based on available "
            "financial, behavioral, contextual, timing, and language-pattern evidence. "
        )

        if evidence_count == 0:
            analysis += "No significant anomalies were detected in the submitted data set. "
        else:
            analysis += "Detected indicators should be corroborated against policy records, invoices, statements, and independent evidence. "

        if claim.claim_type.lower() in HIGH_RISK_TYPES:
            analysis += "The claim type carries higher baseline sensitivity and warrants stricter document validation controls. "

        if missing_fields:
            analysis += (
                "Because mandatory data elements are missing, this outcome is provisional and should not be interpreted "
                "as a definitive fraud conclusion."
            )
        else:
            analysis += "Conclusion remains evidence-based and non-accusatory pending standard verification completion."

        return analysis


def parse_date(value: str) -> Optional[datetime]:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def load_claim(path: str) -> ClaimData:
    with open(path, "r", encoding="utf-8") as file:
        payload = json.load(file)

    documents = payload.get("supporting_documents", [])
    if not isinstance(documents, list):
        documents = []

    return ClaimData(
        claim_amount=payload.get("claim_amount"),
        claim_type=payload.get("claim_type", ""),
        claim_description=payload.get("claim_description", ""),
        incident_date=payload.get("incident_date"),
        filing_date=payload.get("filing_date"),
        policy_start_date=payload.get("policy_start_date"),
        coverage_upgrade_date=payload.get("coverage_upgrade_date"),
        policy_limit=payload.get("policy_limit"),
        prior_claim_count=payload.get("prior_claim_count"),
        claimant_history=payload.get("claimant_history", ""),
        behavioral_notes=payload.get("behavioral_notes", ""),
        supporting_documents=documents,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an insurance claim for potential fraud risk.")
    parser.add_argument("--input", required=True, help="Path to JSON claim input file")
    parser.add_argument("--output", help="Optional path to save report text")
    args = parser.parse_args()

    claim = load_claim(args.input)
    result = ClaimAnalyzer().analyze(claim)
    report = result.formatted_report()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(report + "\n")

    print(report)


if __name__ == "__main__":
    main()
