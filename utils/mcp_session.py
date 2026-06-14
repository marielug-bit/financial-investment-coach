"""Persistent MCP session — shared across all pages via st.session_state."""
import asyncio
import threading
import streamlit as st


class MCPSession:
    """Keeps all 6 MCP servers alive in a background thread."""

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._agent = None
        self._client = None
        self.tool_names: list[str] = []
        self._ready = threading.Event()
        self.error: str | None = None

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        asyncio.run_coroutine_threadsafe(self._init(), self._loop)
        if not self._ready.wait(timeout=45):
            self.error = self.error or "MCP servers did not respond within 45 s"

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _init(self):
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.agents.orchestrator import _server_config, _get_llm, _get_system_prompt
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from langchain.agents import create_agent
        try:
            self._client = MultiServerMCPClient(_server_config())
            tools = await self._client.get_tools()
            self.tool_names = [t.name for t in tools]
            self._agent = create_agent(_get_llm(), tools, system_prompt=_get_system_prompt())
        except Exception as e:
            self.error = str(e)
        finally:
            self._ready.set()

    def ask(self, question: str, timeout: int = 120) -> str:
        from src.agents.orchestrator import _extract_answer
        from langchain_core.messages import HumanMessage

        async def _run():
            return _extract_answer(
                await self._agent.ainvoke({"messages": [HumanMessage(content=question)]})
            )
        return asyncio.run_coroutine_threadsafe(_run(), self._loop).result(timeout=timeout)

    def run_weekly_report(self, timeout: int = 180) -> str:
        prompt = (
            "Generate and send the weekly coach report. "
            "1. Search documents for key findings. "
            "2. Get current prices for tracked tickers. "
            "3. Get the paper portfolio summary. "
            "4. Identify 3 investment opportunities. "
            "5. Send to the 'weekly' email group using send_weekly_coach_report. "
            "Write in plain English for a beginner."
        )
        return self.ask(prompt, timeout=timeout)

    def cleanup(self):
        self._loop.call_soon_threadsafe(self._loop.stop)


def get_mcp() -> MCPSession | None:
    return st.session_state.get("_mcp")


def start_mcp() -> MCPSession:
    if st.session_state.get("_mcp") is None:
        st.session_state._mcp = MCPSession()
    return st.session_state._mcp
