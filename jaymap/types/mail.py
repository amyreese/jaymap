# Copyright 2021 John Reese
# Licensed under the MIT License

"""
https://jmap.io/spec-mail.html
"""

from typing import Optional, Any, List, Dict

from jaymap.types.base import Datatype, field
from jaymap.types.core import Id, UnsignedInt, UTCDate, FilterCondition


class MailboxRights(Datatype):
    may_read_items: bool
    may_add_items: bool
    may_remove_items: bool
    may_set_seen: bool
    may_set_keywords: bool
    may_create_child: bool
    may_rename: bool
    may_delete: bool
    may_submit: bool


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
    my_rights: MailboxRights
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


class EmailBodyPart(Datatype):
    part_id: Optional[str]
    blob_id: Optional[Id]
    size: UnsignedInt
    name: Optional[str]
    type: str
    charset: Optional[str]
    disposition: Optional[str]
    cid: Optional[str]
    language: Optional[List[str]]
    location: Optional[str]
    headers: List[EmailHeader] = field(default_factory=list)
    sub_parts: Optional[List["EmailBodyPart"]] = field(default_factory=list)


class EmailBodyValue(Datatype):
    value: str
    is_encoding_problem: bool = False
    is_truncated: bool = False


class Email(Datatype):
    id: Id
    blob_id: Id
    thread_id: Id
    mailbox_ids: Dict[Id, bool]
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
    body_values: Dict[str, EmailBodyValue]
    text_body: List[EmailBodyPart]
    html_body: List[EmailBodyPart]
    attachments: List[EmailBodyPart]
    has_attachment: bool
    preview: str
    body_structure: Optional[EmailBodyPart] = None
    headers: List[EmailHeader] = field(default_factory=list)


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


class MailboxCondition(FilterCondition, sparse=True):
    parent_id: Optional[Id] = None
    name: Optional[str] = None
    role: Optional[str] = None
    has_any_role: Optional[bool] = None
    is_subscribed: Optional[bool] = None


class EmailCondition(FilterCondition, sparse=True):
    in_mailbox: Optional[Id] = None
    in_mailbox_other_than: Optional[List[Id]] = None
    before: Optional[UTCDate] = None
    after: Optional[UTCDate] = None
    min_size: Optional[UnsignedInt] = None
    max_size: Optional[UnsignedInt] = None
    all_in_thread_have_keyword: Optional[str] = None
    some_in_thread_have_keyword: Optional[str] = None
    none_in_thread_have_keyword: Optional[str] = None
    has_keyword: Optional[str] = None
    not_keyword: Optional[str] = None
    has_attachment: Optional[bool] = None
    text: Optional[str] = None
    from_: Optional[str] = None
    to: Optional[str] = None
    cc: Optional[str] = None
    bcc: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    header: Optional[List[str]] = None
