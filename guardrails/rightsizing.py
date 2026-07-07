import math
from typing import Optional

from models import EnvPolicy, GuardrailMessage, InstancePricing, Job, MessageLevel, Usage


def rightsize(
        job: Job,
        env_policy: EnvPolicy,
        usage: Optional[Usage],
        pricing: dict[str, InstancePricing],
        current_cost: Optional[float],
) -> tuple[Optional[GuardrailMessage], Optional[float]]:
    target = env_policy.target_utilization
    if usage is None or current_cost is None or not target:
        return None, None
    if usage.p95_cpu_utilization is None or usage.avg_memory_utilization is None:
        return None, None

    current = pricing.get(job.cluster.instance_type)
    if current is None:
        return None, None

    workers = job.cluster.workers
    runtime = usage.runtime_hours_per_month

    # Smallest worker count that keeps projected utilization at or under target.
    # CPU uses p95 (the spec's guardrail). Memory has no p95 in the schema, so use avg.
    # Taking the max of the two demands so shrink happen when both side agree there is room.
    min_workers_for_cpu_p95 = math.ceil(workers * usage.p95_cpu_utilization / target)
    min_workers_for_mem_avg = math.ceil(workers * usage.avg_memory_utilization / target)
    new_workers = max(1, min(max(min_workers_for_cpu_p95, min_workers_for_mem_avg), workers))
    # Client demand less workers, no room to shrink, never add more workers, stay silent
    if new_workers >= workers:
        return None, None

    proposed_cost = new_workers * current.hourly * runtime
    savings = current_cost - proposed_cost
    if savings <= 0:
        return None, None

    projected_cpu_p95 = workers * usage.p95_cpu_utilization / new_workers
    projected_mem_avg = workers * usage.avg_memory_utilization / new_workers

    message = GuardrailMessage(
        "RIGHTSIZE_AVAILABLE",
        job.env,
        MessageLevel.WARN,
        f"Job appears over-provisioned. Reducing workers {workers} -> {new_workers} keeps "
        f"projected p95 CPU {projected_cpu_p95:.0%} and memory {projected_mem_avg:.0%} at or under the "
        f"{target:.0%} target. Estimated savings ${savings:,.2f}/month.",
        f"Reduce cluster workers from {workers} to {new_workers}.",
    )
    return message, savings
