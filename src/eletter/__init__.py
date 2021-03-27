"""
Simple e-mail composition & decomposition

``eletter`` provides functionality for constructing & deconstructing
`email.message.EmailMessage` instances without having to touch the needlessly
complicated `EmailMessage` class itself.  A simple function enables composition
of e-mails with text and/or HTML bodies plus attachments, and classes are
provided for composing more complex multipart e-mails.

Visit <https://github.com/jwodder/eletter> or <https://eletter.rtfd.io> for
more information.
"""

__version__ = "0.5.0"
__author__ = "John Thorvald Wodder II"
__author_email__ = "eletter@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/eletter"

from mailbits import format_addresses
from .classes import (
    Address,
    Alternative,
    Attachment,
    BytesAttachment,
    EmailAttachment,
    Group,
    HTMLBody,
    MailItem,
    Mixed,
    Multipart,
    Related,
    TextAttachment,
    TextBody,
)
from .core import assemble_content_type, compose, reply_quote
from .decompose import Eletter, SimpleEletter, decompose, decompose_simple
from .errors import DecompositionError, Error, MixedContentError, SimplificationError

__all__ = [
    "Address",
    "Alternative",
    "Attachment",
    "BytesAttachment",
    "DecompositionError",
    "Eletter",
    "EmailAttachment",
    "Error",
    "Group",
    "HTMLBody",
    "MailItem",
    "Mixed",
    "MixedContentError",
    "Multipart",
    "Related",
    "SimpleEletter",
    "SimplificationError",
    "TextAttachment",
    "TextBody",
    "assemble_content_type",
    "compose",
    "decompose",
    "decompose_simple",
    "format_addresses",
    "reply_quote",
]
