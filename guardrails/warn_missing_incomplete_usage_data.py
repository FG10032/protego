from typing import Optional

from models import Job, GuardrailMessage, MessageLevel, Usage


def warn_missing_incomplete_usage_data(
        job: Job, env: str, usages: dict[str, Usage]
) -> Optional[GuardrailMessage]:
    if job.name not in usages:
        return GuardrailMessage(
            "MISSING_USAGE_DATA",
            env,
            MessageLevel.WARN,
            "No historical usage metrics found for this job; utilization and worker rightsizing could not be assessed.",
            "Provide usage metrics to enable utilization checks and rightsizing.",
        )

    usage = usages[job.name]
    missing = [k for k in Usage().__dict__.keys() if getattr(usage, k) is None]
    if missing:
        return GuardrailMessage(
            "INCOMPLETE_USAGE_DATA",
            env,
            MessageLevel.WARN,
            f"Usage metrics are incomplete (missing: {', '.join(missing)}). Worker rightsizing will be skipped.",
            "Provide the missing usage metrics.",
        )
    return None
