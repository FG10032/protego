from dataclasses import replace

import pytest
from builders import PRICING, QA_POLICY, make_job, make_usage
from guardrails import (
    check_dynamic_allocation,
    check_max_executor_cores,
    check_max_executor_memory,
    check_unknown_instance_type,
    check_unsupported_architecture,
    warn_low_utilization,
    warn_missing_incomplete_usage_data,
    warn_non_preferred_architecture,
    warn_stranded_resources,
)
from models import MessageLevel


@pytest.mark.parametrize("message, code", [
    (check_unknown_instance_type(make_job(instance_type="a1b.2xlarge"), "qa", QA_POLICY, PRICING), "UNKNOWN_INSTANCE_TYPE"),
    (check_unsupported_architecture(make_job(architecture="quantum"), "qa", QA_POLICY), "UNSUPPORTED_ARCHITECTURE"),
    (check_max_executor_cores(make_job(executor_cores=8), "qa", QA_POLICY), "EXECUTOR_CORES_EXCEEDED"),
    (check_max_executor_memory(make_job(executor_memory_gb=32), "qa", QA_POLICY), "EXECUTOR_MEMORY_EXCEEDED"),
    (check_dynamic_allocation(make_job(type="batch", dynamic_allocation=False), "qa", QA_POLICY),
     "DYNAMIC_ALLOCATION_REQUIRED"),
])
def test_blocking_guardrail_fires(message, code):
    assert message.code == code
    assert message.level == MessageLevel.ERROR


def test_unknown_instance_only_warns_when_not_enforced():
    lenient = replace(QA_POLICY, fail_on_unknown_instance_type=False)
    msg = check_unknown_instance_type(make_job(instance_type="a1b.2xlarge"), "qa", lenient, PRICING)
    assert msg.level == MessageLevel.WARN


def test_non_preferred_arch_warns_only_when_equivalent_exists():
    msg = warn_non_preferred_architecture(make_job(architecture="x86_64"), "qa", QA_POLICY, PRICING)
    assert msg.code == "NON_PREFERRED_ARCHITECTURE"
    assert warn_non_preferred_architecture(make_job(architecture="x86_64"), "qa", QA_POLICY,
                                           {"m6i.4xlarge": PRICING["m6i.4xlarge"]}) is None


def test_low_utilization_warns_at_zero_but_not_on_missing_metric():
    job = make_job()
    assert warn_low_utilization(job, "qa", QA_POLICY, {job.name: make_usage(avg_cpu=0.0)}) is not None
    assert warn_low_utilization(job, "qa", QA_POLICY, {job.name: make_usage(avg_cpu=None)}) is None


def test_usage_missing_vs_partial():
    job = make_job()
    assert warn_missing_incomplete_usage_data(job, "qa", {}).code == "MISSING_USAGE_DATA"
    assert warn_missing_incomplete_usage_data(job, "qa",
                                              {job.name: make_usage(p95_cpu=None)}).code == "INCOMPLETE_USAGE_DATA"


@pytest.mark.parametrize("cores, mem, bound", [(1, 30, "CPU-side"), (5, 4, "memory-side")])
def test_stranded_flags_binding_dimension(cores, mem, bound):
    msg = warn_stranded_resources(make_job(executor_cores=cores, executor_memory_gb=mem), "qa", PRICING)
    assert msg.code == "STRANDED_RESOURCES" and bound in msg.cause


def test_balanced_not_stranded():
    assert warn_stranded_resources(make_job(executor_cores=4, executor_memory_gb=16), "qa", PRICING) is None
