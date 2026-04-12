CASE = {
    "case_id": "EASY-001",
    "alert": """
ALERT: Suspicious activity detected on Account #847291
- 6 transactions in the last 2 hours
- Merchants: McDonald's ($1.23), Shell Gas ($0.99), Amazon ($2.50),
  Starbucks ($0.75), Walmart ($1.10), Target ($0.88)
- Account age: 12 days
- All transactions approved
""",
    "ground_truth": "FRAUD",
        "risk_level": "EASY",
        "fraud_type": "card_testing",
    "evidence_map": {
        "QUERY_HISTORY": {
            "result": "Account opened 12 days ago. No prior transactions before today. "
                      "6 transactions all within last 2 hours at varied merchants. "
                      "All amounts under $5.",
            "informativeness": 0.9
        },
        "ANALYZE_VELOCITY": {
            "result": "VELOCITY ALERT: 6 transactions in 118 minutes. "
                      "Average inter-transaction time: 19.6 minutes. "
                      "All different merchant categories. Classic card-testing signature.",
            "informativeness": 1.0
        },
        "CHECK_DEVICE": {
            "result": "Single device, consistent fingerprint across all transactions.",
            "informativeness": 0.3
        },
        "VERIFY_LOCATION": {
            "result": "All transactions within 2-mile radius. Consistent location.",
            "informativeness": 0.2
        },
        "CROSS_REF_NETWORK": {
            "result": "No linked accounts found.",
            "informativeness": 0.1
        },
        "CHECK_IDENTITY": {
            "result": "Identity verification: Pending (new account, docs not yet reviewed).",
            "informativeness": 0.4
        }
    }
}

def grade(actions_taken: list, final_ruling: str, steps_used: int) -> float:
    if final_ruling != "FRAUD":
        return 0.0
    if steps_used <= 3:
        efficiency = 1.0
    elif steps_used <= 5:
        efficiency = 0.8
    elif steps_used <= 8:
        efficiency = 0.6
    else:
        efficiency = 0.4
    key_evidence = {"QUERY_HISTORY", "ANALYZE_VELOCITY"}
    evidence_score = len(key_evidence.intersection(set(actions_taken))) / len(key_evidence)
    return round(0.6 * efficiency + 0.4 * evidence_score, 2)
