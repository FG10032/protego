from typing import Optional

from models import Job, GuardrailMessage, EnvPolicy, MessageLevel


def check_dynamic_allocation(
        job: Job, env: str, env_policy: EnvPolicy,
) -> Optional[GuardrailMessage]:
    dynamic_allocation = job.spark.dynamic_allocation
    require_dynamic_allocation_for_batch = env_policy.require_dynamic_allocation_for_batch

    if require_dynamic_allocation_for_batch and job.type == "batch" and not dynamic_allocation:
        return GuardrailMessage(
            "DYNAMIC_ALLOCATION_REQUIRED",
            env,
            MessageLevel.ERROR,
            "Batch job has dynamic allocation disabled but policy requires it.",
            "Set spark.dynamic_allocation to true for batch job.",
        )
    return None
