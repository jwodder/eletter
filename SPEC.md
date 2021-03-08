Python module for simple e-mail construction

- Include a `reply_quote(text, prefix="> ")` function for prepending a prefix
  to all lines in a string
    - Also include functions for de-quoting text and deleting all quoted text?

- Non-multipart MIME objects should have `content: bytes` or (for `text/*`)
  `content: str` attributes for getting & setting their contents

- Addresses can be given in the following formats:
    - `'user@example.com'`
    - `Address('Egg Sampler', 'user@example.com')`

- Make message/MIME objects support combining into a multipart sequence with
  `__add__` and combining into a `multipart/alternative` with `__or__`

- Simple composition:

        compose(
            subject: str,
            text: Optional[str] = None,
            html: Optional[str] = None,
            from_: Union[str, Address],
            to: Iterable[Union[str, Address]],
            cc: Optional[Iterable[Union[str, Address]] = None,
            bcc: Optional[Iterable[Union[str, Address]] = None,
            attachments: Optional[Iterable[Attachment]] = None,
            date: Optional[datetime] = None,
            headers: Optional[Dict[str, Union[str, Iterable[str]]]] = None,
        ) -> email.message.EmailMessage

    - At least one of `text` and `html` must be set.
    - Addresses can be given as either strings (for just an e-mail address) or
      as `Address(realname, address)` objects

- Complex composition:

    ELetter(ABC):
        abstractmethod: compose(subject, from_, ...) -> EmailMessage

    Attachment(ELetter)
    BytesAttachment(Attachment)
        __init__(filename: str, content: bytes, content_type: str = "application/octet-stream", inline: bool = False)
    TextAttachment(Attachment)
        __init__(filename: str, content: str, content_type: str = "text/plain", inline: bool = False)
    EmailAttachment(Attachment)
        __init__(filename: str, content: EmailMessage, content_type: str = "message/rfc822", inline: bool = False)

    TextBody(ELetter)
        __init__(content: str, subtype="plain")
    HTMLBody(ELetter)
        __init__(content: str, subtype="html")

    ELetter + ELetter = Mixed
    ELetter | ELetter = Alternative

    Mixed([ELetter, ...])
    Alternative([ELetter, ...])

    Mixed += Mixed
    Alternative |= Alternative

    # Support multipart/related somehow
