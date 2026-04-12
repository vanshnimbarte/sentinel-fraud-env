"""Typed OpenEnv client for the My Env v4 (echo) benchmark."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from openenv.core.client_types import StepResult
from openenv.core.env_client import EnvClient


@dataclass
class MyEnvV4Action:
    message: str


@dataclass
class MyEnvV4Observation:
    echoed_message: str


class MyEnvV4Env(EnvClient[MyEnvV4Action, MyEnvV4Observation, Dict[str, Any]]):
    """WebSocket client for the echo environment; supports from_docker_image via EnvClient."""

    def _step_payload(self, action: MyEnvV4Action) -> Dict[str, Any]:
        return asdict(action)

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[MyEnvV4Observation]:
        raw = payload.get("observation", {}) or {}
        if isinstance(raw, dict):
            echoed = (
                raw.get("echoed_message")
                or raw.get("echo")
                or raw.get("text")
                or ""
            )
        else:
            echoed = str(
                getattr(raw, "echoed_message", None)
                or getattr(raw, "echo", None)
                or getattr(raw, "text", "")
                or ""
            )
        return StepResult(
            observation=MyEnvV4Observation(echoed_message=str(echoed)),
            reward=payload.get("reward"),
            done=bool(payload.get("done", False)),
        )

    def _parse_state(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return payload
