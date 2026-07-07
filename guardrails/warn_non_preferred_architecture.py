from typing import Optional

from models import Job, GuardrailMessage, EnvPolicy, InstancePricing, MessageLevel


def warn_non_preferred_architecture(
        job: Job, env: str, env_policy: EnvPolicy, pricing: dict[str, InstancePricing]
) -> Optional[GuardrailMessage]:
    instance_type = job.cluster.instance_type
    architecture = job.cluster.architecture
    preferred_architecture = env_policy.preferred_architecture
    if preferred_architecture and architecture and architecture != preferred_architecture:
        equivalent = _find_equivalent(instance_type, preferred_architecture, pricing)
        if equivalent:
            return GuardrailMessage(
                "NON_PREFERRED_ARCHITECTURE",
                env,
                MessageLevel.WARN,
                f"Job runs on '{architecture}' but the preferred architecture is "
                f"'{preferred_architecture}'. Compatible option '{equivalent}' is available.",
                f"Suggest migrating to {equivalent} ({preferred_architecture}). Please validate "
                f"workload compatibility and rebuild historical utilization before committing.",
            )
    return None


def _find_equivalent(
        instance_type: str,
        preferred_architecture: str,
        pricing: dict[str, InstancePricing],
) -> Optional[str]:
    current = pricing.get(instance_type)
    if current is None:
        return None
    for name, spec in pricing.items():
        if (
                spec.architecture == preferred_architecture and
                spec.vcpu == current.vcpu and
                spec.memory_gb == current.memory_gb
        ):
            return name
    return None
