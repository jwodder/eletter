.. currentmodule:: eletter

Changelog
=========

v0.4.0 (in development)
-----------------------
- Using ``|``, ``&``, or ``^`` on a `MailItem` and a `str` now automatically
  converts the `str` to a `TextBody`
- The ``from_`` argument to the `compose()` function & method can now be
  `None`/omitted

v0.3.0 (2021-03-11)
-------------------
- Gave the `from_file()` classmethods ``inline`` and ``content_id`` arguments
- Gave all classes optional ``content_id`` attributes
- Added `TextBody`, `HTMLBody`, `Alternative`, `Mixed`, and `Related` classes
  for constructing complex e-mails

v0.2.0 (2021-03-09)
-------------------
- Gave `BytesAttachment` and `FileAttachment` each a `from_file()` classmethod
- The `from_` and `reply_to` arguments to `compose()` may now be passed lists
  of addresses
- Support address groups
- Added `assemble_content_type()`, `format_addresses()`, and `reply_quote()`
  utility functions
- Added an `EmailAttachment` class

v0.1.0 (2021-03-09)
-------------------
Initial release