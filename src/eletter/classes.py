from abc import ABC, abstractmethod
from collections.abc import Iterable as IterableABC
from datetime import datetime
from email import headerregistry as hr
from email import message_from_binary_file
from email import policy
from email.message import EmailMessage
import os
import os.path
from typing import (
    Iterable,
    List,
    Mapping,
    MutableSequence,
    Optional,
    TypeVar,
    Union,
    overload,
)
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
    """ An e-mail address group """

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


@attr.s
class MailItem(ABC):
    """ Base class for all ``eletter`` message components """

    #: :mailheader:`Content-ID` header value for the item
    content_id: Optional[str] = attr.ib(default=None, kw_only=True)

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
        """
        Convert the `MailItem` into an `~email.message.EmailMessage` with the
        item's contents as the payload and with the given subject,
        :mailheader:`From` address, :mailheader:`To` addresses, and optional
        other headers.

        :param str subject: The e-mail's :mailheader:`Subject` line
        :param from_:
            The e-mail's :mailheader:`From` line.  Note that this argument is
            spelled with an underscore, as "``from``" is a keyword in Python.
        :type from_: address or iterable of addresses
        :param to: The e-mail's :mailheader:`To` line
        :type to: iterable of addresses
        :param cc: The e-mail's :mailheader:`CC` line
        :type cc: iterable of addresses
        :param bcc: The e-mail's :mailheader:`BCC` line
        :type bcc: iterable of addresses
        :param reply_to: The e-mail's :mailheader:`Reply-To` line
        :type reply_to: address or iterable of addresses
        :param address sender:
            The e-mail's :mailheader:`Sender` line.  The address must be a
            string or `Address`, not a `Group`.
        :param datetime date: The e-mail's :mailheader:`Date` line
        :param mapping headers:
            A collection of additional headers to add to the e-mail.  A header
            value may be either a single string or an iterable of strings to add
            multiple headers with the same name.  If you wish to set an
            otherwise-unsupported address header like :mailheader:`Resent-From`
            to a list of addresses, use the `format_addresses()` function to
            first convert the addresses to a string.
        :rtype: email.message.EmailMessage
        """
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

    def __and__(self, other: "MailItem") -> "Mixed":
        parts: List[MailItem] = []
        for mi in [self, other]:
            if isinstance(mi, Mixed):
                parts.extend(mi.content)
            else:
                parts.append(mi)
        return Mixed(parts)

    def __xor__(self, other: "MailItem") -> "Related":
        parts: List[MailItem] = []
        for mi in [self, other]:
            if isinstance(mi, Related):
                parts.extend(mi.content)
            else:
                parts.append(mi)
        return Related(parts)


class Attachment(MailItem):
    """ Base class for the attachment classes """

    pass


@attr.s(auto_attribs=True)
class TextAttachment(Attachment, ContentTyped):
    """
    A textual e-mail attachment.  ``content_type`` defaults to ``"text/plain"``
    and must have a maintype of :mimetype:`text`.
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
            cid=self.content_id,
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
        content_id: Optional[str] = None,
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
            content=content,
            filename=filename,
            content_type=content_type,
            inline=inline,
            content_id=content_id,
        )


@attr.s(auto_attribs=True)
class BytesAttachment(Attachment, ContentTyped):
    """
    A binary e-mail attachment.  `content_type` defaults to
    ``"application/octet-stream"``.
    """

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
            cid=self.content_id,
        )
        return msg

    @classmethod
    def from_file(
        cls,
        path: AnyPath,
        content_type: Optional[str] = None,
        inline: bool = False,
        content_id: Optional[str] = None,
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
            content=content,
            filename=filename,
            content_type=content_type,
            inline=inline,
            content_id=content_id,
        )


@attr.s(auto_attribs=True)
class EmailAttachment(Attachment):
    """ A :mimetype:`message/rfc822` e-mail attachment """

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
            cid=self.content_id,
        )
        return msg

    @classmethod
    def from_file(
        cls, path: AnyPath, inline: bool = False, content_id: Optional[str] = None
    ) -> "EmailAttachment":
        """
        Construct an `EmailAttachment` from the contents of the file at
        ``path``.  The filename of the attachment will be set to the basename
        of ``path``.
        """
        with open(path, "rb") as fp:
            content = message_from_binary_file(fp, policy=policy.default)
            assert isinstance(content, EmailMessage)
        filename = os.path.basename(os.fsdecode(path))
        return cls(
            content=content, filename=filename, inline=inline, content_id=content_id
        )


def mail_item_list(xs: Iterable[MailItem]) -> List[MailItem]:
    return list(xs)


M = TypeVar("M", bound="Multipart")


@attr.s
class Multipart(MailItem, MutableSequence[MailItem]):
    """
    Base class for all multipart classes.  All such classes are mutable
    sequences of `MailItem`\\s supporting the usual methods (construction from
    an iterable, subscription, ``append()``, ``pop()``, etc.).
    """

    #: The `MailItem`\s contained within the instance
    content: List[MailItem] = attr.ib(factory=list, converter=mail_item_list)

    @overload
    def __getitem__(self, index: int) -> MailItem:
        ...

    @overload
    def __getitem__(self: M, index: slice) -> M:
        ...

    def __getitem__(self: M, index: Union[int, slice]) -> Union[MailItem, M]:
        if isinstance(index, int):
            return self.content[index]
        else:
            return type(self)(self.content[index])

    @overload
    def __setitem__(self, index: int, mi: MailItem) -> None:
        ...

    @overload
    def __setitem__(self, index: slice, mis: Iterable[MailItem]) -> None:
        ...

    def __setitem__(
        self, index: Union[int, slice], mi: Union[MailItem, Iterable[MailItem]]
    ) -> None:
        if isinstance(index, int):
            assert isinstance(mi, MailItem)
            self.content[index] = mi
        else:
            assert isinstance(mi, IterableABC)
            self.content[index] = mi

    def __delitem__(self: M, index: Union[int, slice]) -> None:
        del self.content[index]

    def __len__(self) -> int:
        return len(self.content)

    def insert(self, index: int, value: MailItem) -> None:
        """ :meta private: """
        self.content.insert(index, value)

    def append(self, value: MailItem) -> None:
        """ :meta private: """
        self.content.append(value)

    def reverse(self) -> None:
        """ :meta private: """
        self.content.reverse()

    def extend(self, values: Iterable[MailItem]) -> None:
        """ :meta private: """
        self.content.extend(values)

    def pop(self, index: int = -1) -> MailItem:
        """ :meta private: """
        return self.content.pop(index)

    def remove(self, value: MailItem) -> None:
        """ :meta private: """
        self.content.remove(value)

    def __iadd__(self: M, other: Iterable[MailItem]) -> M:
        self.content.extend(other)
        return self


@attr.s
class Alternative(Multipart):
    """
    A :mimetype:`multipart/alternative` e-mail payload.  E-mails clients will
    display the resulting payload by choosing whichever part they support best.

    An `Alternative` instance can be created by combining two or more
    `MailItem`\\s with the ``|`` operator:

    .. code:: python

        text = TextBody("This is displayed on plain text clients.\\n")
        html = HTMLBody("<p>This is displayed on graphical clients.<p>\\n")

        alternative = text | html

    Likewise, additional `MailItem`\\s can be added to an `Alternative`
    instance with the ``|=`` operator:

    .. code:: python

        # Same as above:
        alternative = Alternative()
        alternative |= TextBody("This is displayed on plain text clients.\\n")
        alternative |= HTMLBody("<p>This is displayed on graphical clients.<p>\\n")

    When combining two `Alternative` instances with ``|`` or ``|=``, the
    contents are "flattened":

    .. code:: python

        # Same as above:
        txtalt = Alternative([
            TextBody("This is displayed on plain text clients.\\n")
        ])
        htmlalt = Alternative([
            HTMLBody("<p>This is displayed on graphical clients.<p>\\n")
        ])
        alternative = txtalt | htmlalt
        assert alternative.contents == [
            TextBody("This is displayed on plain text clients.\\n"),
            HTMLBody("<p>This is displayed on graphical clients.<p>\\n"),
        ]
    """

    def _compile(self) -> EmailMessage:
        if not self.content:
            raise ValueError("Cannot compose empty Alternative")
        msg = EmailMessage()
        msg.make_alternative()
        for mi in self.content:
            msg.attach(mi._compile())
        if self.content_id is not None:
            msg["Content-ID"] = self.content_id
        return msg

    def __ior__(self, other: MailItem) -> "Alternative":
        if isinstance(other, Alternative):
            self.content.extend(other.content)
        else:
            self.content.append(other)
        return self


@attr.s
class Mixed(Multipart):
    """
    A :mimetype:`multipart/mixed` e-mail payload.  E-mails clients will
    display the resulting payload one part after another, with attachments
    displayed inline if their ``inline`` attribute is set.

    A `Mixed` instance can be created by combining two or more `MailItem`\\s
    with the ``&`` operator:

    .. code:: python

        text = TextBody("Look at the pretty kitty!\\n")
        image = BytesAttachment.from_file("snuffles.jpeg", inline=True)
        sig = TextBody("Sincerely, Me\\n")

        mixed = text & image & sig

    Likewise, additional `MailItem`\\s can be added to a `Mixed` instance with
    the ``&=`` operator:

    .. code:: python

        # Same as above:
        mixed = Mixed()
        mixed &= TextBody("Look at the pretty kitty!\\n")
        mixed &= BytesAttachment.from_file("snuffles.jpeg", inline=True)
        mixed &= TextBody("Sincerely, Me\\n")

    When combining two `Mixed` instances with ``&`` or ``&=``, the contents are
    "flattened":

    .. code:: python

        part1 = Mixed()
        part1 &= TextBody("Look at the pretty kitty!\\n")
        part1 &= BytesAttachment.from_file("snuffles.jpeg", inline=True)

        part2 = Mixed()
        part2 &= TextBody("Now look at this dog.\\n")
        part2 &= BytesAttachment.from_file("rags.jpeg", inline=True)
        part2 &= TextBody("Which one is cuter?\\n")

        mixed = part1 & part2

        assert mixed.contents == [
            TextBody("Look at the pretty kitty!\\n"),
            BytesAttachment.from_file("snuffles.jpeg", inline=True),
            TextBody("Now look at this dog.\\n"),
            BytesAttachment.from_file("rags.jpeg", inline=True),
            TextBody("Which one is cuter?\\n"),
        ]
    """

    def _compile(self) -> EmailMessage:
        if not self.content:
            raise ValueError("Cannot compose empty Mixed")
        msg = EmailMessage()
        msg.make_mixed()
        for mi in self.content:
            msg.attach(mi._compile())
        if self.content_id is not None:
            msg["Content-ID"] = self.content_id
        return msg

    def __iand__(self, other: MailItem) -> "Mixed":
        if isinstance(other, Mixed):
            self.content.extend(other.content)
        else:
            self.content.append(other)
        return self


@attr.s(auto_attribs=True)
class Related(Multipart):
    """
    A :mimetype:`multipart/related` e-mail payload.  E-mail clients will
    display the part indicated by the `start` parameter, or the first part if
    `start` is not set.  This part may refer to other parts (e.g., images or
    CSS stylesheets) by their :mailheader:`Content-ID` headers, which can be
    generated using `email.utils.make_msgid()`.

    .. note::

        :mailheader:`Content-ID` headers begin & end with angle brackets
        (``<...>``), which need to be stripped off before including the ID in
        the starting part.

    A `Related` instance can be created by combining two or more `MailItem`\\s
    with the ``^`` operator:

    .. code:: python

        from email.utils import make_msgid

        img_cid = make_msgid()

        html = HTMLBody(
            "<p>Look at the pretty kitty!</p>"
            f'<img src="cid:{img_cid[1:-1]}"/>"
            "<p>Isn't he <em>darling</em>?</p>"
        )

        image = BytesAttachment.from_file("snuffles.jpeg", content_id=img_cid)

        related = html ^ image

    Likewise, additional `MailItem`\\s can be added to a `Related` instance
    with the ``^=`` operator:

    .. code:: python

        # Same as above:

        img_cid = make_msgid()

        related = Related()

        related ^= HTMLBody(
            "<p>Look at the pretty kitty!</p>"
            f'<img src="cid:{img_cid[1:-1]}"/>"
            "<p>Isn't he <em>darling</em>?</p>"
        )

        related ^= BytesAttachment.from_file("snuffles.jpeg", content_id=img_cid)

    When combining two `Related` instances with ``^`` or ``^=``, the contents
    are "flattened":

    .. code:: python

        # Same as above:

        img_cid = make_msgid()

        htmlrel = Related([
            HTMLBody(
                "<p>Look at the pretty kitty!</p>"
                f'<img src="cid:{img_cid[1:-1]}"/>"
                "<p>Isn't he <em>darling</em>?</p>"
            )
        ])

        imgrel = Related([
            BytesAttachment.from_file("snuffles.jpeg", content_id=img_cid)
        ])

        related = htmlrel ^ imgrel

        assert related.contents == [
            HTMLBody(
                "<p>Look at the pretty kitty!</p>"
                f'<img src="cid:{img_cid[1:-1]}"/>"
                "<p>Isn't he <em>darling</em>?</p>"
            ),
            BytesAttachment.from_file("snuffles.jpeg", content_id=img_cid),
        ]
    """

    #: The :mailheader:`Content-ID` of the part to display (defaults to the
    #: first part)
    start: Optional[str] = None

    def _compile(self) -> EmailMessage:
        if not self.content:
            raise ValueError("Cannot compose empty Related")
        msg = EmailMessage()
        msg.make_related()
        ctype: Optional[str] = None
        for mi in self.content:
            obj = mi._compile()
            if self.start is not None and mi.content_id == self.start:
                ctype = obj.get_content_type()
            msg.attach(obj)
        if self.content_id is not None:
            msg["Content-ID"] = self.content_id
        if ctype is None:
            ctype = msg.get_payload()[0].get_content_type()
        msg.set_param("type", ctype)
        if self.start is not None:
            msg.set_param("start", self.start)
        return msg

    def __ixor__(self, other: MailItem) -> "Related":
        if isinstance(other, Related):
            self.content.extend(other.content)
        else:
            self.content.append(other)
        return self


@attr.s(auto_attribs=True)
class TextBody(MailItem):
    """ A :mimetype:`text/plain` e-mail body """

    #: The plain text body
    content: str

    def _compile(self) -> EmailMessage:
        msg = EmailMessage()
        msg.set_content(self.content, cid=self.content_id)
        return msg


@attr.s(auto_attribs=True)
class HTMLBody(MailItem):
    """ A :mimetype:`text/html` e-mail body """

    #: The HTML source of the body
    content: str

    def _compile(self) -> EmailMessage:
        msg = EmailMessage()
        msg.set_content(self.content, subtype="html", cid=self.content_id)
        return msg
