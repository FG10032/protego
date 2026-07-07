from typing import Optional

from models import Job, GuardrailMessage, EnvPolicy, InstancePricing, MessageLevel


def check_unknown_instance_type(
        job: Job, env: str, env_policy: EnvPolicy, pricing: dict[str, InstancePricing]
) -> Optional[GuardrailMessage]:
    instance_type = job.cluster.instance_type

    if instance_type not in pricing:
        if env_policy.fail_on_unknown_instance_type:
            return GuardrailMessage(
                "UNKNOWN_INSTANCE_TYPE",
                env,
                MessageLevel.ERROR,
                f"Instance type '{instance_type}' is not a known type from the pricing list.",
                "Use a known instance type from the pricing list.",
            )
        else:
            return GuardrailMessage(
                "UNKNOWN_INSTANCE_TYPE",
                env,
                MessageLevel.WARN,
                f"Instance type '{instance_type}' is not a known type from pricing list, cost cannot be verified.",
                "Add this instance type to the pricing list or use a known type.",
            )
    return None
