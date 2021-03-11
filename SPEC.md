- Add a `decompose()` function for converting an EmailMessage to an OO
  representation? (as an `ELetter` object with `content: Composable`, `subject`,
  `from_`, etc. fields)
    - Include a `parse_addresses()` function for parsing unhandled address
      headers (like Resent-To) into lists of `Group` and `Address` objects
    - This may require letting attachments' `filename`s be `None`

- Add a `decompose_simple()` function for converting an EmailMessage to a
  `SimpleELetter` object with `text`, `html`, `attachments`, `subject`,
  `from_`, etc. fields?
    - Give basic decomposed objects a `simplify()` method for
      simple-decomposition?
    - Give the function & method an `unmix=False` parameter for controlling
      whether to "unmix" attachments in the middle of a `multipart/mixed`?
    - Add an `unrelate=False` parameter for whether to decompose
      `multipart/related` messages?
