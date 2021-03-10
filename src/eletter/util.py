from collections.abc import Iterable as IterableABC
from email import headerregistry as hr
from email.message import EmailMessage
from mimetypes import guess_type
import os
from typing import Any, Dict, Iterable, List, Tuple, Union
import attr

AnyPath = Union[bytes, str, "os.PathLike[bytes]", "os.PathLike[str]"]

SingleAddress = Union[str, hr.Address]

AddressOrGroup = Union[str, hr.Address, hr.Group]


@attr.s(auto_attribs=True)
class ContentType:
    maintype: str
    subtype: str
    params: Dict[str, Any]

    @classmethod
    def parse(cls, s: str) -> "ContentType":
        maintype, subtype, params = parse_content_type(s)
        return cls(maintype, subtype, params)


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
