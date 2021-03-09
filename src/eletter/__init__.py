"""
Simple e-mail composition

``eletter`` provides a basic function for constructing an
``email.message.EmailMessage`` instance without having to touch the needlessly
complicated ``EmailMessage`` class itself.  E-mails with text bodies and/or
HTML bodies plus attachments are supported.  Support for more complex e-mails
is planned for later.

Visit <https://github.com/jwodder/eletter> for more information.
"""

__version__ = "0.2.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "eletter@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/eletter"

from abc import ABC, abstractmethod
from datetime import datetime
from email import headerregistry as hr
from email.message import EmailMessage
from mimetypes import guess_type
import os
import os.path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union
import attr

__all__ = ["Address", "Attachment", "BytesAttachment", "TextAttachment", "compose"]

AnyPath = Union[bytes, str, "os.PathLike[bytes]", "os.PathLike[str]"]


@attr.s(auto_attribs=True)
class Address:
    display_name: str
    address: str


@attr.s(auto_attribs=True)
class ContentType:
    maintype: str
    subtype: str
    params: Dict[str, Any]

    @classmethod
    def parse(cls, s: str) -> "ContentType":
        maintype, subtype, params = parse_content_type(s)
        return cls(maintype, subtype, params)


def cache_content_type(
    ctd: "ContentTyped",
    _attr: Optional[attr.Attribute],
    value: str,
) -> None:
    ct = ContentType.parse(value)
    if ctd.DEFAULT_CONTENT_TYPE.startswith("text/") and ct.maintype != "text":
        raise ValueError("content_type must be text/*")
    ctd._ct = ct


@attr.s
class ContentTyped:
    DEFAULT_CONTENT_TYPE = "application/octet-stream"

    content_type: str = attr.ib(
        kw_only=True,
        default=attr.Factory(lambda self: self.DEFAULT_CONTENT_TYPE, takes_self=True),
        on_setattr=cache_content_type,
    )
    _ct: ContentType = attr.ib(init=False, repr=False, eq=False, order=False)

    def __attrs_post_init__(self) -> None:
        cache_content_type(self, None, self.content_type)


class Attachment(ABC, ContentTyped):
    @abstractmethod
    def _compile(self) -> EmailMessage:
        ...


@attr.s(auto_attribs=True)
class TextAttachment(Attachment):
    DEFAULT_CONTENT_TYPE = "text/plain"

    content: str
    filename: str
    inline: bool = attr.ib(default=False, kw_only=True)

    def _compile(self) -> EmailMessage:
        assert self._ct.maintype == "text", "Content-Type is not text/*"
        params = dict(self._ct.params)
        charset = params.pop("charset", "utf-8")
        msg = EmailMessage()
        msg.set_content(
            self.content,
            subtype=self._ct.subtype,
            disposition="inline" if self.inline else "attachment",
            filename=self.filename,
            params=params,
            charset=charset,
        )
        return msg

    @classmethod
    def from_file(
        cls,
        path: AnyPath,
        content_type: Optional[str] = None,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
    ) -> "TextAttachment":
        with open(path, "r", encoding=encoding, errors=errors) as fp:
            content = fp.read()
        filename = os.path.basename(os.fsdecode(path))
        if content_type is None:
            content_type = get_mime_type(filename)
        return cls(content=content, filename=filename, content_type=content_type)


@attr.s(auto_attribs=True)
class BytesAttachment(Attachment):
    content: bytes
    filename: str
    inline: bool = attr.ib(default=False, kw_only=True)

    def _compile(self) -> EmailMessage:
        msg = EmailMessage()
        msg.set_content(
            self.content,
            self._ct.maintype,
            self._ct.subtype,
            disposition="inline" if self.inline else "attachment",
            filename=self.filename,
            params=self._ct.params,
        )
        return msg

    @classmethod
    def from_file(
        cls, path: AnyPath, content_type: Optional[str] = None
    ) -> "BytesAttachment":
        with open(path, "rb") as fp:
            content = fp.read()
        filename = os.path.basename(os.fsdecode(path))
        if content_type is None:
            content_type = get_mime_type(filename)
        return cls(content=content, filename=filename, content_type=content_type)


def compose(
    subject: str,
    from_: Union[str, Address],
    to: Iterable[Union[str, Address]],
    text: Optional[str] = None,
    html: Optional[str] = None,
    cc: Optional[Iterable[Union[str, Address]]] = None,
    bcc: Optional[Iterable[Union[str, Address]]] = None,
    reply_to: Optional[Union[str, Address]] = None,
    sender: Optional[Union[str, Address]] = None,
    date: Optional[datetime] = None,
    headers: Optional[Mapping[str, Union[str, Iterable[str]]]] = None,
    attachments: Optional[Iterable[Attachment]] = None,
) -> EmailMessage:
    msg: Optional[EmailMessage] = None
    if text is not None:
        msg = EmailMessage()
        msg.set_content(text)
    if html is not None:
        if msg is None:
            msg = EmailMessage()
            msg.set_content(html, subtype="html")
        else:
            msg.add_alternative(html, subtype="html")
    if msg is None:
        raise ValueError("At least one of text and html must be non-None")
    if attachments is not None:
        msg.make_mixed()
        for a in attachments:
            msg.attach(a._compile())
    msg["Subject"] = subject
    msg["From"] = compile_address(from_)
    msg["To"] = list(map(compile_address, to))
    if cc is not None:
        msg["CC"] = list(map(compile_address, cc))
    if bcc is not None:
        msg["BCC"] = list(map(compile_address, bcc))
    if reply_to is not None:
        msg["Reply-To"] = compile_address(reply_to)
    if sender is not None:
        msg["Sender"] = compile_address(sender)
    if date is not None:
        msg["Date"] = date
    if headers is not None:
        for k, v in headers.items():
            values: List[str]
            if isinstance(v, str):
                values = [v]
            else:
                values = list(v)
            for v2 in values:
                msg[k] = v2
    return msg


def compile_address(addr: Union[str, Address]) -> hr.Address:
    if isinstance(addr, str):
        return hr.Address(addr_spec=addr)
    else:
        return hr.Address(display_name=addr.display_name, addr_spec=addr.address)


def parse_content_type(s: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    Split a :mailheader:`Content-Type` value into a triple of ``(maintype,
    subtype, params)``
    """
    msg = EmailMessage()
    msg["Content-Type"] = s
    if msg["Content-Type"].defects:
        raise ValueError(s)
    ct = msg["Content-Type"]
    return (ct.maintype, ct.subtype, dict(ct.params))


def get_mime_type(filename: str, strict: bool = False) -> str:
    """
    Like `mimetypes.guess_type()`, except that if the file is compressed, the
    MIME type for the compression is returned.  Also, the default return value
    is now ``'application/octet-stream'`` instead of `None`.
    """
    mtype, encoding = guess_type(filename, strict)
    if encoding is None:
        return mtype or "application/octet-stream"
    elif encoding == "gzip":
        # application/gzip is defined by RFC 6713
        return "application/gzip"
        # There is also a "+gzip" MIME structured syntax suffix defined by RFC
        # 8460; exactly when can that be used?
        # return mtype + '+gzip'
    else:
        return "application/x-" + encoding
