# Copyright 2021 John Reese
# Licensed under the MIT License

"""
https://jmap.io/spec-mail.html
"""

from typing import Optional, Any, List, Dict

from jaymap.types.core import (
    datatype,
    DataClassJsonMixin,
    Id,
    UnsignedInt,
    UTCDate,
    field,
)


@datatype
class Mailbox(DataClassJsonMixin):

    id: Id
    name: str
    parent_id: Optional[Id]
    role: Optional[str]
    sort_order: UnsignedInt
    total_emails: UnsignedInt
    unread_emails: UnsignedInt
    total_threads: UnsignedInt
    unread_threads: UnsignedInt
    my_rights: Any
    is_subscribed: bool


@datatype
class Thread(DataClassJsonMixin):
    id: Id
    email_ids: List[Id]


@datatype
class EmailAddress(DataClassJsonMixin):
    name: Optional[str]
    email: str


@datatype
class EmailAddressGroup(DataClassJsonMixin):
    name: Optional[str]
    addresses: List[EmailAddress]


@datatype
class EmailHeader(DataClassJsonMixin):
    name: str
    value: str


@datatype
class Email(DataClassJsonMixin):
    id: Id
    blob_id: Id
    thread_id: Id
    mailbox_Ids: Dict[Id, bool]
    keywords: Dict[str, bool]
    size: UnsignedInt
    received_at: UTCDate
    message_id: Optional[List[str]]
    in_reply_to: Optional[List[str]]
    references: Optional[List[str]]
    sender: Optional[List[EmailAddress]]
    from_: Optional[List[EmailAddress]]
    to: Optional[List[EmailAddress]]
    cc: Optional[List[EmailAddress]]
    bcc: Optional[List[EmailAddress]]
    reply_to: Optional[List[EmailAddress]]
    subject: Optional[str]
    sent_at: Optional[str]


@datatype
class SearchSnippet(DataClassJsonMixin):
    email_id: Id
    subject: Optional[str]
    preview: Optional[str]


@datatype
class Identity(DataClassJsonMixin):
    id: Id
    name: str
    email: str
    reply_to: Optional[List[str]]
    bcc: Optional[List[str]]
    text_signature: str
    html_signature: str
    may_delete: bool


@datatype
class Address(DataClassJsonMixin):
    email: str
    parameters: Any


@datatype
class Envelope(DataClassJsonMixin):
    mail_from: str
    rcpt_to: List[Address]


@datatype
class DeliveryStatus(DataClassJsonMixin):
    smtp_reply: str
    delivered: str
    displayed: str


@datatype
class EmailSubmission(DataClassJsonMixin):
    id: Id
    identity_id: Id
    email_id: Id
    thread_id: Id
    envelope: Optional[Envelope]
    send_at: UTCDate
    undo_status: str
    delivery_status: Optional[DeliveryStatus]
    dsn_blob_ids: List[Id] = field(default_factory=list)
    mdn_blob_ids: List[Id] = field(default_factory=list)


@datatype
class VacationResponse(DataClassJsonMixin):
    id: Id
    is_enabled: bool
    from_date: Optional[UTCDate]
    to_date: Optional[UTCDate]
    subject: Optional[str]
    text_body: Optional[str]
    html_body: Optional[str]
