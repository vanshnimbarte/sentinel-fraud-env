import asyncio, os
import httpx
from openai import OpenAI

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN     = os.environ.get("HF_TOKEN", "your-key-here")
ENV_URL      = os.environ.get("ENV_URL", "http://localhost:7860")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

SYSTEM_PROMPT = """You are a senior fraud investigator at a financial institution.
Investigate fraud alerts using available tools. Be strategic with your budget.

Available actions (output EXACTLY one, nothing else):
  QUERY_HISTORY, CHECK_DEVICE, VERIFY_LOCATION,
  CROSS_REF_NETWORK, CHECK_IDENTITY, ANALYZE_VELOCITY,
  RULE FRAUD, RULE LEGITIMATE, RULE ESCALATE

Output ONLY the action name. No explanation."""

async def run_task(task_id: str):
    async with httpx.AsyncClient(timeout=60) as http:
        r = await http.post(f"{ENV_URL}/reset", params={"task_id": task_id})
        data = r.json()
        session_id = data["session_id"]
        obs = data["observation"]["text"]
        total_reward = 0.0
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        print(f'[START] task_id="{task_id}" session_id="{session_id}"')
        done = False
        step_num = 0
        while not done and step_num < 12:
            messages.append({"role": "user", "content": obs})
            resp = client.chat.completions.create(
                model=MODEL_NAME, messages=messages,
                max_tokens=20, temperature=0.0
            )
            action = resp.choices[0].message.content.strip().upper()
            messages.append({"role": "assistant", "content": action})
            r = await http.post(
                f"{ENV_URL}/step",
                params={"session_id": session_id},
                json={"command": action}
            )
            step_data = r.json()
            reward = step_data["reward"]
            done   = step_data["done"]
            obs    = step_data["observation"]["text"]
            total_reward += reward
            step_num += 1
            print(f'[STEP] step={step_num} action="{action}" reward={reward} done={done}')
        print(f'[END] task_id="{task_id}" total_reward={round(total_reward,2)} steps={step_num}')
        return total_reward

async def main():
    for task in ["easy_investigation","medium_investigation","hard_investigation"]:
        await run_task(task)
        print()

if __name__ == "__main__":
    asyncio.run(main())
