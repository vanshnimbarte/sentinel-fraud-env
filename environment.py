from fastapi import FastAPI
from fastapi.responses import JSONResponse
from models import InvestigationAction, FraudObservation, EnvironmentState, EvidenceItem
from tasks import easy, medium, hard
import uuid

app = FastAPI(title="SENTINEL Fraud Investigation Environment")
sessions = {}

TASKS = {
    "easy_investigation": easy.CASE,
    "medium_investigation": medium.CASE,
    "hard_investigation": hard.CASE,
}
GRADERS = {
    "easy_investigation": easy.grade,
    "medium_investigation": medium.grade,
    "hard_investigation": hard.grade,
}
BUDGETS = {
    "easy_investigation": 10,
    "medium_investigation": 8,
    "hard_investigation": 7,
}
VALID_BASE_COMMANDS = [
    "QUERY_HISTORY","CHECK_DEVICE","VERIFY_LOCATION",
    "CROSS_REF_NETWORK","CHECK_IDENTITY","ANALYZE_VELOCITY"
]
VALID_RULINGS = ["FRAUD", "LEGITIMATE", "ESCALATE"]

def build_text(alert, evidence, budget):
    text = f"{alert}\n\n--- EVIDENCE GATHERED ---\n"
    if not evidence:
        text += "None yet.\n"
    else:
        for i, ev in enumerate(evidence, 1):
            text += f"{i}. [{ev.query}] {ev.result}\n"
    text += f"\n--- BUDGET: {budget} queries remaining ---\n"
    text += "\nAvailable: QUERY_HISTORY, CHECK_DEVICE, VERIFY_LOCATION, "
    text += "CROSS_REF_NETWORK, CHECK_IDENTITY, ANALYZE_VELOCITY, "
    text += "RULE FRAUD, RULE LEGITIMATE, RULE ESCALATE"
    return text

@app.post("/reset")
async def reset(task_id: str = "easy_investigation"):
    if task_id not in TASKS:
        return JSONResponse(status_code=400, content={"error": f"Unknown task: {task_id}"})
    session_id = str(uuid.uuid4())
    case = TASKS[task_id]
    sessions[session_id] = {
        "task_id": task_id, "case": case, "evidence": [],
        "actions_taken": [], "budget": BUDGETS[task_id],
        "done": False, "total_reward": 0.0, "final_ruling": None,
    }
    obs = FraudObservation(
        alert=case["alert"], evidence=[],
        budget_remaining=BUDGETS[task_id], step_count=0,
        text=build_text(case["alert"], [], BUDGETS[task_id])
    )
    return {"session_id": session_id, "observation": obs, "reward": 0.0, "done": False}

@app.post("/step")
async def step(session_id: str, action: InvestigationAction):
    s = sessions.get(session_id)
    if not s:
        return JSONResponse(status_code=404, content={"error": "Session not found"})
    if s["done"]:
        return JSONResponse(status_code=400, content={"error": "Session finished"})
    cmd = action.command.strip().upper()
    case = s["case"]
    reward = 0.0
    if cmd.startswith("RULE "):
        ruling = cmd.split(" ", 1)[1].strip()
        if ruling not in VALID_RULINGS:
            reward = -0.5
            obs_text = f"Invalid ruling. Use: RULE FRAUD / RULE LEGITIMATE / RULE ESCALATE"
        else:
            s["final_ruling"] = ruling
            s["done"] = True
            score = GRADERS[s["task_id"]](s["actions_taken"], ruling, len(s["actions_taken"]))
            reward = score * 10
            s["total_reward"] += reward
            obs = FraudObservation(
                alert=case["alert"], evidence=s["evidence"],
                budget_remaining=s["budget"], step_count=len(s["actions_taken"]),
                text=f"Case closed. Ruling: {ruling}. Score: {score:.2f}"
            )
            return {"session_id": session_id, "observation": obs,
                    "reward": round(reward, 2), "done": True, "score": score}
    elif s["budget"] <= 0:
        s["done"] = True
        reward = -5.0
        obs_text = "Budget exhausted. Case auto-closed."
    elif cmd in VALID_BASE_COMMANDS:
        ev_map = case["evidence_map"]
        if cmd in ev_map:
            if cmd in s["actions_taken"]:
                reward = -0.5
                result_text = f"[Already queried] {ev_map[cmd]['result']}"
                info = 0.0
            else:
                reward = ev_map[cmd]["informativeness"]
                result_text = ev_map[cmd]["result"]
                info = ev_map[cmd]["informativeness"]
            s["evidence"].append(EvidenceItem(query=cmd, result=result_text, informativeness=info))
            s["actions_taken"].append(cmd)
            s["budget"] -= 1
            obs_text = build_text(case["alert"], s["evidence"], s["budget"])
        else:
            reward = -0.2
            obs_text = f"No data for: {cmd}"
    else:
        reward = -0.5
        obs_text = f"Unknown command: {cmd}"
    s["total_reward"] += reward
    obs = FraudObservation(
        alert=case["alert"], evidence=s["evidence"],
        budget_remaining=s["budget"], step_count=len(s["actions_taken"]),
        text=obs_text
    )
    return {"session_id": session_id, "observation": obs,
            "reward": round(reward, 2), "done": s["done"]}

@app.get("/state")
async def state(session_id: str):
    s = sessions.get(session_id)
    if not s:
        return JSONResponse(status_code=404, content={"error": "Session not found"})
    return EnvironmentState(
        case_id=s["case"]["case_id"], task_id=s["task_id"],
        ground_truth="[HIDDEN]", is_done=s["done"],
        total_reward=round(s["total_reward"], 2)
    )

@app.get("/health")
async def health():
    return {"status": "ok", "tasks": list(TASKS.keys())}
