from datetime import datetime
from email import headerregistry as hr
from email.message import EmailMessage
from typing import Dict, List, Optional, Union
import attr
from mailbits import ContentType, parse_addresses
from .classes import (
    Alternative,
    BytesAttachment,
    EmailAttachment,
    HTMLBody,
    MailItem,
    Mixed,
    Multipart,
    Related,
    TextAttachment,
    TextBody,
)


@attr.s
class Eletter:
    """ A decomposed e-mail message """

    #: The message's body
    content: MailItem = attr.ib()

    #: The message's subject line, if any
    subject: Optional[str] = attr.ib(default=None)

    #: The message's :mailheader:`From` addresses
    from_: List[Union[hr.Address, hr.Group]] = attr.ib(factory=list)

    #: The message's :mailheader:`To` addresses
    to: List[Union[hr.Address, hr.Group]] = attr.ib(factory=list)

    #: The message's :mailheader:`CC` addresses
    cc: List[Union[hr.Address, hr.Group]] = attr.ib(factory=list)

    #: The message's :mailheader:`BCC` addresses
    bcc: List[Union[hr.Address, hr.Group]] = attr.ib(factory=list)

    #: The message's :mailheader:`Reply-To` addresses
    reply_to: List[Union[hr.Address, hr.Group]] = attr.ib(factory=list)

    #: The message's :mailheader:`Sender` address, if any
    sender: Optional[hr.Address] = attr.ib(default=None)

    #: The message's :mailheader:`Date` header, if set
    date: Optional[datetime] = attr.ib(default=None)

    #: Any additional headers on the message
    headers: Dict[str, List[str]] = attr.ib(factory=dict)


STANDARD_HEADERS = {
    "subject",
    "from",
    "to",
    "cc",
    "bcc",
    "reply-to",
    "sender",
    "date",
    "content-type",
    "content-id",
    "content-disposition",
    "content-transfer-encoding",
    "mime-version",
}


def decompose(msg: EmailMessage) -> Eletter:
    """
    Decompose an `~email.message.EmailMessage` into an `Eletter` instance
    containing a `MailItem` and a collection of headers.  Only structures that
    can be represented by ``eletter`` classes are supported.

    All message parts that are not :mimetype:`text/plain`,
    :mimetype:`text/html`, :mimetype:`multipart/*`, or :mimetype:`message/*`
    are treated as attachments.

    Any information specific to how the message is encoded is discarded
    (namely, "charset" parameters on :mimetype:`text/*` parts,
    :mailheader:`Content-Transfer-Encoding` headers, and
    :mailheader:`MIME-Version` headers).

    Headers on message sub-parts that do not have representations on
    `MailItem`\\s are discarded (namely, everything other than
    :mailheader:`Content-Type`, :mailheader:`Content-Disposition`, and
    :mailheader:`Content-ID`).

    :raises TypeError:
        if any sub-part of ``msg`` is not an `~email.message.EmailMessage`
        instance
    :raises ValueError:
        if ``msg`` contains a part with an unrepresentable
        :mailheader:`Content-Type`
    """

    subject = get_str_header(msg, "Subject")
    from_ = get_address_list(msg, "From")
    to = get_address_list(msg, "To")
    cc = get_address_list(msg, "CC")
    bcc = get_address_list(msg, "BCC")
    reply_to = get_address_list(msg, "Reply-To")
    sender_head = msg.get("Sender")
    sender: Optional[hr.Address]
    if sender_head is not None:
        assert isinstance(sender_head, hr.SingleAddressHeader)
        sender = sender_head.address
    else:
        sender = None
    date_head = msg.get("Date")
    date: Optional[datetime]
    if date_head is not None:
        assert isinstance(date_head, hr.DateHeader)
        date = date_head.datetime
    else:
        date = None
    headers: Dict[str, List[str]] = {}
    for h in msg.keys():
        h = h.lower()
        if h not in STANDARD_HEADERS:
            headers[h] = list(map(str, msg.get_all(h, [])))
    content = get_content(msg)
    return Eletter(
        subject=subject,
        from_=from_,
        to=to,
        cc=cc,
        bcc=bcc,
        reply_to=reply_to,
        sender=sender,
        date=date,
        headers=headers,
        content=content,
    )


def get_content(msg: EmailMessage) -> MailItem:
    maintype = msg.get_content_maintype()
    subtype = msg.get_content_subtype()
    disposition = msg.get_content_disposition()
    filename = msg.get_filename(None)
    content_id = get_str_header(msg, "Content-ID")
    if filename is not None and disposition is None:
        disposition = "attachment"
    if maintype == "multipart":
        content: Multipart
        if subtype == "mixed":
            content = Mixed(content_id=content_id)
        elif subtype == "alternative":
            content = Alternative(content_id=content_id)
        elif subtype == "related":
            h = msg["Content-Type"]
            start: Optional[str]
            if h is not None:
                assert isinstance(h, hr.ContentTypeHeader)
                s = h.params.get("start")
                assert s is None or isinstance(s, str)
                start = s
            else:
                start = None
            content = Related(content_id=content_id, start=start)
        else:
            raise ValueError(f"Unsupported Content-Type: {maintype}/{subtype}")
        for p in msg.iter_parts():
            if not isinstance(p, EmailMessage):
                raise TypeError("EmailMessage parts must be EmailMessage instances")
            content.append(get_content(p))
        return content
    elif maintype == "message":
        if subtype == "rfc822":
            body = msg.get_content()
            if not isinstance(body, EmailMessage):
                raise TypeError("EmailMessage parts must be EmailMessage instances")
            return EmailAttachment(
                content=body,
                filename=filename,
                inline=disposition == "inline",
                content_id=content_id,
            )
        else:
            raise ValueError(f"Unsupported Content-Type: {maintype}/{subtype}")
    elif maintype == "text":
        text = msg.get_content()
        assert isinstance(text, str)
        ct = get_str_header(msg, "Content-Type")
        if ct is None:
            ct = "text/plain"
        parsed_ct = ContentType.parse(ct)
        parsed_ct.params.pop("charset", None)
        if (
            filename is not None
            or disposition == "attachment"
            or subtype not in ("plain", "html")
        ):
            return TextAttachment(
                content=text,
                filename=filename,
                content_type=str(parsed_ct),
                inline=disposition == "inline",
                content_id=content_id,
            )
        elif subtype == "plain":
            return TextBody(text, content_id=content_id)
        else:
            assert subtype == "html"
            return HTMLBody(text, content_id=content_id)
    else:
        blob = msg.get_content()
        assert isinstance(blob, bytes)
        ct = get_str_header(msg, "Content-Type")
        if ct is None:
            ct = "application/octet-stream"
        return BytesAttachment(
            content=blob,
            filename=filename,
            content_type=ct,
            content_id=content_id,
            inline=disposition == "inline",
        )


def get_str_header(msg: EmailMessage, header: str) -> Optional[str]:
    value = msg.get(header)
    if value is not None:
        return str(value)
    else:
        return None


def get_address_list(
    msg: EmailMessage, header: str
) -> List[Union[hr.Address, hr.Group]]:
    addresses = []
    for h in msg.get_all(header, []):
        assert isinstance(h, hr.AddressHeader)
        addresses.extend(parse_addresses(h))
    return addresses
