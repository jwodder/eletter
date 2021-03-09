Python module for simple e-mail construction

- Make message/MIME objects support combining into a multipart sequence with
  `__add__` and combining into a `multipart/alternative` with `__or__`

- Complex composition:

        MailItem(ABC):
            @abstractmethod
            def _compile() -> EmailMessage

            # All MailItems (or at least attachments and bodies) have a
            # nullable `content_id` attribute that the user must set themselves
            # if they want to use.

        Composable(MailItem):
            compose(subject, from_, ...) -> EmailMessage

        Attachment(MailItem)

        TextBody(Composable)
            __init__(content: str, subtype="plain")
        HTMLBody(Composable)
            __init__(content: str, subtype="html")

        MailItem + MailItem = Mixed
        MailItem | MailItem = Alternative

        Mixed([MailItem, ...])  # Implements Composable
        Alternative([MailItem, ...])  # Implements Composable

        Mixed += Mixed
        Alternative |= Alternative

    - TODO: Support multipart/related somehow (just with construction via
      `Related([MailItem, ...])`?)

- Add a `decompose()` function for converting an EmailMessage to an OO
  representation? (as an `ELetter` object with `content: Composable`, `subject`,
  `from_`, etc. fields)
    - Include a `parse_addresses()` function for parsing unhandled address
      headers (like Resent-To) into lists of `Group` and `Address` objects

- Add a `decompose_simple()` function for converting an EmailMessage to a
  `SimpleELetter` object with `text`, `html`, `attachments`, `subject`,
  `from_`, etc. fields?
    - Give basic decomposed objects a `simplify()` method for
      simple-decomposition?
