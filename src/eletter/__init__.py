"""
Simple e-mail composition

Visit <https://github.com/jwodder/eletter> for more information.
"""

__version__ = "0.1.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "eletter@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/eletter"

from datetime import datetime
from email import headerregistry as hr
from email.message import EmailMessage
from typing import Iterable, List, Mapping, NamedTuple, Optional, Union


class Address(NamedTuple):
    display_name: str
    address: str


def compose(
    subject: str,
    from_: Union[str, Address],
    to: Iterable[Union[str, Address]],
    text: Optional[str] = None,
    html: Optional[str] = None,
    cc: Optional[Iterable[Union[str, Address]]] = None,
    bcc: Optional[Iterable[Union[str, Address]]] = None,
    reply_to: Optional[Union[str, Address]] = None,
    date: Optional[datetime] = None,
    headers: Optional[Mapping[str, Union[str, Iterable[str]]]] = None,
    # attachments: Optional[Iterable[Attachment]] = None,
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
    msg["Subject"] = subject
    msg["From"] = compile_address(from_)
    msg["To"] = list(map(compile_address, to))
    if cc is not None:
        msg["CC"] = list(map(compile_address, cc))
    if bcc is not None:
        msg["BCC"] = list(map(compile_address, bcc))
    if reply_to is not None:
        msg["Reply-To"] = compile_address(reply_to)
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
