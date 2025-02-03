import copy
from dataclasses import dataclass
from typing import Optional

import pandas as pd


def make_empty_jobs_df() -> pd.DataFrame:
    return pd.DataFrame(columns=list(Job.__annotations__.keys())).set_index("uid")

@dataclass
class Job:
    uid: str
    title: str

    company: str
    location: str

    allows_remote: Optional[bool] = None
    is_full_time: Optional[bool] = None

    """
    Auto-helper to reshape data into the correct format.
    Post init should generally not be relied on, instead have the provider take care of this if the pattern is known. 
    """
    def __post_init__(self):
        # Location data is generally in a dict, try to flatten it
        if isinstance(self.location, dict):
            location_dict = copy.deepcopy({k.lower(): v for k, v in self.location.items()})

            location_str = ""
            for sub_field in ["city", "state", "province", "country"]:
                if sub_field not in location_dict:
                    continue

                if location_str:
                    location_str += ", "

                location_str += location_dict[sub_field]
            self.location = location_str

        # Remote and full time information might not be bool, try to figure it out
        if isinstance(self.allows_remote, str):
            self.allows_remote = "remote" in self.allows_remote.lower()

        if isinstance(self.is_full_time, str):
            self.is_full_time = "full" in self.is_full_time.lower()
