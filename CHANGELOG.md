v0.5.0 (2021-03-27)
-------------------
- Attachments' filenames can now be `None`
- Added a `decompose()` function for decomposing an `EmailMessage` into a
  `MailItem` plus headers
- Added a `decompose_simple()` function for decomposing an `EmailMessage` into
  a text body, HTML body, attachments, and headers
- The `subject` argument to the `compose()` function & method can now be
  `None`/omitted
- If an address argument to `compose()` is set to an empty list, the
  corresponding header will no longer be present in the resulting e-mail
- Gave `Related` a `get_root()` method

v0.4.0 (2021-03-13)
-------------------
- Using `|`, `&`, or `^` on a `MailItem` and a `str` now automatically converts
  the `str` to a `TextBody`
- The `from_` argument to the `compose()` function & method can now be
  `None`/omitted
- `format_addresses()` has been moved to
  [mailbits](https://github.com/jwodder/mailbits) but is still re-exported from
  this library for the time being.
- **Breaking**: All arguments to the `compose()` function & method are now
  keyword-only

v0.3.0 (2021-03-11)
-------------------
- Gave the `from_file()` classmethods `inline` and `content_id` arguments
- Gave all classes optional `content_id` attributes
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
