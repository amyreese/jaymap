# Copyright 2021 John Reese
# Licensed under the MIT License

"""
Custom encoder/decoder for JMAP specification
"""

import json
from datetime import datetime, timezone
from typing import Any


class JMAPEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            # "2014-10-30T14:12:00Z"
            # "2014-10-30T14:12:00+08:00"
            s = obj.strftime(r"%Y-%m-%dT%H:%I%S")
            if obj.tzinfo is timezone.utc or obj.tzinfo is None:
                s += "Z"
            return s

        return json.JSONEncoder.default(self, obj)


class JMAPDecoder(json.JSONDecoder):
    pass
