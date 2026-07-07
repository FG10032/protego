from pathlib import Path

from exceptions import ConfigError
from loaders.helpers import _as_dict, _from_dict, _read_yaml
from models import Job


def load_jobs(path: Path) -> list[Job]:
    yaml_dict = _as_dict(_read_yaml(path), str(path))
    yaml_jobs = yaml_dict.get("jobs")
    if not isinstance(yaml_jobs, list):
        raise ConfigError(f"{path}: 'jobs' must be a list, got {type(yaml_jobs).__name__}")

    jobs = []
    existing_names = set()
    for i, yaml_job in enumerate(yaml_jobs):
        where = f"{path}.jobs[{i}]"
        job = _from_dict(Job, yaml_job, where)
        if job.name in existing_names:
            raise ConfigError(f"{path}: duplicate job name '{job.name}'")
        existing_names.add(job.name)
        jobs.append(job)
    return jobs
