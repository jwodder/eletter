Python module for simple e-mail construction

- Support lists for `from_` and `reply_to`?
- Support address groups?
- Allow `Any` as values for headers?
    - Add a function for converting an iterable of eletter addresses (and
      groups) to a list of headerregistry Groups and Addresses?

- Include a `reply_quote(text, prefix="> ")` function for prepending a prefix
  to all lines in a string

- Make message/MIME objects support combining into a multipart sequence with
  `__add__` and combining into a `multipart/alternative` with `__or__`

- Complex composition:

    MailItem(ABC):
        @abstractmethod
        def _compile() -> EmailMessage

    Composable(MailItem):
        compose(subject, from_, ...) -> EmailMessage

    Attachment(MailItem)
    BytesAttachment(Attachment)
        __init__(filename: str, content: bytes, filename: str, content_type: str = "application/octet-stream", inline: bool = False)
    TextAttachment(Attachment)
        __init__(filename: str, content: str, filename: str, content_type: str = "text/plain", inline: bool = False)
    EmailAttachment(Attachment)
        __init__(filename: str, content: EmailMessage, filename: str, content_type: str = "message/rfc822", inline: bool = False)

    TextBody(Composable)
        __init__(content: str, subtype="plain")
    HTMLBody(Composable)
        __init__(content: str, subtype="html")

    MailItem + MailItem = Mixed
    MailItem | MailItem = Alternative

    Mixed([MailItem, ...])
    Alternative([MailItem, ...])

    Mixed += Mixed
    Alternative |= Alternative

    # Support multipart/related somehow

- Add a `decompose()` function for converting an EmailMessage to an OO
  representation? (as an `ELetter` object with `content: Composable`, `subject`,
  `from_`, etc. fields)

- Add a `decompose_simple()` function for converting an EmailMessage to a
  `SimpleELetter` object with `text`, `html`, `attachments`, `subject`,
  `from_`, etc. fields?

- Add & export an `assemble_content_type(maintype, subtype, **params)`
  function?
