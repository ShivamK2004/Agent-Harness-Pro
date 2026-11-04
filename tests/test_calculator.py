import pytest
from harness.tools.calculator import calculate, CalculatorError

def test_basic_arithmetic():
    assert calculate("125 * 8 + 40") == "1040"

def test_parentheses_and_power():
    assert calculate("(10 + 2) ** 2") == "144"

def test_rejects_function_calls():
    with pytest.raises(CalculatorError):
        calculate("__import__('os').system('whoami')")

def test_rejects_large_exponent():
    with pytest.raises(CalculatorError):
        calculate("2 ** 100")

def test_natural_language_multiplication_routing():
    from harness.tools.task_router import classify_task, extract_arithmetic_expression
    task = "What is 25 multiplied by 4?"
    assert classify_task(task) == "calculation"
    assert extract_arithmetic_expression(task) == "25 * 4"
    assert calculate(extract_arithmetic_expression(task)) == "100"

def test_general_question_does_not_force_knowledge_retrieval():
    from harness.tools.task_router import classify_task
    assert classify_task("Tell me about yourself") == "general"
