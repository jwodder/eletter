"""
Simple e-mail composition

``eletter`` provides a basic function for constructing an
`email.message.EmailMessage` instance without having to touch the needlessly
complicated `EmailMessage` class itself.  E-mails with text bodies and/or HTML
bodies plus attachments are supported.  Support for more complex e-mails is
planned for later.

Visit <https://github.com/jwodder/eletter> for more information.
"""

__version__ = "0.2.0"
__author__ = "John Thorvald Wodder II"
__author_email__ = "eletter@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/eletter"

from abc import ABC, abstractmethod
from collections.abc import Iterable as IterableABC
from datetime import datetime
from email import headerregistry as hr
from email import message_from_binary_file
from email import policy
from email.message import EmailMessage
from mimetypes import guess_type
import os
import os.path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union
import attr

__all__ = [
    "Address",
    "Attachment",
    "BytesAttachment",
    "EmailAttachment",
    "Group",
    "TextAttachment",
    "assemble_content_type",
    "compose",
    "format_addresses",
    "reply_quote",
]

AnyPath = Union[bytes, str, "os.PathLike[bytes]", "os.PathLike[str]"]

SingleAddress = Union[str, hr.Address]

AddressOrGroup = Union[str, hr.Address, hr.Group]


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

    #: The :mailheader:`Content-Type` of the attachment
    content_type: str = attr.ib(
        kw_only=True,
        default=attr.Factory(lambda self: self.DEFAULT_CONTENT_TYPE, takes_self=True),
        on_setattr=cache_content_type,
    )
    _ct: ContentType = attr.ib(init=False, repr=False, eq=False, order=False)

    def __attrs_post_init__(self) -> None:
        cache_content_type(self, None, self.content_type)


class Attachment(ABC):
    """ Base class for the attachment classes """

    @abstractmethod
    def _compile(self) -> EmailMessage:
        ...


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
        return cls(content=content, filename=filename, content_type=content_type)


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
        cls, path: AnyPath, content_type: Optional[str] = None
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
        return cls(content=content, filename=filename, content_type=content_type)


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
    def from_file(cls, path: AnyPath) -> "EmailAttachment":
        """
        Construct an `EmailAttachment` from the contents of the file at
        ``path``.  The filename of the attachment will be set to the basename
        of ``path``.
        """
        with open(path, "rb") as fp:
            content = message_from_binary_file(fp, policy=policy.default)
            assert isinstance(content, EmailMessage)
        filename = os.path.basename(os.fsdecode(path))
        return cls(content=content, filename=filename)


def compose(
    subject: str,
    from_: Union[AddressOrGroup, Iterable[AddressOrGroup]],
    to: Iterable[AddressOrGroup],
    text: Optional[str] = None,
    html: Optional[str] = None,
    cc: Optional[Iterable[AddressOrGroup]] = None,
    bcc: Optional[Iterable[AddressOrGroup]] = None,
    reply_to: Optional[Union[AddressOrGroup, Iterable[AddressOrGroup]]] = None,
    sender: Optional[SingleAddress] = None,
    date: Optional[datetime] = None,
    headers: Optional[Mapping[str, Union[str, Iterable[str]]]] = None,
    attachments: Optional[Iterable[Attachment]] = None,
) -> EmailMessage:
    """
    Construct an `~email.message.EmailMessage` instance from a subject,
    :mailheader:`From` address, :mailheader:`To` value, and a plain text and/or
    HTML body, optionally accompanied by attachments and other headers.

    :param str subject: The e-mail's :mailheader:`Subject` line
    :param from_:
        The e-mail's :mailheader:`From` line.  Note that this argument is
        spelled with an underscore, as "``from``" is a keyword in Python.
    :type from_: address or iterable of addresses
    :param to: The e-mail's :mailheader:`To` line
    :type to: iterable of addresses
    :param str text:
        The contents of a :mimetype:`text/plain` body for the e-mail.  At least
        one of ``text`` and ``html`` must be specified.
    :param str html:
        The contents of a :mimetype:`text/html` body for the e-mail.  At least
        one of ``text`` and ``html`` must be specified.
    :param cc: The e-mail's :mailheader:`CC` line
    :type cc: iterable of addresses
    :param bcc: The e-mail's :mailheader:`BCC` line
    :type bcc: iterable of addresses
    :param reply_to: The e-mail's :mailheader:`Reply-To` line
    :type reply_to: address or iterable of addresses
    :param address sender:
        The e-mail's :mailheader:`Sender` line.  The address must be a string
        or `Address`, not a `Group`.
    :param datetime date: The e-mail's :mailheader:`Date` line
    :param attachments: A collection of attachments to append to the e-mail
    :type attachments: iterable of attachments
    :param mapping headers:
        A collection of additional headers to add to the e-mail.  A header
        value may be either a single string or an iterable of strings to add
        multiple headers with the same name.  If you wish to set an
        otherwise-unsupported address header like :mailheader:`Resent-From` to
        a list of addresses, use the `format_addresses()` function to first
        convert the addresses to a string.
    :rtype: email.message.EmailMessage
    :raises ValueError: if neither ``text`` nor ``html`` is set
    """
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


def compile_address(addr: SingleAddress) -> hr.Address:
    if isinstance(addr, str):
        return hr.Address(addr_spec=addr)
    else:
        return addr


def compile_addresses(
    addrs: Union[AddressOrGroup, Iterable[AddressOrGroup]]
) -> List[Union[hr.Address, hr.Group]]:
    if isinstance(addrs, str):
        return [hr.Address(addr_spec=addrs)]
    elif not isinstance(addrs, IterableABC):
        return [addrs]
    else:
        return [hr.Address(addr_spec=a) if isinstance(a, str) else a for a in addrs]


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


def assemble_content_type(maintype: str, subtype: str, **params: str) -> str:
    """
    Construct a :mailheader:`Content-Type` string from a maintype, subtype, and
    some number of parameters

    :raises ValueError: if ``f"{maintype}/{subtype}"`` is an invalid
        :mailheader:`Content-Type`
    """
    ct = f"{maintype}/{subtype}"
    msg = EmailMessage()
    msg["Content-Type"] = ct
    if msg["Content-Type"].defects:
        raise ValueError(ct)
    for k, v in params.items():
        msg.set_param(k, v)
    return str(msg["Content-Type"])


def reply_quote(s: str, prefix: str = "> ") -> str:
    """
    Quote__ a text following the *de facto* standard for replying to an e-mail;
    that is, prefix each line of the text with ``"> "`` (or a custom prefix),
    and if a line already starts with the prefix, omit any trailing whitespace
    from the newly-added prefix (so ``"> already quoted"`` becomes ``">>
    already quoted"``).

    If the resulting string does not end with a newline, one is added.  The
    empty string is treated as a single line.

    __ https://en.wikipedia.org/wiki/Usenet_quoting
    """
    s2 = ""
    for ln in (s or "\n").splitlines(True):
        if ln.startswith(prefix):
            s2 += prefix.rstrip() + ln
        else:
            s2 += prefix + ln
    if not s2.endswith(("\n", "\r")):
        s2 += "\n"
    return s2


def format_addresses(addresses: Iterable[AddressOrGroup]) -> str:
    """
    Format a sequence of addresses for use in a custom address header field
    """
    msg = EmailMessage()
    msg["To"] = compile_addresses(addresses)
    return str(msg["To"])
