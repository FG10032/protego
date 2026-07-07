from typing import Optional

import guardrails
from models import (
    EnvPolicy,
    InstancePricing,
    Job,
    JobResult,
    MessageLevel,
    Policy,
    Usage,
)


def estimate_monthly_cost(
        job: Job, usage: Optional[Usage], pricing: dict[str, InstancePricing]
) -> Optional[float]:
    node = pricing.get(job.cluster.instance_type)
    if node is None or usage is None or usage.runtime_hours_per_month is None:
        return None
    return job.cluster.workers * node.hourly * usage.runtime_hours_per_month


def evaluate_job(job: Job, policy: Policy, usages: dict[str, Usage]) -> JobResult:
    env = job.env
    env_policy = policy.policies.get(env) or EnvPolicy()
    pricing = policy.pricing
    usage = usages.get(job.name)
    cost = estimate_monthly_cost(job, usage, pricing)

    guardrail_messages = [
        guardrails.check_unknown_instance_type(job, env, env_policy, pricing),
        guardrails.check_unsupported_architecture(job, env, env_policy),
        guardrails.check_max_executor_cores(job, env, env_policy),
        guardrails.check_max_executor_memory(job, env, env_policy),
        guardrails.check_dynamic_allocation(job, env, env_policy),
        guardrails.warn_non_preferred_architecture(job, env, env_policy, pricing),
        guardrails.warn_stranded_resources(job, env, pricing),
        guardrails.warn_missing_incomplete_usage_data(job, env, usages),
        guardrails.warn_low_utilization(job, env, env_policy, usages),
    ]
    rightsize_message, savings = guardrails.rightsize(job, env_policy, usage, pricing, cost)

    messages = [m for m in guardrail_messages + [rightsize_message] if m is not None]
    levels = {m.level for m in messages}
    if MessageLevel.ERROR in levels:
        status = "fail"
    elif MessageLevel.WARN in levels:
        status = "warn"
    else:
        status = "pass"

    return JobResult(
        name=job.name,
        env=env,
        status=status,
        messages=messages,
        estimated_monthly_cost=cost,
        potential_monthly_savings=savings,
    )
