# Evaluation Suite

This directory contains the automated evaluation test cases for the RAG pipelines using [DeepEval](https://github.com/confident-ai/deepeval).

## Setup

Ensure you have installed the test requirements from the root directory:
```bash
pip install -r apps/api/requirements.txt
```

You must have your `.env` file configured with `OPENAI_API_KEY` at the root of the project, as DeepEval uses OpenAI models by default to score metrics (like Faithfulness and Answer Relevancy).

## Running the Tests

To run the full suite and see the test summaries, run the helper script from the root of the project:

On Windows:
```cmd
run_evals.bat
```

On Unix/Linux:
```bash
./run_evals.sh
```

Alternatively, you can run DeepEval directly:
```bash
deepeval test run evaluation/
```
