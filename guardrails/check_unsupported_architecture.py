from typing import Optional

from models import Job, GuardrailMessage, EnvPolicy, MessageLevel


def check_unsupported_architecture(
        job: Job, env: str, env_policy: EnvPolicy,
) -> Optional[GuardrailMessage]:
    architecture = job.cluster.architecture
    allowed_architectures = env_policy.allowed_architectures

    if allowed_architectures and architecture and architecture not in allowed_architectures:
        return GuardrailMessage(
            "UNSUPPORTED_ARCHITECTURE",
            env,
            MessageLevel.ERROR,
            f"Architecture '{architecture}' is not allowed (allowed: {', '.join(allowed_architectures)}).",
            f"Switch to one of: {', '.join(allowed_architectures)}.",
        )
    return None
