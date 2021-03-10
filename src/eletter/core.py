from datetime import datetime
from email.message import EmailMessage
from typing import Iterable, Mapping, Optional, Union
from .classes import Attachment, HTMLBody, MailItem, TextBody
from .util import AddressOrGroup, SingleAddress, compile_addresses


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
    :mailheader:`From` address, :mailheader:`To` addresses, and a plain text
    and/or HTML body, optionally accompanied by attachments and other headers.

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
    :param attachments:
        A collection of :ref:`attachments <attachments>` to append to the
        e-mail
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
    msg: Optional[MailItem] = None
    if text is not None:
        msg = TextBody(text)
    if html is not None:
        if msg is None:
            msg = HTMLBody(html)
        else:
            msg |= HTMLBody(html)
    if msg is None:
        raise ValueError("At least one of text and html must be non-None")
    if attachments is not None:
        for a in attachments:
            msg &= a
    return msg.compose(
        subject=subject,
        from_=from_,
        to=to,
        cc=cc,
        bcc=bcc,
        reply_to=reply_to,
        sender=sender,
        date=date,
        headers=headers,
    )


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
    Format a sequence of addresses for use in a custom address header string
    """
    msg = EmailMessage()
    msg["To"] = compile_addresses(addresses)
    return str(msg["To"])
