"""
Real-time agent activity logging via LangChain callbacks.

Provides verbose, human-readable console output showing what each agent
is doing: LLM thinking, tool calls, tool results, and errors.
"""

import json
import logging
import time
from typing import Any, Optional
from uuid import UUID

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import LLMResult

logger = logging.getLogger("app.agent_activity")


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    ORCHESTRATOR = "\033[1;35m"  # Bold Magenta
    ANALYZER = "\033[1;36m"  # Bold Cyan
    UPDATER = "\033[1;33m"  # Bold Yellow

    THINKING = "\033[34m"  # Blue
    TOOL_CALL = "\033[32m"  # Green
    TOOL_RESULT = "\033[90m"  # Gray
    ERROR = "\033[1;31m"  # Bold Red
    SUCCESS = "\033[1;32m"  # Bold Green


AGENT_STYLES = {
    "orchestrator": {"prefix": "ORCHESTRATOR", "color": Colors.ORCHESTRATOR},
    "analyzer": {"prefix": "ANALYZER    ", "color": Colors.ANALYZER},
    "updater": {"prefix": "UPDATER     ", "color": Colors.UPDATER},
}


def _truncate(text: str, max_len: int = 200) -> str:
    text = str(text).replace("\n", " ").strip()
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def _format_tool_args(input_str: str, max_len: int = 150) -> str:
    try:
        args = json.loads(input_str)
        if isinstance(args, dict):
            parts = []
            for k, v in args.items():
                v_str = str(v)
                if len(v_str) > 60:
                    v_str = v_str[:60] + "..."
                parts.append(f"{k}={v_str}")
            return ", ".join(parts)
    except (json.JSONDecodeError, TypeError):
        pass
    return _truncate(input_str, max_len)


def _extract_tool_result_summary(output: Any, max_len: int = 200) -> str:
    output_str = str(output)
    try:
        data = json.loads(output_str)
        if isinstance(data, dict):
            summary_parts = []
            for key in [
                "status",
                "message",
                "repo_path",
                "language",
                "package_manager",
                "outdated_count",
                "total_updates",
                "pr_url",
                "issue_url",
                "branch_name",
                "succeeded",
                "from_cache",
            ]:
                if key in data:
                    val = str(data[key])
                    if len(val) > 80:
                        val = val[:80] + "..."
                    summary_parts.append(f"{key}={val}")
            if summary_parts:
                return ", ".join(summary_parts[:5])
    except (json.JSONDecodeError, TypeError):
        pass
    return _truncate(output_str, max_len)


class AgentActivityHandler(BaseCallbackHandler):
    """
    LangChain callback handler that provides verbose, real-time logging
    of agent activity to console and Python logging framework.

    Usage:
        handler = AgentActivityHandler("orchestrator")
        agent.invoke({"messages": [...]}, config={"callbacks": [handler]})
    """

    def __init__(self, agent_name: str, job_id: Optional[str] = None):
        self.agent_name = agent_name
        self.job_id = job_id
        self._style = AGENT_STYLES.get(
            agent_name, {"prefix": agent_name.upper(), "color": Colors.BOLD}
        )
        self._llm_start_time: Optional[float] = None
        self._tool_start_times: dict[UUID, float] = {}
        self.activity_log: list[dict[str, Any]] = []

    def _prefix(self) -> str:
        color = self._style["color"]
        prefix = self._style["prefix"]
        return f"{color}[{prefix}]{Colors.RESET}"

    def _log_activity(self, event_type: str, detail: str, **extra: Any) -> None:
        entry = {
            "agent": self.agent_name,
            "event": event_type,
            "detail": detail,
            "job_id": self.job_id,
            **extra,
        }
        self.activity_log.append(entry)
        logger.debug(json.dumps(entry))

    # ── LLM / Chat Model Events ─────────────────────────────────

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        self._llm_start_time = time.time()
        msg_count = sum(len(batch) for batch in messages)
        print(
            f"{self._prefix()} {Colors.THINKING}Thinking... "
            f"({msg_count} messages in context){Colors.RESET}"
        )
        self._log_activity("llm_start", f"Chat model invoked with {msg_count} messages")

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        elapsed = ""
        if self._llm_start_time:
            elapsed = f" ({time.time() - self._llm_start_time:.1f}s)"
            self._llm_start_time = None

        token_info = ""
        if response.llm_output and "usage" in response.llm_output:
            usage = response.llm_output["usage"]
            token_info = (
                f" | tokens: {usage.get('input_tokens', '?')} in, "
                f"{usage.get('output_tokens', '?')} out"
            )

        print(
            f"{self._prefix()} {Colors.DIM}LLM responded{elapsed}{token_info}"
            f"{Colors.RESET}"
        )
        self._log_activity("llm_end", f"LLM responded{elapsed}{token_info}")

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        print(f"{self._prefix()} {Colors.ERROR}LLM ERROR: {error}{Colors.RESET}")
        self._log_activity("llm_error", str(error))

    # ── Tool Events ──────────────────────────────────────────────

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._tool_start_times[run_id] = time.time()
        tool_name = serialized.get("name", "unknown_tool")
        formatted_args = _format_tool_args(input_str)

        print(
            f"{self._prefix()} {Colors.TOOL_CALL}>>> Calling tool: "
            f"{Colors.BOLD}{tool_name}{Colors.RESET}"
        )
        if formatted_args:
            print(
                f"{self._prefix()} {Colors.DIM}    args: {formatted_args}{Colors.RESET}"
            )

        self._log_activity("tool_start", tool_name, args=_truncate(input_str, 500))

    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        elapsed = ""
        if run_id in self._tool_start_times:
            elapsed = f" ({time.time() - self._tool_start_times.pop(run_id):.1f}s)"

        summary = _extract_tool_result_summary(output)

        output_str = str(output)
        is_error = '"status": "error"' in output_str or '"status":"error"' in output_str

        if is_error:
            print(
                f"{self._prefix()} {Colors.ERROR}<<< Tool returned error{elapsed}: "
                f"{summary}{Colors.RESET}"
            )
        else:
            print(
                f"{self._prefix()} {Colors.TOOL_RESULT}<<< Tool result{elapsed}: "
                f"{summary}{Colors.RESET}"
            )

        self._log_activity("tool_end", summary, elapsed=elapsed)

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        self._tool_start_times.pop(run_id, None)
        print(
            f"{self._prefix()} {Colors.ERROR}<<< Tool EXCEPTION: {error}{Colors.RESET}"
        )
        self._log_activity("tool_error", str(error))

    # ── Agent Events ─────────────────────────────────────────────

    def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        print(
            f"{self._prefix()} {Colors.BOLD}Agent decided: {action.tool}{Colors.RESET}"
        )
        self._log_activity("agent_action", action.tool)

    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        summary = _truncate(finish.return_values.get("output", str(finish.log)), 300)
        print(
            f"{self._prefix()} {Colors.SUCCESS}Agent finished: {summary}{Colors.RESET}"
        )
        self._log_activity("agent_finish", summary)

    # ── Chain Events (minimal, to avoid noise) ───────────────────

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        print(f"{self._prefix()} {Colors.ERROR}Chain error: {error}{Colors.RESET}")
        self._log_activity("chain_error", str(error))
