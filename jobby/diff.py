import enum

import pandas as pd

class JobDiff(str, enum.Enum):
    NEW = "NEW"
    OLD = "OLD"
    GONE = "GONE"

"""Compute the diff of the two jobs sets and return the union of the two with a new diff column"""
def diff_job_dfs(old_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    old_keys = set(old_df.index)
    new_keys = set(new_df.index)

    new_jobs = new_keys.difference(old_keys)
    old_jobs = new_keys.intersection(old_keys)
    gone_jobs = old_keys.difference(new_keys)

    combined = pd.concat([
        new_df.loc[list(new_jobs)].assign(diff=JobDiff.NEW).sort_index(),
        new_df.loc[list(old_jobs)].assign(diff=JobDiff.OLD).sort_index(),
        old_df.loc[list(gone_jobs)].assign(diff=JobDiff.GONE).sort_index(),
    ])

    return combined[["diff"] + [c for c in combined.columns if c != "diff"]]
