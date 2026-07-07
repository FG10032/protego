import math
from typing import Optional

from models import Job, GuardrailMessage, InstancePricing, MessageLevel

RESERVE_VCPU = 1.0
RESERVE_MEMORY_GB = 2.0
STRANDING_THRESHOLD = 0.5


def warn_stranded_resources(
        job: Job, env: str, pricing: dict[str, InstancePricing]
) -> Optional[GuardrailMessage]:
    node = pricing.get(job.cluster.instance_type)
    if node is None:
        return None

    cores = job.spark.executor_cores
    mem = job.spark.executor_memory_gb
    if cores <= 0 or mem <= 0:
        return None

    usable_cores = node.vcpu - RESERVE_VCPU
    usable_mem = node.memory_gb - RESERVE_MEMORY_GB
    if usable_cores <= 0 or usable_mem <= 0:
        return None

    # Spark reserves per-executor memory overhead on top of executor_memory_gb.
    overhead = max(0.384, 0.10 * mem)
    exec_mem = mem + overhead

    executor_num_saturating_cores = math.floor(usable_cores / cores)
    executor_num_saturating_mem = math.floor(usable_mem / exec_mem)
    fit = min(executor_num_saturating_cores, executor_num_saturating_mem)
    if fit <= 0:
        # Executor does not fit on this node. Intentionally not flagged here: a job
        # that has been running clearly did fit, so this would mean our model
        # is wrong, not the config.
        return None

    used_cores = fit * cores
    used_mem = fit * exec_mem
    stranded_cores = 1 - used_cores / usable_cores
    stranded_mem = 1 - used_mem / usable_mem
    stranded = max(stranded_cores, stranded_mem)


    if stranded > STRANDING_THRESHOLD:
        side = "memory" if stranded_mem >= stranded_cores else "CPU"
        return GuardrailMessage(
            "STRANDED_RESOURCES",
            env,
            MessageLevel.WARN,
            f"Instance '{job.cluster.instance_type}' packs only {fit} executor(s) per node, "
            f"leaving {stranded_cores:.0%} of usable cores and {stranded_mem:.0%} of usable memory, "
            f"idling ({side}-side).",
            "Rebalance executor_cores/executor_memory_gb, or choose an instance type whose "
            "vCPU:memory ratio matches the executor shape, so each node packs more fully.",
        )
    return None
