"""
Simple e-mail composition

Visit <https://github.com/jwodder/eletter> for more information.
"""

__version__ = "0.1.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "eletter@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/eletter"

from abc import ABC, abstractmethod
from datetime import datetime
from email import headerregistry as hr
from email.message import EmailMessage
from functools import partial
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union
import attr


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


class Attachment(ABC):
    @abstractmethod
    def _compile(self) -> EmailMessage:
        ...


def cache_content_type(
    attach: Union["TextAttachment", "BytesAttachment"],
    _attr: Optional[attr.Attribute],
    value: str,
    text: bool = False,
) -> None:
    ct = ContentType.parse(value)
    if text and ct.maintype != "text":
        raise ValueError("content_type must be text/*")
    attach._ct = ct


@attr.s(auto_attribs=True)
class TextAttachment(Attachment):
    content: str
    filename: str
    content_type: str = attr.ib(
        default="text/plain", on_setattr=partial(cache_content_type, text=True)
    )
    inline: bool = False
    _ct: ContentType = attr.ib(init=False, repr=False, eq=False, order=False)

    def __attrs_post_init__(self) -> None:
        cache_content_type(self, None, self.content_type, text=True)

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


@attr.s(auto_attribs=True)
class BytesAttachment(Attachment):
    content: bytes
    filename: str
    content_type: str = attr.ib(
        default="application/octet-stream", on_setattr=cache_content_type
    )
    inline: bool = False
    _ct: ContentType = attr.ib(init=False, repr=False, eq=False, order=False)

    def __attrs_post_init__(self) -> None:
        cache_content_type(self, None, self.content_type)

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
