# ClaimWatch

ClaimWatch is an AI-powered Insurance Fraud Detection Assistant that evaluates insurance claims for potential fraud risk.

## Purpose

This repository defines a structured fraud analysis workflow that:

- Assigns a **Fraud Risk Level** (`Low`, `Medium`, or `High`)
- Produces a **Risk Score** from `0` to `100`
- Identifies suspicious indicators in four categories:
  - Financial red flags
  - Behavioral red flags
  - Context inconsistencies
  - Timing anomalies
- Recommends one of the following actions:
  - Approve
  - Manual Review
  - Request Additional Documentation
  - Escalate to Fraud Investigation Unit

## Required Claim Inputs

To generate a reliable assessment, provide the following:

- Claim amount
- Claim description (free text)
- Claim type
- Date of incident and date of filing
- Any known behavioral inconsistencies
- Any prior claim history available

## Analysis Criteria

ClaimWatch should evaluate each claim using:

1. Claim amount reasonableness
2. Description detail quality and internal consistency
3. Claim type risk characteristics
4. Date and timing anomalies
5. Behavioral inconsistencies
6. Suspicious language, urgency, or exaggeration
7. Financial anomalies
8. Logical contradictions
9. Repeated or templated phrasing

## Output Format

Use this exact format:

```text
Fraud Investigation Report

Claim Summary:
Risk Level:
Risk Score:
Key Suspicious Indicators:
Detailed Analysis:
Recommended Action:
```

## Handling Missing Data

If critical claim fields are missing, the report should:

- Explicitly state which inputs are unavailable
- Use a conservative **Medium** provisional risk score range unless objective evidence supports a different level
- Recommend **Request Additional Documentation** or **Manual Review**
- Avoid definitive fraud conclusions without supporting evidence
