from collections.abc import Iterable as IterableABC
from email import headerregistry as hr
from mimetypes import guess_type
import os
from typing import Iterable, List, Union

AnyPath = Union[bytes, str, "os.PathLike[bytes]", "os.PathLike[str]"]

SingleAddress = Union[str, hr.Address]

AddressOrGroup = Union[str, hr.Address, hr.Group]


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
