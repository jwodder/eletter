"""
Simple e-mail composition

``eletter`` provides a basic function for constructing an
`email.message.EmailMessage` instance without having to touch the needlessly
complicated `EmailMessage` class itself.  E-mails with text bodies and/or HTML
bodies plus attachments are supported.  Support for more complex e-mails is
planned for later.

Visit <https://github.com/jwodder/eletter> for more information.
"""

__version__ = "0.3.0.dev1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "eletter@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/eletter"

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
from .core import assemble_content_type, compose, format_addresses, reply_quote

__all__ = [
    "Address",
    "Alternative",
    "Attachment",
    "BytesAttachment",
    "EmailAttachment",
    "Group",
    "HTMLBody",
    "MailItem",
    "Mixed",
    "Multipart",
    "Related",
    "TextAttachment",
    "TextBody",
    "assemble_content_type",
    "compose",
    "format_addresses",
    "reply_quote",
]
