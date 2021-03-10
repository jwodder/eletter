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
