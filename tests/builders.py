from models import (
    ClusterConfig,
    DataConfig,
    EnvPolicy,
    InstancePricing,
    Job,
    Policy,
    SparkConfig,
    Usage,
)

PRICING = {
    "m6i.2xlarge": InstancePricing(0.384, 8, 32, "x86_64"),
    "m6i.4xlarge": InstancePricing(0.768, 16, 64, "x86_64"),
    "m7g.2xlarge": InstancePricing(0.326, 8, 32, "arm64"),
    "m7g.4xlarge": InstancePricing(0.653, 16, 64, "arm64"),
}

QA_POLICY = EnvPolicy(
    require_dynamic_allocation_for_batch=True,
    max_executor_cores=5,
    max_executor_memory_gb=24,
    allowed_architectures=["x86_64", "arm64"],
    preferred_architecture="arm64",
    fail_on_unknown_instance_type=True,
    warn_if_estimated_utilization_below=0.35,
    target_utilization=0.65,
)


def make_policy(env_policy=QA_POLICY, pricing=None):
    return Policy(policies={"qa": env_policy}, pricing=dict(pricing or PRICING))


def make_job(
    name="job",
    env="qa",
    type="batch",
    instance_type="m6i.4xlarge",
    workers=20,
    architecture="x86_64",
    executor_cores=4,
    executor_memory_gb=16,
    dynamic_allocation=True,
    max_executors=80,
    schedule="daily",
):
    return Job(
        name=name,
        env=env,
        type=type,
        engine="spark",
        cluster=ClusterConfig(instance_type, workers, architecture),
        spark=SparkConfig(executor_cores, executor_memory_gb, dynamic_allocation, max_executors),
        data=DataConfig(schedule=schedule),
    )


def make_usage(avg_cpu=0.5, p95_cpu=0.6, avg_mem=0.5, runtime=150.0):
    return Usage(avg_cpu, p95_cpu, avg_mem, runtime)
