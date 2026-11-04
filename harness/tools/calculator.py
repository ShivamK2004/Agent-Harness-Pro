"""Safe arithmetic evaluator. Never evaluates arbitrary Python code."""
from __future__ import annotations
import ast
import operator

_ALLOWED_BINOPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
                   ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
                   ast.Mod: operator.mod, ast.Pow: operator.pow}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}

class CalculatorError(ValueError):
    pass

def _eval(node, depth=0):
    if depth > 20:
        raise CalculatorError("Expression is too deeply nested")
    if isinstance(node, ast.Expression):
        return _eval(node.body, depth + 1)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        if abs(node.value) > 10**12:
            raise CalculatorError("Numeric literal is too large")
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left, right = _eval(node.left, depth + 1), _eval(node.right, depth + 1)
        if isinstance(node.op, ast.Pow) and abs(right) > 8:
            raise CalculatorError("Exponent magnitude is limited to 8")
        result = _ALLOWED_BINOPS[type(node.op)](left, right)
        if isinstance(result, (int, float)) and abs(result) > 10**15:
            raise CalculatorError("Result exceeds safety limit")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_eval(node.operand, depth + 1))
    raise CalculatorError("Only basic arithmetic (+, -, *, /, //, %, **, parentheses) is allowed")

def calculate(expression: str) -> str:
    if len(expression) > 120:
        raise CalculatorError("Expression is too long")
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _eval(parsed)
    except (SyntaxError, ZeroDivisionError, OverflowError) as exc:
        raise CalculatorError(f"Invalid arithmetic expression: {exc}") from exc
    return str(result)
