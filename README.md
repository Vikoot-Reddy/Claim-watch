# ClaimWatch

ClaimWatch is an AI-powered Insurance Fraud Detection Assistant that analyzes claim inputs, assigns fraud risk, and outputs a structured **Fraud Investigation Report**.

## Features

- End-to-end JSON input → risk analysis → text report workflow
- Risk level classification: `Low`, `Medium`, `High`
- Risk score output from `0` to `100`
- Suspicious indicator detection across:
  - Financial red flags
  - Behavioral red flags
  - Context inconsistencies
  - Timing anomalies
- Action recommendation:
  - Approve
  - Manual Review
  - Request Additional Documentation
  - Escalate to Fraud Investigation Unit

## Project Structure

- `claimwatch.py` — CLI + fraud analysis engine
- `tests/test_claimwatch.py` — unit tests for low/medium/high-risk paths
- `sample_claim.json` — sample input payload
- `report_example.md` — sample formatted report output

## Input Schema

The CLI expects a JSON file with the following fields:

```json
{
  "claim_amount": 27500,
  "claim_description": "Water damage claim...",
  "claim_type": "Home",
  "incident_date": "2026-02-01",
  "filing_date": "2026-02-28",
  "behavioral_notes": "Claimant was cooperative...",
  "prior_claim_count": 2
}
```

### Field Notes

- `claim_amount` *(number, optional but recommended)*
- `claim_description` *(string, required for strong analysis)*
- `claim_type` *(string, optional but recommended)*
- `incident_date` *(string, formats: `YYYY-MM-DD`, `YYYY/MM/DD`, `MM/DD/YYYY`)*
- `filing_date` *(string, same supported formats)*
- `behavioral_notes` *(string, optional)*
- `prior_claim_count` *(integer, optional)*

## Run ClaimWatch

```bash
python3 claimwatch.py --input sample_claim.json
```

Optional file output:

```bash
python3 claimwatch.py --input sample_claim.json --output report.txt
```

## Output Format

ClaimWatch always emits this structure:

```text
Fraud Investigation Report

Claim Summary:
Risk Level:
Risk Score:
Key Suspicious Indicators:
Detailed Analysis:
Recommended Action:
```

## Analysis Logic (High Level)

ClaimWatch evaluates:

1. Claim amount reasonableness
2. Claim description quality, suspicious urgency, and exaggeration language
3. Claim type context
4. Timeline consistency between incident and filing
5. Behavioral notes for inconsistency or non-cooperation
6. Narrative contradictions
7. Repeated or templated phrasing
8. Missing critical fields (provisional handling)

If key fields are missing, ClaimWatch uses a conservative provisional medium-risk posture and recommends requesting documentation.

## Testing

Run unit tests:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
