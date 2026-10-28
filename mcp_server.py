# -*- coding: utf-8 -*-
"""
GenPark Reasoning Backtracking Counterfactual Auditor MCP Server
Exposes thought loop detection and checkpoint rollback tools via JSON-RPC 2.0 over STDIO.
"""

import sys
import json
from client import GenParkReasoningBacktrackingCounterfactualAuditor

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-reasoning-backtracking-counterfactual-auditor", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "audit_reasoning_trace",
                        "description": "Detects reasoning loops, deadlocks, and logical contradictions to execute non-destructive checkpoint rollbacks.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "reasoning_trace_steps": {
                                    "type": "array",
                                    "items": {"type": "object"}
                                }
                            },
                            "required": ["reasoning_trace_steps"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "audit_reasoning_trace":
            auditor = GenParkReasoningBacktrackingCounterfactualAuditor()
            res = auditor.audit_reasoning_trace(args.get("reasoning_trace_steps", []))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Method '{method}' not supported"}}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("MCP Server Discovery Test OK")
        aud = GenParkReasoningBacktrackingCounterfactualAuditor()
        test_res = aud.audit_reasoning_trace([
            {"content": "Let x = 10"},
            {"content": "Substitute x into equation"},
            {"content": "Wait, this contradicts our initial assumption that x > 20"}
        ])
        print(f"Test Verdict: {test_res['trace_health_verdict']}")
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
