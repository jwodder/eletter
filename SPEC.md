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

- Support lists for `from_` and `reply_to`?
- Replace `Address` with the one in headerregistry?
    - Make my `Address` a subclass or wrapper around the stdlib one?
- Support address groups?
- Allow `Any` as values for headers?

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

- Give `BytesAttachment` and `TextAttachment` a `from_file(path,
  content_type=None)` classmethod
