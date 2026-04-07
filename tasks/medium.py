CASE = {
    "case_id": "MED-001",
    "alert": """
ALERT: Large transaction flagged on Account #221847
- $3,400 wire transfer to international account (Romania)
- Account has 2+ years of clean history, good credit score
- Account holder: Sarah Mitchell, 34, Chicago IL
- Transaction time: 2:17 AM local
This is an established customer. Proceed carefully.
""",
    "ground_truth": "FRAUD",
    "fraud_type": "account_takeover",
    "evidence_map": {
        "CHECK_DEVICE": {
            "result": "DEVICE MISMATCH: Previous 847 transactions all from iPhone 12 "
                      "(device_id: A7F2). This transaction: Samsung Galaxy S24 (device_id: NEW-003). "
                      "Device first seen: 47 minutes ago.",
            "informativeness": 1.0
        },
        "VERIFY_LOCATION": {
            "result": "IMPOSSIBLE TRAVEL: Last login 3 hours ago from Chicago, IL. "
                      "Current login from Bucharest, Romania. "
                      "Distance: 5,272 miles. Impossible in 3 hours.",
            "informativeness": 1.0
        },
        "CHECK_IDENTITY": {
            "result": "CREDENTIAL CHANGE: Password reset requested 2 hours ago via email link. "
                      "Email opened from IP matching Romania location.",
            "informativeness": 0.9
        },
        "QUERY_HISTORY": {
            "result": "Clean 2-year history. 847 transactions, avg $145. "
                      "No prior international transfers. No prior late-night transactions.",
            "informativeness": 0.5
        },
        "ANALYZE_VELOCITY": {
            "result": "Single large transaction. No velocity concern.",
            "informativeness": 0.2
        },
        "CROSS_REF_NETWORK": {
            "result": "Receiving account (Romania) flagged in 3 prior fraud cases this month.",
            "informativeness": 0.8
        }
    }
}

def grade(actions_taken: list, final_ruling: str, steps_used: int) -> float:
    if final_ruling != "FRAUD":
        return 0.0
    smoking_guns = {"CHECK_DEVICE", "VERIFY_LOCATION", "CHECK_IDENTITY"}
    evidence_found = len(smoking_guns.intersection(set(actions_taken)))
    if evidence_found < 2:
        return 0.3
    efficiency = 1.0 if steps_used <= 5 else (0.8 if steps_used <= 8 else 0.6)
    evidence_completeness = evidence_found / 3
    return round(0.5 * efficiency + 0.5 * evidence_completeness, 2)
