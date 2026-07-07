from typing import Optional

from models import Job, GuardrailMessage, EnvPolicy, MessageLevel, Usage


def warn_low_utilization(
        job: Job, env: str, env_policy: EnvPolicy, usages: dict[str, Usage]
) -> Optional[GuardrailMessage]:
    usage = usages.get(job.name)
    if not usage:
        return None

    threshold = env_policy.warn_if_estimated_utilization_below
    avg_cpu = usage.avg_cpu_utilization
    if threshold and avg_cpu is not None and avg_cpu < threshold:
        return GuardrailMessage(
            "LOW_UTILIZATION",
            env,
            MessageLevel.WARN,
            f"Average CPU utilization {avg_cpu:.0%} is below the {threshold:.0%} threshold; the job may be over-provisioned.",
            "Review the rightsizing recommendation to reduce workers or instance size.",
        )
    return None
