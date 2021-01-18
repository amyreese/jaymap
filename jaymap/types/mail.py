# Copyright 2021 John Reese
# Licensed under the MIT License

"""
https://jmap.io/spec-mail.html
"""

from typing import Optional, Any, List, Dict

from jaymap.types.base import Datatype, field
from jaymap.types.core import Id, UnsignedInt, UTCDate


class Mailbox(Datatype):
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


class Thread(Datatype):
    id: Id
    email_ids: List[Id]


class EmailAddress(Datatype):
    name: Optional[str]
    email: str


class EmailAddressGroup(Datatype):
    name: Optional[str]
    addresses: List[EmailAddress]


class EmailHeader(Datatype):
    name: str
    value: str


class Email(Datatype):
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


class SearchSnippet(Datatype):
    email_id: Id
    subject: Optional[str]
    preview: Optional[str]


class Identity(Datatype):
    id: Id
    name: str
    email: str
    reply_to: Optional[List[str]]
    bcc: Optional[List[str]]
    text_signature: str
    html_signature: str
    may_delete: bool


class Address(Datatype):
    email: str
    parameters: Any


class Envelope(Datatype):
    mail_from: str
    rcpt_to: List[Address]


class DeliveryStatus(Datatype):
    smtp_reply: str
    delivered: str
    displayed: str


class EmailSubmission(Datatype):
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


class VacationResponse(Datatype):
    id: Id
    is_enabled: bool
    from_date: Optional[UTCDate]
    to_date: Optional[UTCDate]
    subject: Optional[str]
    text_body: Optional[str]
    html_body: Optional[str]
