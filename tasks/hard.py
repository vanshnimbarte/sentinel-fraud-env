CASE = {
    "case_id": "HARD-001",
    "alert": """
ALERT: Multiple high-value transactions on Account #992341
- $8,200 in purchases over 72 hours (electronics, luxury goods, gift cards)
- Account holder: James Kowalski, DOB 1989-03-15, Seattle WA
- Account age: 14 months, credit limit recently raised to $10,000
- Credit score: 720 (built gradually over 14 months)
Customer has been a good payer. Transactions seem unusual but account is established.
""",
    "ground_truth": "FRAUD_HIGH_RISK",
    "fraud_type": "synthetic_identity_bustout",
    "evidence_map": {
        "CHECK_IDENTITY": {
            "result": "SSN issued 2019 (subject born 1989, SSN should predate 2005). "
                      "Address: PO Box only, not residential. Phone: VOIP number. "
                      "No employment verification on file.",
            "informativeness": 0.9
        },
        "QUERY_HISTORY": {
            "result": "14 months of perfect payment history. Started with secured card $500. "
                      "Limit raised 3 times. Last 72 hours: sudden maximum utilization. "
                      "Pattern: slow credit building then sudden full spend.",
            "informativeness": 0.8
        },
        "CROSS_REF_NETWORK": {
            "result": "SSN linked to 2 other bank accounts. Both show identical 14-month "
                      "credit-building pattern. Both hit maximum utilization in last 7 days.",
            "informativeness": 1.0
        },
        "VERIFY_LOCATION": {
            "result": "Purchases across 3 cities in 72 hours: Seattle, Portland, San Francisco. "
                      "Shipping addresses: 4 different freight forwarders.",
            "informativeness": 0.7
        },
        "ANALYZE_VELOCITY": {
            "result": "72-hour spend $8,200 vs entire prior 13-month total of $4,100. "
                      "Current spend is 2x entire history in 3 days.",
            "informativeness": 0.8
        },
        "CHECK_DEVICE": {
            "result": "Device consistent with prior history. No anomaly detected.",
            "informativeness": 0.1
        }
    }
}

def grade(actions_taken: list, final_ruling: str, steps_used: int) -> float:
    if final_ruling != "FRAUD_HIGH_RISK":
        return 0.0
    required_evidence = {"CHECK_IDENTITY", "QUERY_HISTORY", "CROSS_REF_NETWORK"}
    found = len(required_evidence.intersection(set(actions_taken)))
    if found < 2:
        return 0.2
    evidence_score = found / 3
    efficiency = 1.0 if steps_used <= 7 else (0.7 if steps_used <= 10 else 0.5)
    return round(0.4 * efficiency + 0.6 * evidence_score, 2)
