from abc import ABC, abstractmethod
from datetime import datetime
from email import headerregistry as hr
from email import message_from_binary_file
from email import policy
from email.message import EmailMessage
import os
import os.path
from typing import Iterable, List, Mapping, Optional, Union
import attr
from .util import (
    AddressOrGroup,
    AnyPath,
    ContentType,
    SingleAddress,
    compile_address,
    compile_addresses,
    get_mime_type,
)


class Address(hr.Address):
    """ A combination of a person's name and their e-mail address """

    def __init__(self, display_name: str, address: str) -> None:
        super().__init__(display_name=display_name, addr_spec=address)


class Group(hr.Group):
    """ A e-mail address group """

    def __init__(self, display_name: str, addresses: Iterable[SingleAddress]) -> None:
        super().__init__(
            display_name=display_name, addresses=tuple(map(compile_address, addresses))
        )


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

    #: The :mailheader:`Content-Type` of the attachment
    content_type: str = attr.ib(
        kw_only=True,
        default=attr.Factory(lambda self: self.DEFAULT_CONTENT_TYPE, takes_self=True),
        on_setattr=cache_content_type,
    )
    _ct: ContentType = attr.ib(init=False, repr=False, eq=False, order=False)

    def __attrs_post_init__(self) -> None:
        cache_content_type(self, None, self.content_type)


class MailItem(ABC):
    """ Base class for all ``eletter`` message components """

    @abstractmethod
    def _compile(self) -> EmailMessage:
        ...

    def compose(
        self,
        subject: str,
        from_: Union[AddressOrGroup, Iterable[AddressOrGroup]],
        to: Iterable[AddressOrGroup],
        cc: Optional[Iterable[AddressOrGroup]] = None,
        bcc: Optional[Iterable[AddressOrGroup]] = None,
        reply_to: Optional[Union[AddressOrGroup, Iterable[AddressOrGroup]]] = None,
        sender: Optional[SingleAddress] = None,
        date: Optional[datetime] = None,
        headers: Optional[Mapping[str, Union[str, Iterable[str]]]] = None,
    ) -> EmailMessage:
        msg = self._compile()
        msg["Subject"] = subject
        msg["From"] = compile_addresses(from_)
        msg["To"] = compile_addresses(to)
        if cc is not None:
            msg["CC"] = compile_addresses(cc)
        if bcc is not None:
            msg["BCC"] = compile_addresses(bcc)
        if reply_to is not None:
            msg["Reply-To"] = compile_addresses(reply_to)
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

    def __or__(self, other: "MailItem") -> "Alternative":
        parts: List[MailItem] = []
        for mi in [self, other]:
            if isinstance(mi, Alternative):
                parts.extend(mi.content)
            else:
                parts.append(mi)
        return Alternative(parts)

    def __add__(self, other: "MailItem") -> "Mixed":
        parts: List[MailItem] = []
        for mi in [self, other]:
            if isinstance(mi, Mixed):
                parts.extend(mi.content)
            else:
                parts.append(mi)
        return Mixed(parts)


class Attachment(MailItem):
    """ Base class for the attachment classes """

    pass


@attr.s(auto_attribs=True)
class TextAttachment(Attachment, ContentTyped):
    """
    A representation of a textual e-mail attachment.  The content type must
    have a maintype of :mimetype:`text`.
    """

    DEFAULT_CONTENT_TYPE = "text/plain"

    #: The body of the attachment
    content: str
    #: The filename of the attachment
    filename: str
    #: Whether the attachment should be displayed inline in clients
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
        inline: bool = False,
    ) -> "TextAttachment":
        """
        Construct a `TextAttachment` from the contents of the file at ``path``.
        The filename of the attachment will be set to the basename of ``path``.
        If ``content_type`` is `None`, the :mailheader:`Content-Type` is
        guessed based on ``path``'s file extension.  ``encoding`` and
        ``errors`` are used when opening the file and have no relation to the
        :mailheader:`Content-Type`.
        """
        with open(path, "r", encoding=encoding, errors=errors) as fp:
            content = fp.read()
        filename = os.path.basename(os.fsdecode(path))
        if content_type is None:
            content_type = get_mime_type(filename)
        return cls(
            content=content, filename=filename, content_type=content_type, inline=inline
        )


@attr.s(auto_attribs=True)
class BytesAttachment(Attachment, ContentTyped):
    """ A representation of a binary e-mail attachment """

    #: The body of the attachment
    content: bytes
    #: The filename of the attachment
    filename: str
    #: Whether the attachment should be displayed inline in clients
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
        cls, path: AnyPath, content_type: Optional[str] = None, inline: bool = False
    ) -> "BytesAttachment":
        """
        Construct a `BytesAttachment` from the contents of the file at
        ``path``.  The filename of the attachment will be set to the basename
        of ``path``.  If ``content_type`` is `None`, the
        :mailheader:`Content-Type` is guessed based on ``path``'s file
        extension.
        """
        with open(path, "rb") as fp:
            content = fp.read()
        filename = os.path.basename(os.fsdecode(path))
        if content_type is None:
            content_type = get_mime_type(filename)
        return cls(
            content=content, filename=filename, content_type=content_type, inline=inline
        )


@attr.s(auto_attribs=True)
class EmailAttachment(Attachment):
    """ A representation of a :mimetype:`message/rfc822` e-mail attachment """

    #: The body of the attachment
    content: EmailMessage
    #: The filename of the attachment
    filename: str
    #: Whether the attachment should be displayed inline in clients
    inline: bool = attr.ib(default=False, kw_only=True)

    def _compile(self) -> EmailMessage:
        msg = EmailMessage()
        msg.set_content(
            self.content,
            disposition="inline" if self.inline else "attachment",
            filename=self.filename,
        )
        return msg

    @classmethod
    def from_file(cls, path: AnyPath, inline: bool = False) -> "EmailAttachment":
        """
        Construct an `EmailAttachment` from the contents of the file at
        ``path``.  The filename of the attachment will be set to the basename
        of ``path``.
        """
        with open(path, "rb") as fp:
            content = message_from_binary_file(fp, policy=policy.default)
            assert isinstance(content, EmailMessage)
        filename = os.path.basename(os.fsdecode(path))
        return cls(content=content, filename=filename, inline=inline)


def mail_item_list(xs: Iterable[MailItem]) -> List[MailItem]:
    return list(xs)


@attr.s
class Alternative(MailItem):
    content: List[MailItem] = attr.ib(converter=mail_item_list)

    def _compile(self) -> EmailMessage:
        if not self.content:
            raise ValueError("Cannot compose empty Alternative")
        msg = EmailMessage()
        msg.make_alternative()
        for mi in self.content:
            msg.attach(mi._compile())
        return msg

    def __ior__(self, other: MailItem) -> "Alternative":
        if isinstance(other, Alternative):
            self.content.extend(other.content)
        else:
            self.content.append(other)
        return self


@attr.s
class Mixed(MailItem):
    content: List[MailItem] = attr.ib(converter=mail_item_list)

    def _compile(self) -> EmailMessage:
        if not self.content:
            raise ValueError("Cannot compose empty Mixed")
        msg = EmailMessage()
        msg.make_mixed()
        for mi in self.content:
            msg.attach(mi._compile())
        return msg

    def __iadd__(self, other: MailItem) -> "Mixed":
        if isinstance(other, Mixed):
            self.content.extend(other.content)
        else:
            self.content.append(other)
        return self


@attr.s(auto_attribs=True)
class TextBody(MailItem):
    content: str

    def _compile(self) -> EmailMessage:
        msg = EmailMessage()
        msg.set_content(self.content)
        return msg


@attr.s(auto_attribs=True)
class HTMLBody(MailItem):
    content: str

    def _compile(self) -> EmailMessage:
        msg = EmailMessage()
        msg.set_content(self.content, subtype="html")
        return msg
