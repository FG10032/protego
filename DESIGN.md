# Design Notes

## Architecture

- `models/`: typed objects, top level ones are `Job`, `Polycy`, `Usage` and `JobResult`. Rests are just build blocks.
- `loaders/`: parse and validate the YAML/JSON inputs into corresponding models, with located error about field existence.
- `guardrails/`: pure functions, contains decision logic about rules checks, include blocking checks, the warnings, and rightsizing.
- `evaluate.py`: runs every check for a job, union the guardrail results into final job status, calculate costs and savings.
- `pipeline_review/`: the CLI entry point.

## Which violations block, and why

A job fails if it's unsafe or unpractical to deploy:
- **`UNKNOWN_INSTANCE_TYPE`**: blocks only where policy sets `fail_on_unknown_instance_type`.
  Assume `fail_on_unknown_instance_type` exists for different env use case, 
  In production this is a real risk due to unrecognized hardware, and we can't compute cost either. 
  In test environments it is ignorable.
- **`UNSUPPORTED_ARCHITECTURE`**: architecture not on the allowed list, should block since giving
  unsupported arch to clients could lead to huge risk.
- **`EXECUTOR_CORES_EXCEEDED` / `EXECUTOR_MEMORY_EXCEEDED`**: executor sizing over the
  policy ceiling, oversized executors pack badly onto nodes and cause scheduling failures.
- **`DYNAMIC_ALLOCATION_REQUIRED`**: a production batch job with dynamic allocation off
  holds a fixed allocation for the whole run, the most common quiet source of waste.

what does not block:
- env with no policy
- **`NON_PREFERRED_ARCHITECTURE`**
- **`LOW_UTILIZATION`**
- **`MISSING`/`INCOMPLETE_USAGE_DATA`**
- **`STRANDED_RESOURCES`**
- **`RIGHTSIZE_AVAILABLE`**

## Rightsizing

Why rightsizing? Because from historical usage, the job is running 'too good' with resource
usage rate far below the sla we need to start worry, which means we can shrink the workers to
cut cost. The key is to find:

Smallest worker count that keeps projected utilization at or under target.

Assumption: projection is linear on historical usage. 

CPU uses p95 (the spec's guardrail). Memory has no p95 in the schema, so use avg.
Taking the max of the two demands so shrink happen when both side agree there is room.
```
min_workers_for_cpu_p95 = ceil(workers × p95_cpu / target)
min_workers_for_mem_avg = ceil(workers × avg_mem / target)
new_workers = max(1, min(max(min_workers_for_cpu_p95, min_workers_for_mem_avg), workers))
```

On the other hand, if new_workers turned out to be more than the current workers number demand by clients,
there's no room to shrink, and we don't add more workers for rightsizing, so the warning stay silent.

## Why an architecture switch is not a savings recommendation

Not sure how historical usage is measured, assume it's based on current setup of (worker count,
arch, etc), it can't be used to predict the next changed setup, or only reliable if the change is
small on that axis. Dropping workers on the same instance can be predicted and linear, switch x86
to arm64 does not. Graviton cores have different per-core performance, so the measured p95 no longer
describes the new hardware, and sizing an arm cluster honestly would first require
rerunning the cluster on arm for some time to collect fresh usage. So architecture stays a compliance
flag (`NON_PREFERRED_ARCHITECTURE`) with no dollar figure attached. Two instances with equal
vCPU and memory are interchangeable on paper, not necessarily at runtime.

## Stranded resources (beyond the brief)

A structural check that flags a cluster whose executor shape packs badly onto its node.

Why bad? Given the clients executor_core, executor_mem and node spec of usable total resources, 
after subtracted the reserving part for OS+shuffling+mem_overhead the maximum number of executors 
a node can run at the same time is determined. And when running at max executors, if either 
exe_cpu/exe_mem is configured too low, that resource will be largely
idle (which also means the job is other side heavy, and that side dominates the max executors on
a node).

So what we do? First, only warns, never fails. Since the calculation rely on some estimation on 
how much resources should be reserved on the node, and how memory overhead is calculated. It's possible
some already running jobs might be viewed as "bad fit" by our model. To avoid the risk before get
reliable estimation, making warn only is safer.

## Handling incomplete and conflicting data

Incomplete data: Any check that depends on a missing field short-circuits: it warns, skips, or returns None, 
so we never compute on data we don't have.

Conflicting signals: Cost vs Risk. A switch to arm64 looks cheaper, 
but the saving can't be trusted since the usage was measured on x86. That's handled in the above section.

Explainability. Every message holds a code, a plain reason, and a fix, and a rightsize message carries its own numbers 
(current and proposed workers, projected utilization, dollars saved). Bad input fails at the exact field, 
and identical input gives identical output, so any result is easy to trace. The other 
half is what we don't output: no saving number on an arch switch, no rightsizing without usage. 
We'd rather say nothing than put out a number we can't back.

## Kept deliberately simple

- No over-utilization alarm. We only warn when a job wastes resources, not when it needs more. To catch a job that needs more you'd watch sustained high load, not one p95 spike, and we didn't build that.
- No streaming throughput check. A streaming job tells you its event rate, like 35000 events a second. The real question is whether the cluster can keep up with that rate. To answer it you need to know how many events one worker can handle a second, and the input never says. So you can't tell if 8 workers is plenty or too few for 35000 a second. You have the demand but not the capacity, so we skip it. Streaming jobs get the same CPU and memory rightsizing as batch.

## Next in production

- A warning for jobs that need more, not less. It triggers when sustained load stays high, and it has its own high threshold in policy, the mirror of the low-utilization one.
- Currently we flagged Graviton as preferred but give no number. Later, move the job to Graviton, collect real usage there, then compute the actual saving.

