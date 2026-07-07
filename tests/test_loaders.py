import pytest

from exceptions import ConfigError
from loaders.load_job import load_jobs
from loaders.load_usage import load_usage


def test_duplicate_job_name_rejected(tmp_path):
    jobs_yaml = """
jobs:
  - name: same-name
    env: prod
    type: batch
    engine: spark
    cluster: {instance_type: m6i.4xlarge, workers: 4, architecture: x86_64}
    spark: {executor_cores: 2, executor_memory_gb: 8, dynamic_allocation: true}
    data: {}
  - name: same-name
    env: prod
    type: batch
    engine: spark
    cluster: {instance_type: m6i.4xlarge, workers: 4, architecture: x86_64}
    spark: {executor_cores: 2, executor_memory_gb: 8, dynamic_allocation: true}
    data: {}
"""
    jobs_file = tmp_path.joinpath("jobs.yaml")
    jobs_file.write_text(jobs_yaml)

    with pytest.raises(ConfigError) as error:
        load_jobs(jobs_file)
    assert "duplicate job name" in str(error.value)


def test_from_dict_error_locates_the_offending_job(tmp_path):
    jobs_yaml = """
jobs:
  - name: ok
    env: prod
    type: batch
    engine: spark
    cluster: {instance_type: m6i.4xlarge, workers: 4, architecture: x86_64}
    spark: {executor_cores: 2, executor_memory_gb: 8, dynamic_allocation: true}
    data: {}
  - name: broken
    env: prod
    type: batch
    engine: spark
    cluster: {workers: 4, architecture: x86_64}
    spark: {executor_cores: 2, executor_memory_gb: 8, dynamic_allocation: true}
    data: {}
"""
    jobs_file = tmp_path.joinpath("jobs.yaml")
    jobs_file.write_text(jobs_yaml)

    with pytest.raises(ConfigError) as error:
        load_jobs(jobs_file)
    message = str(error.value)
    assert "jobs[1]" in message
    assert "instance_type" in message


def test_as_dict_error_locates_the_offending_usage_entry(tmp_path):
    usage_file = tmp_path.joinpath("usage.json")
    usage_file.write_text('{"job-a": "not-a-mapping"}')

    with pytest.raises(ConfigError) as error:
        load_usage(usage_file)
    assert "usage[job-a]" in str(error.value)
