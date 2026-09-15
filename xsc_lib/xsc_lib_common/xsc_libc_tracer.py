import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

class DevelopmentTracer:
    """
    Development-only forensic reasoning tracer.
    Isolates raw model reasoning (CoT) away from canonical production logs, SDRs, and DB state.
    """
    
    # In a real setup, this might be configurable via AppConfig, but we hardcode 
    # the POC dev traces directory to ensure it is always isolated.
    TRACE_FILE = os.path.join(os.getcwd(), "data", "dev_traces", "reasoning_traces.jsonl")

    @classmethod
    def _ensure_dir(cls):
        os.makedirs(os.path.dirname(cls.TRACE_FILE), exist_ok=True)

    @classmethod
    def log_trace(
        cls, 
        reasoning_available: bool, 
        reasoning_content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Logs a reasoning trace.
        Never exposed to APIs or SDRs. 
        """
        cls._ensure_dir()
        
        ctx = context or {}
        
        trace_record = {
            "TraceID": str(uuid.uuid4()),
            "CorrelationID": ctx.get("correlation_id"),
            "DecisionID": ctx.get("decision_id"), # Only populated if available
            "AgentIdentity": ctx.get("agent_identity", "unknown"),
            "Domain": ctx.get("domain", "unknown"),
            "Model": ctx.get("model", "unknown"),
            "Timestamp": datetime.now(timezone.utc).isoformat(),
            "ReasoningAvailable": reasoning_available,
            "ReasoningContent": reasoning_content
        }

        with open(cls.TRACE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace_record) + "\n")
