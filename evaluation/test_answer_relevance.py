import json
import os
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

# Load the test dataset
current_dir = os.path.dirname(os.path.abspath(__file__))
test_data_path = os.path.join(current_dir, "test_data.json")

with open(test_data_path, "r") as f:
    test_data = json.load(f)

@pytest.mark.parametrize("data", test_data)
def test_answer_relevance(data):
    """
    Evaluates whether the actual output is relevant to the original input.
    Answer Relevancy checks if the generated answer directly addresses 
    the question asked by the user, without including redundant information.
    """
    test_case = LLMTestCase(
        input=data["input"],
        actual_output=data["actual_output"],
        retrieval_context=data["retrieval_context"]
    )
    
    # Threshold 0.7 means the answer must be at least 70% relevant to the input
    metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-4o", include_reason=True)
    
    assert_test(test_case, [metric])
