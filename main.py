import argparse
import logging
from pathlib import Path

import pandas as pd
import tqdm

from jobby.config import Config
from jobby.diff import diff_job_dfs
from jobby.job import make_empty_jobs_df

def get_all_jobs(config: Config) -> pd.DataFrame:
    job_dfs = []
    for provider in tqdm.tqdm(config.providers):
        job_df = provider.get_jobs()
        if job_df is not None:
            job_dfs.append(job_df)

    return pd.concat(job_dfs).set_index('uid') if job_dfs else make_empty_jobs_df()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args()

    config = Config.load(args.config)

    out_file = config.output_dir / "jobs.csv"
    new_df = get_all_jobs(config)
    old_df = pd.read_csv(out_file).set_index("uid") if out_file.exists() else make_empty_jobs_df()

    jobs_df = diff_job_dfs(old_df=old_df, new_df=new_df)

    jobs_df.to_csv(out_file, index=True)

    logging.info(f"Wrote jobs to {out_file}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()