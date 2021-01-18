# Copyright 2021 John Reese
# Licensed under the MIT License

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Iterable

from jaymap.types.core import Id, UnsignedInt, Capabilities

if TYPE_CHECKING:
    from jaymap.client import JMAP


@dataclass
class MailboxAPI:
    account_id: Id
    client: "JMAP"

    async def get(self, ids: Optional[Iterable[Id]] = None) -> None:
        pass
