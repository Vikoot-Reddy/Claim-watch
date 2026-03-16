# ClaimWatch

ClaimWatch is an AI-powered Insurance Fraud Detection Analyst that performs end-to-end insurance claim risk assessment and generates investigator-ready fraud reports.

## What ClaimWatch Does

ClaimWatch evaluates claims using five investigation dimensions:

1. **Financial Risk Indicators**
2. **Behavioral Indicators**
3. **Timing & Context Analysis**
4. **Logical Consistency Checks**
5. **Language Pattern Indicators**

It then assigns:

- **Risk Score** (`0–100`)
- **Risk Level**
  - `Low` (`0–30`)
  - `Medium` (`31–60`)
  - `High` (`61–100`)
- **Recommended Action**
  - Approve Claim
  - Manual Review Required
  - Request Additional Documentation
  - Escalate to Fraud Investigation Unit

## Project Structure

- `claimwatch.py` — CLI and analysis engine
- `tests/test_claimwatch.py` — unit tests covering low/medium/high and missing-data cases
- `sample_claim.json` — runnable sample input
- `report_example.md` — sample structured report output

## Input JSON Schema

```json
{
  "claim_amount": 27500,
  "claim_type": "Property",
  "claim_description": "Water damage in house basement...",
  "incident_date": "2026-02-01",
  "filing_date": "2026-02-28",
  "policy_start_date": "2025-06-01",
  "coverage_upgrade_date": "2026-01-25",
  "policy_limit": 50000,
  "prior_claim_count": 2,
  "claimant_history": "Prior small claim in previous year.",
  "behavioral_notes": "Claimant cooperative but repeatedly requested same-day payout.",
  "supporting_documents": ["photos.zip", "repair_estimate.pdf"]
}
```

### Field Notes

- `claim_amount` *(number)*
- `claim_type` *(string; Auto, Health, Property, Travel, Life, etc.)*
- `claim_description` *(string)*
- `incident_date` *(string; `YYYY-MM-DD`, `YYYY/MM/DD`, `MM/DD/YYYY`)*
- `filing_date` *(string; claim submission date)*
- `policy_start_date` *(string)*
- `coverage_upgrade_date` *(string, optional)*
- `policy_limit` *(number, optional)*
- `prior_claim_count` *(integer, optional)*
- `claimant_history` *(string, optional)*
- `behavioral_notes` *(string, optional)*
- `supporting_documents` *(array of strings, optional)*

## Run ClaimWatch

```bash
python3 claimwatch.py --input sample_claim.json
```

Optional file output:

```bash
python3 claimwatch.py --input sample_claim.json --output report.txt
```

## Report Format

ClaimWatch emits this structure:

```text
Fraud Investigation Report

Claim Summary:
Risk Level:
Risk Score:

Key Suspicious Indicators:

Financial:
Behavioral:
Context:
Timing:
Language Pattern Indicators:

Detailed Analysis:

Recommended Action:
Justification:
```

## Testing

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
