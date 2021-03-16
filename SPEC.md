- Add a `decompose_simple()` function for converting an EmailMessage to a
  `SimpleEletter` object with `text`, `html`, `attachments`, `subject`,
  `from_`, etc. fields?
    - Give basic decomposed objects a `simplify()` method for
      simple-decomposition?
    - Give the function & method an `unmix=False` parameter for controlling
      whether to "unmix" attachments in the middle of a `multipart/mixed`?
