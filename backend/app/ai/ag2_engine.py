import json
from typing import Any, Dict, Optional

from autogen import ConversableAgent, UserProxyAgent

from ..core.config import settings


class AgenticDecisionEngine:
    """AG2-powered decision engine that wraps a ConversableAgent.

    The engine orchestrates a short autonomous conversation between a controller
    (UserProxyAgent) and an assistant (ConversableAgent) configured to speak JSON.
    The assistant is backed by Groq's OpenAI-compatible endpoint so that we can
    benefit from AG2's tooling while keeping Groq as the underlying model.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self._assistant: Optional[ConversableAgent] = None
        self._controller: Optional[UserProxyAgent] = None

    @property
    def is_configured(self) -> bool:
        return bool(settings.GROQ_API_KEY)

    def _init_agents(self) -> None:
        if self._assistant is not None and self._controller is not None:
            return

        if not self.is_configured:
            # Groq credentials missing; AG2 conversation is disabled.
            return

        llm_config = {
            "config_list": [
                {
                    "model": settings.GROQ_MODEL,
                    "api_key": settings.GROQ_API_KEY,
                    "base_url": settings.GROQ_BASE_URL,
                }
            ],
            "temperature": settings.GROQ_TEMPERATURE,
            "timeout": 120,
        }

        system_message = [
            "You are an autonomous logistics decision-maker.",
            "Always respond with valid JSON that exactly matches the schema provided in the prompt.",
            "Do not include any additional commentary outside the JSON object.",
            "If you cannot comply, respond with an object {\"error\": \"reason\"}.",
        ]

        self._assistant = ConversableAgent(
            name=f"{self.agent_name}_assistant",
            system_message=system_message,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=settings.AGENT_AUTONOMOUS_TURNS,
            llm_config=llm_config,
            code_execution_config={"use_docker": False},
            silent=True,
        )
        self._controller = UserProxyAgent(
            name=f"{self.agent_name}_controller",
            human_input_mode="NEVER",
            system_message="You provide contextual information to the assistant and never request human input.",
            code_execution_config={"use_docker": False},
            silent=True,
        )

    async def a_make_decision(
        self,
        *,
        context: Dict[str, Any],
        prompt: str,
        response_format: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Run an AG2 conversation and return the parsed JSON payload."""

        self._init_agents()
        if self._assistant is None or self._controller is None:
            return None

        # Compose a single-turn message for the assistant.
        message = json.dumps(
            {
                "context": context,
                "instructions": prompt,
                "response_schema": response_format,
            },
            indent=2,
        )

        chat_result = await self._controller.a_initiate_chat(
            self._assistant,
            clear_history=True,
            silent=True,
            max_turns=settings.AGENT_AUTONOMOUS_TURNS,
            message=f"Use the given context and instructions. Reply with JSON:\n{message}",
        )

        raw_reply = self._extract_last_content(chat_result.chat_history)
        if not raw_reply:
            return None

        parsed = self._try_parse_json(raw_reply)
        return parsed

    @staticmethod
    def _extract_last_content(chat_history: list[dict[str, Any]]) -> Optional[str]:
        if not chat_history:
            return None

        last_msg = chat_history[-1]
        content = last_msg.get("content")
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            # OpenAI-compatible responses sometimes return a list of dict parts.
            text_parts = []
            for part in content:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(str(part["text"]))
            return "".join(text_parts).strip() if text_parts else None
        return None

    @staticmethod
    def _try_parse_json(payload: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            # Attempt to recover by extracting the last JSON object.
            start = payload.find("{")
            end = payload.rfind("}")
            if start != -1 and end != -1 and start < end:
                snippet = payload[start : end + 1]
                try:
                    return json.loads(snippet)
                except json.JSONDecodeError:
                    return None
            return None
