from datetime import datetime
from email import headerregistry as hr
from email.message import EmailMessage
from functools import partial
from typing import Dict, List, Optional, Tuple, Union
import attr
from mailbits import ContentType, parse_addresses
from .classes import (
    Alternative,
    Attachment,
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
from .core import compose
from .errors import DecompositionError, MixedContentError, SimplificationError


@attr.s
class Eletter:
    """
    .. versionadded:: 0.5.0

    A decomposed e-mail message
    """

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

    #: Any additional headers on the message.  The header names are lowercase.
    headers: Dict[str, List[str]] = attr.ib(factory=dict)

    def compose(self) -> EmailMessage:
        """
        Convert the `Eletter` back into an `~email.message.EmailMessage`
        """
        return self.content.compose(
            subject=self.subject,
            from_=self.from_,
            to=self.to,
            cc=self.cc,
            bcc=self.bcc,
            reply_to=self.reply_to,
            sender=self.sender,
            date=self.date,
            headers=self.headers,
        )

    def simplify(self, unmix: bool = False) -> "SimpleEletter":
        """
        Simplify the `Eletter` into a `SimpleEletter`, breaking down
        `Eletter.content` into a text body, HTML body, and a list of
        attachments.

        By default, a :mimetype:`multipart/mixed` message can only be
        simplified if all of the attachments come after all of the message
        bodies; set ``unmix`` to `True` to separate the attachments from the
        bodies regardless of what order they come in.

        :raises SimplificationError: if ``msg`` cannot be simplified
        """
        content = smooth(self.content)
        text: Optional[str]
        html: Optional[str]
        attachments: List[Attachment]
        if isinstance(content, Alternative):
            text = None
            html = None
            attachments = []
            for t, h, attach in map(partial(simplify_alt_part, unmix=unmix), content):
                if t is not None and h is None:
                    if text is None:
                        text = t
                    else:
                        raise SimplificationError(
                            "Multiple text/plain parts in multipart/alternative"
                        )
                elif h is not None and t is None:
                    if html is None:
                        html = h
                    else:
                        raise SimplificationError(
                            "Multiple text/html parts in multipart/alternative"
                        )
                elif t is None and h is None:
                    raise SimplificationError(
                        "Alternative part contains neither text/plain nor text/html"
                    )
                else:
                    raise SimplificationError(
                        "Alternative part contains both text/plain and text/html"
                    )
                attachments.extend(a for a in attach if a not in attachments)
        else:
            text, html, attachments = simplify_alt_part(content, unmix=unmix)
        if text is None and html is None:
            raise SimplificationError("No text or HTML bodies in message")
        return SimpleEletter(
            text=text,
            html=html,
            attachments=attachments,
            subject=self.subject,
            from_=self.from_,
            to=self.to,
            cc=self.cc,
            bcc=self.bcc,
            reply_to=self.reply_to,
            sender=self.sender,
            date=self.date,
            headers=self.headers,
        )


@attr.s
class SimpleEletter:
    """
    .. versionadded:: 0.5.0

    A decomposed simple e-mail message, consisting of a text body and/or HTML
    body plus some number of attachments and headers
    """

    #: The message's text body, if any
    text: Optional[str] = attr.ib(default=None)

    #: The message's HTML body, if any
    html: Optional[str] = attr.ib(default=None)

    #: Attachments on the message
    attachments: List[Attachment] = attr.ib(factory=list)

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

    #: Any additional headers on the message.  The header names are lowercase.
    headers: Dict[str, List[str]] = attr.ib(factory=dict)

    def compose(self) -> EmailMessage:
        """
        Convert the `SimpleEletter` back into an `~email.message.EmailMessage`
        """
        return compose(
            text=self.text,
            html=self.html,
            attachments=self.attachments,
            subject=self.subject,
            from_=self.from_,
            to=self.to,
            cc=self.cc,
            bcc=self.bcc,
            reply_to=self.reply_to,
            sender=self.sender,
            date=self.date,
            headers=self.headers,
        )


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
    .. versionadded:: 0.5.0

    Decompose an `~email.message.EmailMessage` into an `Eletter` instance
    containing a `MailItem` and a collection of headers.  Only structures that
    can be represented by ``eletter`` classes are supported.

    All message parts that are not :mimetype:`text/plain`,
    :mimetype:`text/html`, :mimetype:`multipart/*`, or :mimetype:`message/*`
    are treated as attachments.  Attachments without filenames or an explicit
    "attachment" :mailheader:`Content-Disposition` are treated as inline.

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
    :raises DecompositionError:
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
    try:
        ct = ContentType.parse(str(msg.get("Content-Type", msg.get_default_type())))
    except ValueError:
        ct = ContentType.parse("text/plain")
    disposition = msg.get_content_disposition()
    filename = msg.get_filename(None)
    content_id = get_str_header(msg, "Content-ID")
    if filename is not None and disposition is None:
        disposition = "attachment"
    if ct.maintype == "multipart":
        content: Multipart
        if ct.subtype == "mixed":
            content = Mixed(content_id=content_id)
        elif ct.subtype == "alternative":
            content = Alternative(content_id=content_id)
        elif ct.subtype == "related":
            content = Related(content_id=content_id, start=ct.params.get("start"))
        else:
            raise DecompositionError(f"Unsupported Content-Type: {ct.content_type}")
        for p in msg.iter_parts():
            if not isinstance(p, EmailMessage):  # pragma: no cover
                raise TypeError("EmailMessage parts must be EmailMessage instances")
            content.append(get_content(p))
        return content
    elif ct.maintype == "message":
        if ct.subtype == "rfc822":
            body = msg.get_content()
            if not isinstance(body, EmailMessage):  # pragma: no cover
                raise TypeError("EmailMessage parts must be EmailMessage instances")
            return EmailAttachment(
                content=body,
                filename=filename,
                inline=disposition != "attachment",
                content_id=content_id,
            )
        else:
            raise DecompositionError(f"Unsupported Content-Type: {ct.content_type}")
    elif ct.maintype == "text":
        text = msg.get_content()
        assert isinstance(text, str)
        if (
            filename is not None
            or disposition == "attachment"
            or ct.subtype not in ("plain", "html")
        ):
            ct.params.pop("charset", None)
            return TextAttachment(
                content=text,
                filename=filename,
                content_type=str(ct),
                inline=disposition != "attachment",
                content_id=content_id,
            )
        elif ct.subtype == "plain":
            return TextBody(text, content_id=content_id)
        else:
            assert ct.subtype == "html"
            return HTMLBody(text, content_id=content_id)
    else:
        blob = msg.get_content()
        assert isinstance(blob, bytes)
        return BytesAttachment(
            content=blob,
            filename=filename,
            content_type=str(ct),
            content_id=content_id,
            inline=disposition != "attachment",
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


def decompose_simple(msg: EmailMessage, unmix: bool = False) -> SimpleEletter:
    """
    .. versionadded:: 0.5.0

    Decompose an `~email.message.EmailMessage` into a `SimpleEletter` instance
    consisting of a text body and/or HTML body, some number of attachments, and
    a collection of headers.  The `~email.message.EmailMessage` is first
    decomposed with `decompose()` and then simplified by calling
    `Eletter.simplify()`.

    By default, a :mimetype:`multipart/mixed` message can only be simplified if
    all of the attachments come after all of the message bodies; set ``unmix``
    to `True` to separate the attachments from the bodies regardless of what
    order they come in.

    :raises TypeError:
        if any sub-part of ``msg`` is not an `~email.message.EmailMessage`
        instance
    :raises DecompositionError:
        if ``msg`` contains a part with an unrepresentable
        :mailheader:`Content-Type`
    :raises SimplificationError: if ``msg`` cannot be simplified
    """
    return decompose(msg).simplify(unmix=unmix)


def smooth(mi: MailItem) -> MailItem:
    if isinstance(mi, Multipart):
        out: List[MailItem] = []
        for n in mi:
            n = smooth(n)
            # Flatten nested Mixed and Alternative, but not Related:
            if type(n) is type(mi) and not isinstance(mi, Related):
                assert isinstance(n, Multipart)
                out.extend(n)
            elif not (isinstance(n, Multipart) and len(n) == 0):
                out.append(n)
        if len(out) == 1:
            return out[0]
        else:
            return type(mi)(out)
    else:
        return mi


def alt2text_html(alt: Alternative) -> Tuple[str, str]:
    if len(alt) == 2:
        if isinstance(alt[0], TextBody) and isinstance(alt[1], HTMLBody):
            return (alt[0].content, alt[1].content)
        elif isinstance(alt[0], HTMLBody) and isinstance(alt[1], TextBody):
            return (alt[1].content, alt[0].content)
    raise SimplificationError(
        "multipart/alternative inside multipart/mixed is not a text/plain part"
        " plus a text/html part"
    )


def simplify_alt_part(
    content: MailItem, unmix: bool = False
) -> Tuple[Optional[str], Optional[str], List[Attachment]]:
    text: Optional[str] = None
    html: Optional[str] = None
    attachments: List[Attachment] = []

    def add_text(t: str) -> None:
        nonlocal text
        if text is None:
            text = t
        else:
            if not text.endswith("\n"):
                text += "\n"
            text += t

    def add_html(h: str) -> None:
        nonlocal html
        if html is None:
            html = h
        else:
            if not html.endswith("\n"):
                html += "\n"
            html += h

    if isinstance(content, TextBody):
        text = content.content
    elif isinstance(content, HTMLBody):
        html = content.content
    elif isinstance(content, Mixed):
        for mi in content:
            if isinstance(mi, TextBody):
                if attachments and not unmix:
                    raise MixedContentError(
                        "Message intersperses attachments with text"
                    )
                if html is not None:
                    raise SimplificationError(
                        "No matching HTML alternative for text part"
                    )
                add_text(mi.content)
            elif isinstance(mi, HTMLBody):
                if attachments and not unmix:
                    raise MixedContentError(
                        "Message intersperses attachments with text"
                    )
                if text is not None:
                    raise SimplificationError(
                        "No matching text alternative for HTML part"
                    )
                add_html(mi.content)
            # elif isinstance(mi, Mixed):  # smoothed out
            elif isinstance(mi, Alternative):
                # Require the Alt to be only text | html; error on further
                # nesting
                text_part, html_part = alt2text_html(mi)
                if attachments and not unmix:
                    raise MixedContentError(
                        "Message intersperses attachments with text"
                    )
                if (text is None) == (html is None):
                    add_text(text_part)
                    add_html(html_part)
                elif text is not None:
                    raise SimplificationError(
                        "Text + HTML alternative follows text-only body"
                    )
                else:
                    assert html is not None
                    raise SimplificationError(
                        "Text + HTML alternative follows HTML-only body"
                    )
            elif isinstance(mi, Related):
                raise SimplificationError("Cannot simplify multipart/related")
            elif isinstance(mi, Attachment):
                attachments.append(mi)
            else:
                raise TypeError(str(type(mi)))  # pragma: no cover
    elif isinstance(content, Related):
        raise SimplificationError("Cannot simplify multipart/related")
    elif isinstance(content, Attachment):
        raise SimplificationError("Body is an attachment")
    else:
        raise TypeError(str(type(content)))  # pragma: no cover
    return (text, html, attachments)
