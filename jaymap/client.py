# Copyright 2021 John Reese
# Licensed under the MIT License

from dataclasses import dataclass


@dataclass
class JMAP:
    base_url: str
    username: str
    password: str
