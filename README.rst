.. image:: http://www.repostatus.org/badges/latest/active.svg
    :target: http://www.repostatus.org/#active
    :alt: Project Status: Active — The project has reached a stable, usable
          state and is being actively developed.

.. image:: https://github.com/jwodder/eletter/workflows/Test/badge.svg?branch=master
    :target: https://github.com/jwodder/eletter/actions?workflow=Test
    :alt: CI Status

.. image:: https://codecov.io/gh/jwodder/eletter/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/jwodder/eletter

.. image:: https://img.shields.io/pypi/pyversions/eletter.svg
    :target: https://pypi.org/project/eletter/

.. image:: https://img.shields.io/github/license/jwodder/eletter.svg
    :target: https://opensource.org/licenses/MIT
    :alt: MIT License

`GitHub <https://github.com/jwodder/eletter>`_
| `PyPI <https://pypi.org/project/eletter/>`_
| `Issues <https://github.com/jwodder/eletter/issues>`_
| `Changelog <https://github.com/jwodder/eletter/blob/master/CHANGELOG.md>`_

``eletter`` provides a basic function for constructing an
``email.message.EmailMessage`` instance without having to touch the needlessly
complicated ``EmailMessage`` class itself.  E-mails with text bodies and/or
HTML bodies plus attachments are supported.  Support for more complex e-mails
is planned for later.


Installation
============
``eletter`` requires Python 3.6 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install
``eletter`` and its dependencies::

    python3 -m pip install eletter


Example
=======

.. code:: python

    import eletter

    TEXT = (
        "Oh my beloved!\n"
        "\n"
        "Wilt thou dine with me on the morrow?\n"
        "\n"
        "We're having hot pockets.\n"
        "\n"
        "Love, Me\n"
    )

    HTML = (
        "<p>Oh my beloved!</p>\n"
        "<p>Wilt thou dine with me on the morrow?</p>\n"
        "<p>We're having <strong>hot pockets</strong>.<p>\n"
        "<p><em>Love</em>, Me</p>\n"
    )

    with open("hot-pocket.png", "rb") as fp:
        picture = eletter.BytesAttachment(
            content=fp.read(),
            filename="enticement.png",
            content_type="image/png",
        )

    msg = eletter.compose(
        subject="Meet Me",
        from_="me@here.qq",
        to=[eletter.Address("My Dear", "my.beloved@love.love")],
        text=TEXT,
        html=HTML,
        attachments=[picture],
    )

    # Now you can send `msg` like any other EmailMessage, say, by using
    # outgoing <https://github/jwodder/outgoing>.


API
===

.. code:: python

    eletter.compose(
        subject: str,
        from_: Union[AnyAddress, Iterable[AnyAddress]],
        to: Iterable[AnyAddress],
        text: Optional[str] = None,
        html: Optional[str] = None,
        cc: Optional[Iterable[AnyAddress]] = None,
        bcc: Optional[Iterable[AnyAddress]] = None,
        reply_to: Optional[Union[AnyAddress, Iterable[AnyAddress]]] = None,
        sender: Optional[AnyAddress] = None,
        date: Optional[datetime.datetime] = None,
        attachments: Optional[Iterable[Attachment]] = None,
        headers: Optional[Mapping[str, Union[str, Iterable[str]]]] = None,
    ) -> email.message.EmailMessage

Construct an ``EmailMessage`` instance from a subject, "From:" address, "To:"
value, and a plain text and/or HTML body, optionally accompanied by attachments
and other headers.

Arguments:

``subject`` : string (required)
    The e-mail's "Subject:" line

``from_`` : address or iterable of addresses (required)
    The e-mail's "From:" line.  Note that this argument is spelled with an
    underscore, as "``from``" is a keyword in Python.

``to`` : iterable of addresses (required)
    The e-mail's "To:" line

``text`` : string
    The contents of a ``text/plain`` body for the e-mail.  At least one of
    ``text`` and ``html`` must be specified.

``html`` : string
    The contents of a ``text/html`` body for the e-mail.  At least one of
    ``text`` and ``html`` must be specified.

``cc`` : iterable of addresses (optional)
    The e-mail's "CC:" line

``bcc`` : iterable of addresses (optional)
    The e-mail's "BCC:" line

``reply_to`` : address or iterable of addresses (optional)
    The e-mail's "Reply-To:" line

``sender`` : address (optional)
    The e-mail's "Sender:" line.  The address must be a string or ``Address``,
    not a ``Group``.

``date`` : datetime (optional)
    The e-mail's "Date:" line

``attachments`` : iterable of attachments (optional)
    A collection of attachments (see "Attachments_") to append to the e-mail

``headers`` : mapping from header names to strings or iterables of strings (optional)
    A collection of additional headers to add to the e-mail.  A header value
    may be either a single string or an iterable of strings to add multiple
    headers with the same name.  If you wish to set an otherwise-unsupported
    address header like ``Resent-From`` to a list of addresses, use the
    ``format_addresses()`` function to first convert the addresses to a string.


Addresses
---------

Addresses in ``eletter`` can be specified in three ways:

- As an ``"address@domain.com"`` string giving just a bare e-mail address

- As an ``eletter.Address("Display Name", "address@domain.com")`` instance
  pairing a person's name with an e-mail address

- As an ``eletter.Group("Group Name", iterable_of_addresses)`` instance
  specifying a group of addresses (strings or ``Address`` instances)

**Note:** ``eletter.Address`` and ``eletter.Group`` are actually just
subclasses of ``Address`` and ``Group`` from ``email.headerregistry`` with
slightly more convenient constructors.  You can also use the standard library
types directly, if you want to.


Attachments
-----------

``eletter`` has three concrete attachment classes: ``BytesAttachment``,
``TextAttachment``, and ``EmailAttachment``.

``BytesAttachment``
~~~~~~~~~~~~~~~~~~~

.. code:: python

    eletter.BytesAttachment(
        content: bytes,
        filename: str,
        *,
        content_type: str = "application/octet-stream",
        inline: bool = False,
    )

Representation of a binary attachment.  Besides using the constructor,
instances can also be constructed via the ``from_file()`` classmethod:

.. code:: python

    @classmethod
    eletter.BytesAttachment.from_file(
        cls,
        path: Union[bytes, str, os.PathLike],
        content_type: Optional[str] = None,
    ) -> BytesAttachment

Construct a ``BytesAttachment`` from the contents of the file at ``path``.  The
filename of the attachment will be set to the basename of ``path``.  If
``content_type`` is ``None``, the Content-Type is guessed based on ``path``'s
file extension.

``TextAttachment``
~~~~~~~~~~~~~~~~~~

.. code:: python

    eletter.TextAttachment(
        content: str,
        filename: str,
        *,
        content_type: str = "text/plain",
        inline: bool = False,
    )

Representation of a text attachment.  The content type must have a maintype of
"text".  Besides using the constructor, instances can also be constructed via
the ``from_file()`` classmethod:

.. code:: python

    @classmethod
    eletter.TextAttachment.from_file(
        cls,
        path: Union[bytes, str, os.PathLike],
        content_type: Optional[str] = None,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
    ) -> TextAttachment

Construct a ``TextAttachment`` from the contents of the file at ``path``.  The
filename of the attachment will be set to the basename of ``path``.  If
``content_type`` is ``None``, the Content-Type is guessed based on ``path``'s
file extension.  ``encoding`` and ``errors`` are used when opening the file and
have no relation to the Content-Type.

``EmailAttachment``
~~~~~~~~~~~~~~~~~~~

.. code:: python

    eletter.EmailAttachment(
        content: email.message.EmailMessage,
        filename: str,
        *,
        inline: bool = False,
    )

Representation of a ``message/rfc822`` attachment.  Besides using the
constructor, instances can also be constructed via the ``from_file()``
classmethod:

.. code:: python

    @classmethod
    eletter.EmailAttachment.from_file(
        cls,
        path: Union[bytes, str, os.PathLike],
    ) -> EmailAttachment

Construct an ``EmailAttachment`` from the contents of the file at ``path``.
The filename of the attachment will be set to the basename of ``path``.


Utility Functions
-----------------

.. code:: python

    eletter.assemble_content_type(maintype: str, subtype: str, **params: str) -> str

Construct a Content-Type string from a maintype, subtype, and some number of
parameters

.. code:: python

    eletter.format_addresses(addresses: Iterable[AnyAddress]) -> str

Format a sequence of addresses for use in a custom address header field.

.. code:: python

    eletter.reply_quote(s: str, prefix: str = "> ") -> str

Quote__ a text following the *de facto* standard for replying to an e-mail;
that is, prefix each line of the text with ``"> "`` (or a custom prefix), and
if a line already starts with the prefix, omit any trailing whitespace from the
newly-added prefix (so ``"> already quoted"`` becomes ``">> already quoted"``).

If the resulting string does not end with a newline, one is added.  The empty
string is treated as a single line.

__ https://en.wikipedia.org/wiki/Usenet_quoting
