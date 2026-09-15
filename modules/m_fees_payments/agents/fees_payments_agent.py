import json
import logging
from typing import TypedDict, Annotated, Sequence, Any, Optional
from langgraph.graph import StateGraph, START, END
import operator

from langchain_core.utils.function_calling import convert_to_openai_tool
from xsc_lib.xsc_lib_common.nim_adapter import NIMAdapter, LLMMessage
from modules.m_fees_payments.tools.fees_payments_tools import get_fees_payments_agent_tools
from modules.m_fees_payments.capabilities.fees_payments_caps import FeesPaymentsCapabilities

logger = logging.getLogger(__name__)

class FeesPaymentsAgentState(TypedDict):
    correlation_id: str
    request_payload: Optional[dict]
    messages: Annotated[list[LLMMessage], operator.add]
    iteration: int
    max_iterations: int
    final_result: Optional[dict]
    error: Optional[str]

class FeesPaymentsAgent:
    def __init__(self, caps: FeesPaymentsCapabilities, nim_adapter: NIMAdapter):
        self.caps = caps
        self.nim_adapter = nim_adapter
        self.tools = {t.name: t for t in get_fees_payments_agent_tools(self.caps)}
        self.openai_tools = [convert_to_openai_tool(t) for t in self.tools.values()]
        
        # System Prompt enforces Phase 4.8 F&P rules
        self.system_prompt = LLMMessage(role="system", content=(
            "You are the Fees & Payments Agent for the OneApp Agentic Platform. "
            "Your domain responsibility is exclusively Fees & Payments. "
            "You must execute requested student payment operations using your authorized deterministic tools. "
            "You MUST NOT invent payment reasons or decide Admissions business rules. "
            "Workflow to follow:\n"
            "1. validate_payment_request on the incoming request payload.\n"
            "2. If valid, collect_student_payment.\n"
            "3. Return the structured payment result as your final output."
        ))
        
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(FeesPaymentsAgentState)
        
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("execute_tools", self._execute_tools_node)
        
        workflow.add_edge(START, "agent")
        
        # Conditional edge: if tool calls are present, go to execute_tools, else END
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "execute_tools",
                "end": END
            }
        )
        
        workflow.add_edge("execute_tools", "agent")
        
        return workflow.compile()

    def _agent_node(self, state: FeesPaymentsAgentState) -> dict:
        iteration = state.get("iteration", 0)
        max_iterations = state.get("max_iterations", 5)
        
        if iteration >= max_iterations:
            return {"error": "Max iterations reached", "final_result": {"status": "error", "message": "Max iterations reached"}}
            
        messages = [self.system_prompt] + state["messages"]
        
        try:
            trace_context = {
                "correlation_id": state.get("correlation_id"),
                "agent_identity": "agent.fees_payments.primary",
                "domain": "Fees & Payments"
            }
            response = self.nim_adapter.generate_response(messages, tools=self.openai_tools, trace_context=trace_context)
        except Exception as e:
            return {"error": str(e), "final_result": {"status": "error", "message": f"LLM Error: {str(e)}" }}
            
        if response.tool_calls:
            tool_calls_str = json.dumps([tc.model_dump() for tc in response.tool_calls])
            assistant_msg = LLMMessage(role="assistant", content=f"Calling tools: {tool_calls_str}")
            return {
                "messages": [assistant_msg], 
                "iteration": iteration + 1,
            }
        else:
            assistant_msg = LLMMessage(role="assistant", content=response.content or "")
            try:
                final_res = json.loads(response.content)
            except:
                final_res = {"status": "success", "content": response.content}
            return {"messages": [assistant_msg], "final_result": final_res, "iteration": iteration + 1}

    def _execute_tools_node(self, state: FeesPaymentsAgentState) -> dict:
        last_msg = state["messages"][-1]
        try:
            tool_calls_data = json.loads(last_msg.content.replace("Calling tools: ", ""))
        except:
            return {"error": "Failed to parse tool calls"}
            
        tool_results = []
        for tc in tool_calls_data:
            tool_name = tc.get("function_name")
            args_str = tc.get("arguments", "{}")
            try:
                args = json.loads(args_str)
            except json.JSONDecodeError:
                args = {}
                
            if tool_name in self.tools:
                tool = self.tools[tool_name]
                try:
                    res = tool.invoke(args)
                    tool_results.append(f"Tool {tool_name} returned: {json.dumps(res)}")
                except Exception as e:
                    tool_results.append(f"Tool {tool_name} failed: {str(e)}")
            else:
                tool_results.append(f"Tool {tool_name} not authorized.")
                
        observation_msg = LLMMessage(role="user", content="\n".join(tool_results))
        return {"messages": [observation_msg]}

    def _should_continue(self, state: FeesPaymentsAgentState) -> str:
        if state.get("error") or state.get("final_result"):
            return "end"
        last_msg = state["messages"][-1]
        if last_msg.role == "assistant" and "Calling tools:" in last_msg.content:
            return "continue"
        return "end"

    def invoke(self, inputs: dict) -> dict:
        initial_state = {
            "correlation_id": inputs.get("correlation_id", "default-corr"),
            "request_payload": inputs.get("request_payload"),
            "messages": inputs.get("messages", []),
            "iteration": 0,
            "max_iterations": 5,
            "final_result": None,
            "error": None
        }
        return self.graph.invoke(initial_state)
