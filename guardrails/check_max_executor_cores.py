from typing import Optional

from models import Job, GuardrailMessage, EnvPolicy, MessageLevel


def check_max_executor_cores(
        job: Job, env: str, env_policy: EnvPolicy,
) -> Optional[GuardrailMessage]:
    max_executor_cores = env_policy.max_executor_cores
    executor_cores = job.spark.executor_cores

    if max_executor_cores is not None and executor_cores > max_executor_cores:
        return GuardrailMessage(
            "EXECUTOR_CORES_EXCEEDED",
            env,
            MessageLevel.ERROR,
            f"spark.executor_cores={executor_cores} exceeds the policy maximum of {max_executor_cores}.",
            f"Reduce executor_cores to {max_executor_cores} or fewer.",
        )
    return None
