Python module for simple e-mail construction

- Include a `reply_quote(text, prefix="> ")` function for prepending a prefix
  to all lines in a string
    - Also include functions for de-quoting text and deleting all quoted text?

- Non-multipart MIME objects should have `content: bytes` and?/or (for
  `text/*`) `text: str` attributes for getting & setting their contents

- Messages should have an `append` method that takes a MIME object or text
  string to add to the message.  When given a text string, if the last MIME
  subobject in the message is text, the string is appended to it instead of
  creating a new subobject; the user can prevent this by converting the string
  to a MIME object beforehand.

- On output/serialization, text objects are converted to quoted-printable
  UTF-8.  The user can override this by creating the text objects as explicit
  `MIMEText` (or whatever) objects with the appropriate parameters set.

- Addresses can be given in the following formats:
    - `'user@example.com'`
    - `'Egg Sampler <user@example.com>` ?
    - `('Egg Sampler', 'user@example.com')` ?
    - `Address('Egg Sampler', 'user@example.com')` (format used when returning
      addresses)

- Make message/MIME objects support combining into a multipart sequence with
  `__add__` and combining into a `multipart/alternative` with `__or__`

- Include a (hopefully small) number of functions for creating complete Message
  objects from simple specifications (e.g., addresses + subject + (text / text
  + html))
    - cf. <https://sendgrid.com/docs/API_Reference/api_v3.html>?

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
        ) -> email.message.EmailMessage

    - At least one of `text` and `html` must be set.
    - Addresses can be given as either strings (for just an e-mail address) or
      as `Address(realname, address)` objects

- Complex composition:
    
    MailItem(ABC):  # Mailable?
        abstractmethod: compose(subject, from_, ...) -> EmailMessage

    Attachment(MailItem)
    BytesAttachment(Attachment)
        __init__(filename: str, content: bytes, content_type: str = "application/octet-stream", inline: bool = False)
    TextAttachment(Attachment)
        __init__(filename: str, content: str, content_type: str = "text/plain", inline: bool = False)
    EmailAttachment(Attachment)
        __init__(filename: str, content: EmailMessage, content_type: str = "message/rfc822", inline: bool = False)

    TextBody(MailItem) ?
    HTMLBody(MailItem) ???

    MailItem + MailItem = MultipartMixed
    MailItem | MailItem = MultipartAlternative

    MultipartMixed([MailItem, ...])
    MultipartAlternative([MailItem, ...])

    MultipartMixed += MultipartMixed
    MultipartAlternative |= MultipartAlternative

    # Support multipart/related somehow
