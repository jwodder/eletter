from email import headerregistry as hr
from email.messages import EmailMessage
from typing import Iterable, NamedTuple, Optional, Union

class Address(NamedTuple):
    display_name: str
    address: str

def compose(
    subject: str,
    from_: Union[str, Address],
    to: Iterable[Union[str, Address]],
    text: Optional[str] = None,
    html: Optional[str] = None,
    # cc: Optional[Iterable[Union[str, Address]] = None,
    # bcc: Optional[Iterable[Union[str, Address]] = None,
    # attachments: Optional[Iterable[Attachment]] = None,
    # date: Optional[datetime] = None,
    # headers: Optional[Dict[str, Union[str, Iterable[str]]]] = None,
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
    return msg

def compile_address(addr: Union[str, Address]) -> hr.Address:
    if isinstance(addr, str):
        return hr.Address(addr_spec=str)
    else:
        return hr.Address(display_name=addr.display_name, addr_spec=addr.address)
