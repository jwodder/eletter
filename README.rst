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
        from_: Union[str, Address],
        to: Iterable[Union[str, Address]],
        text: Optional[str] = None,
        html: Optional[str] = None,
        cc: Optional[Iterable[Union[str, Address]]] = None,
        bcc: Optional[Iterable[Union[str, Address]]] = None,
        reply_to: Optional[Union[str, Address]] = None,
        sender: Optional[Union[str, Address]] = None,
        date: Optional[datetime.datetime] = None,
        attachments: Optional[Iterable[Attachment]] = None,
        headers: Optional[Mapping[str, Union[str, Iterable[str]]]] = None,
    ) -> email.message.EmailMessage

Construct an ``EmailMessage`` instance from a subject, "From:" address, "To:"
value, and a plain text and/or HTML body, optionally accompanied by attachments
and other headers.

Addresses are specified as either ``"address@domain.com"`` strings or as
``eletter.Address("Display Name", "address@domain.com")`` objects.

Arguments:

``subject`` : string (required)
    The e-mail's "Subject:" line

``from_`` : address (required)
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

``reply_to`` : address (optional)
    The e-mail's "Reply-To:" line

``sender`` : address (optional)
    The e-mail's "Sender:" line

``date`` : datetime (optional)
    The e-mail's "Date:" line

``attachments`` : iterable of attachments (optional)
    A collection of attachments (see below) to append to the e-mail

``headers`` : mapping from header names to strings or iterables of strings (optional)
    A collection of additional headers to add to the e-mail.  A header value
    may be either a single string or an iterable of strings to add multiple
    headers with the same name.


Attachment Objects
------------------

``eletter`` has two concrete attachment classes, ``TextAttachment`` and
``BytesAttachment``:

.. code:: python

    eletter.BytesAttachment(
        content: bytes,
        filename: str,
        content_type: str = "application/octet-stream",
        inline: bool = False,
    )

Representation of a binary attachment.

.. code:: python

    eletter.TextAttachment(
        content: str,
        filename: str,
        content_type: str = "text/plain",
        inline: bool = False,
    )

Representation of a text attachment.  The content type must have a maintype of
"text".
