import json
import os
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric

# Load the test dataset
current_dir = os.path.dirname(os.path.abspath(__file__))
test_data_path = os.path.join(current_dir, "test_data.json")

with open(test_data_path, "r") as f:
    test_data = json.load(f)

@pytest.mark.parametrize("data", test_data)
def test_faithfulness(data):
    """
    Evaluates whether the actual output is faithful to the retrieval context.
    Faithfulness checks if there are any hallucinated claims in the output
    that cannot be deduced from the retrieved context.
    """
    test_case = LLMTestCase(
        input=data["input"],
        actual_output=data["actual_output"],
        retrieval_context=data["retrieval_context"]
    )
    
    # Threshold 0.7 means 70% of the claims in actual_output must be supported
    metric = FaithfulnessMetric(threshold=0.7, model="gpt-4o", include_reason=True)
    
    assert_test(test_case, [metric])
