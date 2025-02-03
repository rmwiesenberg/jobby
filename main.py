import argparse
import dataclasses
import logging
from pathlib import Path

import pandas as pd
import tqdm

from jobby.config import Config
from jobby.job import Job
from jobby.provider import Provider


def get_all_jobs(config: Config) -> pd.DataFrame:
    job_dfs = []
    for provider in tqdm.tqdm(config.providers):
        job_df = provider.get_jobs()
        if job_df is not None:
            job_dfs.append(job_df)

    return (pd.concat(job_dfs) if job_dfs else pd.DataFrame(columns=list(Job.__annotations__.keys()))).set_index('uid')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args()

    config = Config.load(args.config)
    jobs = get_all_jobs(config)

    jobs.to_csv(config.output_dir / "jobs.csv", index=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()