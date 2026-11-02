"""Allow-listed, read-only tools available to the Joker executor."""
import ast
import operator
from datetime import datetime, timezone
from typing import Any


_BIN_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _calculate_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left, right = _calculate_node(node.left), _calculate_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 8:
            raise ValueError("Exponent too large")
        result = _BIN_OPS[type(node.op)](left, right)
        if abs(result) > 1e100:
            raise ValueError("Result too large")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_calculate_node(node.operand))
    raise ValueError("Only basic arithmetic is supported")


def calculator(expression: str) -> dict[str, Any]:
    if len(expression) > 120:
        raise ValueError("Expression too long")
    tree = ast.parse(expression, mode="eval")
    return {"expression": expression, "result": _calculate_node(tree.body)}


def current_time() -> dict[str, str]:
    return {"utc": datetime.now(timezone.utc).isoformat()}


TOOL_FUNCTIONS = {"calculator": calculator, "current_time": lambda: current_time()}

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Calculate a basic arithmetic expression. No code execution.",
        "parameters": {"type": "object", "properties": {"expression": {"type": "string"}},
                       "required": ["expression"], "additionalProperties": False},
    }},
    {"type": "function", "function": {
        "name": "current_time", "description": "Return the current UTC time.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    }},
]


def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Sceptyk gate: unknown tools and unexpected arguments are rejected."""
    if name not in TOOL_FUNCTIONS:
        raise ValueError(f"Tool not allowed: {name}")
    if name == "calculator":
        if set(arguments) != {"expression"} or not isinstance(arguments["expression"], str):
            raise ValueError("Invalid calculator arguments")
        return TOOL_FUNCTIONS[name](arguments["expression"])
    if arguments:
        raise ValueError("This tool accepts no arguments")
    return TOOL_FUNCTIONS[name]()
