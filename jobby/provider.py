import abc
import dataclasses
import logging
from typing import Any, Optional

import pandas as pd
import requests

from jobby.job import Job


class Provider(abc.ABC):
    @property
    @abc.abstractmethod
    def __key__(self) -> str:
        ...

    @classmethod
    @abc.abstractmethod
    def from_config(cls, key: str, data: Any) -> Optional["Provider"]:
        ...

    @abc.abstractmethod
    def get_jobs(self) -> Optional[pd.DataFrame]:
        ...

class RawProvider(Provider):
    __key__ = "raw"

    def __init__(self, name: str, uri: str, keymaps: dict[str, str]):
        self.name = name
        self.uri = uri
        self.keymaps = keymaps

    @classmethod
    def from_config(cls, key: str, data: dict[str, str]) -> "RawProvider":
        return cls(name=key, uri=data.pop("uri"), keymaps=data)

    def get_jobs(self) -> Optional[pd.DataFrame]:
        x = requests.get(self.uri)

        if x.status_code != 200:
            logging.error(f"{x.status_code} received from {self.__key__}")
            return None

        job_json = x.json()
        if "data" in self.keymaps:
            job_json = job_json[self.keymaps["data"]]

        jobs = []
        for job in job_json:
            data = {"company": self.name}
            for field in Job.__annotations__:
                if field in self.keymaps:
                    data[field] = job[self.keymaps[field]]
                elif field in job:
                    data[field] = job[field]
            data["uid"] = f"{self.__key__}.{self.name}.{data['uid']}"

            # noinspection PyTypeChecker
            jobs.append(dataclasses.asdict(Job(**data)))

        return pd.DataFrame.from_records(jobs)


class ADP(Provider):
    __key__ = "adp"

    def __init__(self, cid: str, name: str):
        self.cid = cid
        self.name = name

    def get_uri(self):
        return f"https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/job-requisitions?cid={self.cid}"

    @classmethod
    def from_config(cls, key: str, data: str) -> "ADP":
        return cls(cid=key, name=data)

    def get_jobs(self) -> Optional[pd.DataFrame]:
        x = requests.get(self.get_uri())

        if x.status_code != 200:
            logging.error(f"{x.status_code} received from {self.__key__}")
            return None

        jobs = []
        for job in x.json()["jobRequisitions"]:
            # noinspection PyTypeChecker
            jobs.append(dataclasses.asdict(Job(
                uid=f"{self.__key__}.{self.cid}.{job['itemID']}",
                title=job["requisitionTitle"],
                company=self.name,
                location=""
            )))

        return pd.DataFrame.from_records(jobs)


class RecruiterBox(Provider):
    __key__ = "recruiter_box"

    def __init__(self, uid: str, name: str):
        self.uid = uid
        self.name = name

    def get_uri(self):
        return f"https://app.recruiterbox.com/widget/{self.uid}/openings"

    @classmethod
    def from_config(cls, key: str, data: str) -> "RecruiterBox":
        return cls(uid=key, name=data)

    def get_jobs(self) -> Optional[pd.DataFrame]:
        x = requests.get(self.get_uri())

        if x.status_code != 200:
            logging.error(f"{x.status_code} received from {self.__key__}")
            return None

        jobs = []
        for job in x.json():
            location_str = ""
            location_info = job["location"]
            for sub_field in ["city", "state", "country"]:
                if not location_info[sub_field]:
                    continue

                if location_str:
                    location_str += ", "

                location_str += location_info[sub_field]

            # noinspection PyTypeChecker
            jobs.append(dataclasses.asdict(Job(
                uid=f"{self.__key__}.{self.uid}.{job['id']}",
                title=job["title"],
                company=self.name,
                location=location_str,
                allows_remote=job["allows_remote"],
                is_full_time="full" in job["position_type"].lower(),
            )))

        return pd.DataFrame.from_records(jobs)
