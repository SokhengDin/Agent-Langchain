from enum import Enum
from typing import Tuple


class TaskType(Enum):
    THEORY = "theory"
    CODING = "coding"
    MIXED = "mixed"


class ModelConfig:
    QWEN3_14B = {
        "model": "qwen3:14b",
        "num_ctx": 131072,
        "reasoning": False,
        "description": "Best for pure mathematical theory and proofs (no reasoning mode)"
    }

    QWEN3_CODER_30B = {
        "model": "qwen3-coder:30b",
        "num_ctx": 131072,
        "reasoning": False,
        "description": "Best for code implementation (no reasoning mode)"
    }

    GPT_OSS_20B = {
        "model": "gpt-oss:20b",
        "num_ctx": 131072,
        "reasoning": True,
        "description": "Supports reasoning mode for step-by-step thinking"
    }


def classify_task(message: str) -> TaskType:
    message_lower = message.lower()

    theory_keywords = [
        'prove', 'theorem', 'proof', 'derive', 'derivation',
        'explain', 'definition', 'axiom', 'theory', 'mathematical',
        'why does', 'show that', 'demonstrate that', 'lemma',
        'corollary', 'proposition', 'formal', 'rigor'
    ]

    coding_keywords = [
        'code', 'implement', 'write', 'create', 'build',
        'plot', 'visualize', 'graph', 'chart', 'histogram',
        'analyze', 'train', 'model', 'predict', 'fit',
        'dataset', 'data', 'csv', 'excel', 'pandas',
        'numpy', 'sklearn', 'regression', 'classification'
    ]

    theory_score = sum(1 for keyword in theory_keywords if keyword in message_lower)
    coding_score = sum(1 for keyword in coding_keywords if keyword in message_lower)

    if theory_score > coding_score and theory_score >= 2:
        return TaskType.THEORY
    elif coding_score > theory_score and coding_score >= 2:
        return TaskType.CODING
    else:
        return TaskType.MIXED


def select_model(
    message: str,
    require_reasoning: bool = False,
    prefer_speed: bool = False
) -> Tuple[str, int, bool, str]:
    task_type = classify_task(message)

    if require_reasoning:
        config = ModelConfig.GPT_OSS_20B
        reason = "Reasoning required: Using gpt-oss:20b (only model with reasoning support)"
    elif task_type == TaskType.THEORY:
        config = ModelConfig.QWEN3_14B
        reason = "Theory-focused: qwen3:14b for mathematical rigor"
    elif task_type == TaskType.CODING:
        config = ModelConfig.QWEN3_CODER_30B
        reason = "Code-focused: qwen3-coder:30b for implementation"
    else:
        if prefer_speed:
            config = ModelConfig.QWEN3_14B
            reason = "Mixed task (speed): qwen3:14b"
        else:
            config = ModelConfig.QWEN3_CODER_30B
            reason = "Mixed task (quality): qwen3-coder:30b"

    return (
        config["model"],
        config["num_ctx"],
        config["reasoning"],
        reason
    )
