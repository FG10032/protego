from typing import Optional

from models import Job, GuardrailMessage, EnvPolicy, MessageLevel


def check_max_executor_memory(
        job: Job, env: str, env_policy: EnvPolicy,
) -> Optional[GuardrailMessage]:
    max_executor_memory_gb = env_policy.max_executor_memory_gb
    executor_memory_gb = job.spark.executor_memory_gb

    if max_executor_memory_gb is not None and executor_memory_gb > max_executor_memory_gb:
        return GuardrailMessage(
            "EXECUTOR_MEMORY_EXCEEDED",
            env,
            MessageLevel.ERROR,
            f"executor_memory_gb={executor_memory_gb} exceeds the policy maximum of {max_executor_memory_gb}.",
            f"Reduce executor_memory_gb to {max_executor_memory_gb} or fewer.",
        )
    return None
