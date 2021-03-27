.. currentmodule:: eletter

Tutorial
========

Basic Composition
-----------------

``eletter`` can be used to construct a basic text e-mail using the `compose()`
function like so:

.. code:: python

    from eletter import compose

    msg = compose(
        subject="The subject of the e-mail",
        from_="sender@domain.com",
        to=["recipient@domain.com", "another.recipient@example.nil"],
        text="This is the body of the e-mail.  Write what you want here!\n",
    )

.. note::

    Observe that the ``from_`` argument is spelled with an underscore.  It has
    to be this way, because plain old ``from`` is a keyword in Python.

If you want to construct an HTML e-mail, use the ``html`` keyword instead of
``text``:

.. code:: python

    from eletter import compose

    msg = compose(
        subject="The subject of the e-mail",
        from_="sender@domain.com",
        to=["recipient@domain.com", "another.recipient@example.nil"],
        html=(
            "<p>This is the <strong>body</strong> of the <em>e</em>-mail."
            "  <span style='color: red;'>Write what you want here!</span></p>\n"
        ),
    )

By specifying both ``text`` and ``html``, you'll get an e-mail whose HTML part
is displayed if the e-mail reader supports it and whose text part is displayed
instead on lower-tech clients.

.. code:: python

    from eletter import compose

    msg = compose(
        subject="The subject of the e-mail",
        from_="sender@domain.com",
        to=["recipient@domain.com", "another.recipient@example.nil"],
        text="This is displayed on plain text clients.\n",
        html="<p>This is displayed on graphical clients.<p>\n",
    )


Addresses
---------

In the examples so far, e-mail addresses have just been specified as, well,
addresses.  However, addresses usually belong to people or organizations with
names; we can include these names alongside the addresses by constructing
`Address` objects from pairs of "display names" and e-mail addresses:

.. code:: python

    from eletter import Address, compose

    msg = compose(
        subject="The subject of the e-mail",
        from_=Address("Sender's name goes here", "sender@domain.com"),
        to=[
            Address("Joe Q. Recipient", "recipient@domain.com"),
            Address("Jane Z. Another-Recipient", "another.recipient@example.nil"),
        ],
        text="This is the body of the e-mail.  Write what you want here!\n",
    )

Sometimes addresses come in named groups.  We can represent these with the
`Group` class, which takes a name for the group and an iterable of address
strings and/or `Address` objects:

.. code:: python

    from eletter import Address, Group, compose

    msg = compose(
        subject="The subject of the e-mail",
        from_="sender@domain.com",
        to=[
            Group(
                "friends",
                [
                    Address("Joe Q. Recipient", "recipient@domain.com"),
                    Address("Jane Z. Another-Recipient", "another.recipient@example.nil"),
                    "anonymous@nowhere.nil",
                ],
            ),
            Address("Mr. Not-in-a-Group", "ungrouped@unkno.wn"),
            Group(
                "enemies",
                [
                    "that.guy@over.there",
                    "knows.what.they.did@ancient.history",
                    Address("Anemones", "sea.flora@ocean.net"),
                ],
            ),
        ],
        text="This is the body of the e-mail.  Write what you want here!\n",
    )


CC, BCC, etc.
-------------

Besides :mailheader:`From` and :mailheader:`To` addresses, `compose()` also
accepts optional arguments for :mailheader:`CC`, :mailheader:`BCC`,
:mailheader:`Reply-To`, and :mailheader:`Sender` addresses:

.. code:: python

    from eletter import Address, compose

    msg = compose(
        from_=Address("Mme E.", "me@here.com"),
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        cc=[Address("Cee Cee Cecil", "ccc@seesaws.cc"), "coco@nu.tz"],
        bcc=[
            "eletter@depository.nil",
            Address("Secret Cabal", "illuminati@new.world.order"),
            "mom@house.home",
        ],
        reply_to="replyee@some.where",
        sender="steven.ender@big.senders",
        subject="To: Everyone",
        text="Meeting tonight!  You know the place.  Bring pizza.\n",
    )

.. note::

    The ``to``, ``cc``, and ``bcc`` arguments always take lists or iterables of
    addresses.  ``from_`` and ``reply_to``, on the other hand, can be set to
    either a single address or an iterable of addresses.  ``sender`` must
    always be a single address.


Attachments
-----------

Attachments come in two common types: text and binary.  ``eletter`` provides a
class for each, `TextAttachment` and `BytesAttachment`.

We can construct a `BytesAttachment` as follows:

.. code:: python

    from eletter import BytesAttachment

    attachment = BytesAttachment(
        b'... binary data goes here ...',
        filename="name-of-attachment.dat"
    )

This will create an :mimetype:`application/octet-stream` attachment with an
"attachment" disposition (meaning that most clients will just display it as a
clickable icon).  To set the content type to something more informative, set
the ``content_type`` parameter to the relevant MIME type.  To have the
attachment displayed inline (generally only an option for images & videos), set
the ``inline`` parameter to true.  Hence:

.. code:: python

    from eletter import BytesAttachment

    attachment = BytesAttachment(
        b'... binary data goes here ...',
        filename="name-of-attachment.png"
        content_type="image/png",
        inline=True,
    )

If your desired attachment exists as a file on your system, you can construct a `BytesAttachment` from the file directly with the `~BytesAttachment.from_file()` classmethod:

.. code:: python

    from eletter import BytesAttachment

    attachment = BytesAttachment.from_file(
        "path/to/file.dat",
        content_type="application/x-custom",
        inline=True,
    )

The basename of the given file will be used as the filename of the attachment.
(If you want to use a different name, set the `~BytesAttachment.filename`
attribute on the attachment after creating it.)  If ``content_type`` is not
given, the MIME type of the file will be guessed based on its file extension.

The `TextAttachment` class is analogous to `BytesAttachment`, except that it is
constructed from a `str` instead of `bytes`, and the ``content_type`` (which
defaults to ``"text/plain"``) must be a :mimetype:`text` type.

Once you've created some attachment objects, they can be attached to an e-mail
by passing them in a list as the ``attachments`` argument:

.. code:: python

    from eletter import BytesAttachment, TextAttachment, compose

    spreadsheet = TextAttachment.from_file("income.csv")
    image = BytesAttachment.from_file("cat.jpg")

    msg = compose(
        subject="That data you wanted",
        from_="sender@domain.com",
        to=["recipient@domain.com"],
        text="Here's that data you wanted, sir.  And also the ... other thing.\n",
        attachments=[spreadsheet, image],
    )


Attaching E-mails to E-mails
----------------------------

On rare occasions, you may have an e-mail that you want to completely embed in
a new e-mail as an attachment.  With ``eletter``, you can do this with the
`EmailAttachment` class.  It works the same as `BytesAttachment` and
`TextAttachment`, except that the content must be an
`email.message.EmailMessage` instance, and you can't set the
:mailheader:`Content-Type` (which is always :mimetype:`message/rfc822`).  Like
the other attachment classes, `EmailAttachment` also has a
`~EmailAttachment.from_file()` classmethod for constructing an instance from an
e-mail in a file.


Date and Extra Headers
----------------------

`compose()` takes two more parameters that we haven't mentioned yet.  First is
``date``, which lets you set the :mailheader:`Date` header in an e-mail to a
given `datetime.datetime` instance.  Second is ``headers``, which lets you set
arbitrary extra headers on an e-mail by passing in a `dict`.  Each value in the
`dict` must be either a string or (if you want to set multiple headers with the
same name) an iterable of strings.

.. code:: python

    from datetime import datetime
    from eletter import compose

    msg = compose(
        subject="The subject of the e-mail",
        from_="sender@domain.com",
        to=["recipient@domain.com", "another.recipient@example.nil"],
        text="This is the body of the e-mail.  Write what you want here!\n",
        date=datetime(2021, 3, 10, 17, 56, 36).astimezone(),
        headers={
            "User-Agent": "My Mail Application v.1",
            "Priority": "urgent",
            "Comments": [
                "I like e-mail.",
                "But no one ever looks at e-mails' sources, so no one will ever know.",
            ]
        },
    )


:mimetype:`multipart/mixed` Messages
------------------------------------

All the e-mails constructed so far, when viewed in an e-mail client, have their
attachments listed at the bottom.  What if we want to mix & match attachments
and text, switching from text to an attachment and then back to text?
``eletter`` lets you do this by providing `TextBody` and `HTMLBody` classes
that can be ``&``-ed with attachments to produce :mimetype:`multipart/mixed`
messages, like so:

.. code:: python

    from eletter import BytesAttachment, TextBody

    part1 = TextBody("Look at the pretty kitty!\n")

    snuffles = BytesAttachment.from_file("snuffles.jpeg", inline=True)

    part2 = TextBody("Now look at this dog.\n")

    rags = BytesAttachment.from_file("rags.jpeg", inline=True)

    part3 = TextBody("Which one is cuter?\n")

    mixed = part1 & snuffles & part2 & rags & part3

We can then convert ``mixed`` into an `~email.message.EmailMessage` by calling
its `~MailItem.compose()` method, which takes the same arguments as the
`compose()` function, minus ``text``, ``html``, and ``attachments``.

.. code:: python

    msg = mixed.compose(
        subject="The subject of the e-mail",
        from_="sender@domain.com",
        to=["recipient@domain.com", "another.recipient@example.nil"],
    )

When the resulting e-mail is viewed in a client, you'll see three lines of text
with images between them.

.. tip::

    As a shortcut, you can combine a bare `str` with an ``eletter`` object
    using ``|`` or the other overloaded operators described below (``&`` and
    ``^``), and that `str` will be automatically converted to a `TextBody`.
    The example above could thus be rewritten:

    .. code:: python

        from eletter import BytesAttachment, TextBody

        snuffles = BytesAttachment.from_file("snuffles.jpeg", inline=True)

        rags = BytesAttachment.from_file("rags.jpeg", inline=True)

        mixed = (
            "Look at the pretty kitty!\n"
            & snuffles
            & "Now look at this dog.\n"
            & rags
            & "Which one is cuter?\n"
        )


:mimetype:`multipart/alternative` Messages
------------------------------------------

Now that we know how to construct mixed messages, how do we use them to create
messages with both mixed-HTML and mixed-text payloads where the client shows
whichever mixed payload it can support?  The answer is the ``|`` operator;
using it to combine two ``eletter`` objects will give you a
:mimetype:`multipart/alternative` object, representing an e-mail message with
two different versions of the same content that the client will then pick
between.

.. code:: python

    from eletter import BytesAttachment, HTMLBody, TextBody

    text1 = TextBody("Look at the pretty kitty!\n")
    text2 = TextBody("Now look at this dog.\n")
    text3 = TextBody("Which one is cuter?\n")

    html1 = HTMLBody("<p>Look at the <em>pretty kitty</em>!</p>\n")
    html2 = HTMLBody("<p>Now look at this <strong>dog</strong>.</p>\n")
    html3 = HTMLBody("<p>Which one is <span style='color: pink'>cuter</span>?</p>\n")

    snuffles = BytesAttachment.from_file("snuffles.jpeg", inline=True)
    rags = BytesAttachment.from_file("rags.jpeg", inline=True)

    mixed_text = text1 & snuffles & text2 & rags & text3
    mixed_html = html1 & snuffles & html2 & rags & html3

    alternative = mixed_text | mixed_html

The ``alternative`` object can then be converted to an e-mail with the same
`~MailItem.compose()` method that mixed objects have.

.. tip::

    In this specific example, we can save on e-mail size by instead creating a
    mixed message containing alternative parts, like so:

    .. code:: python

        mixed = (text1 | html1) & snuffles & (text2 | html2) & rags & (text3 | html3)

.. tip::

    The parts of a :mimetype:`multipart/alternative` message should generally
    be placed in increasing order of preference, which means that the text part
    should be on the left of the ``|`` and the HTML part should be on the
    right.


:mimetype:`multipart/related` Messages
--------------------------------------

Mixing plain text and attachments is all well and good, but when it comes to
HTML, it'd be better if we could reference attachments directly in, say, an
``<img>`` tag's ``src`` attribute.  We can do this in three steps:

1. Assign each attachment's ``content_id`` attribute a unique ID generated with
   `email.utils.make_msgid`.

2. Within the HTML document, refer to a given attachment via the URI
   ``cid:{content_id[1:-1]}`` — that is, "``cid:``" followed by the
   attachment's ``content_id`` with the leading & trailing angle brackets
   stripped off.

3. Combine the HTML body with the attachments using the ``^`` operator to make
   a :mimetype:`multipart/related` object.  The HTML body should be on the left
   end of the operator chain!

Example:

.. code:: python

    from email.utils import make_msgid
    from eletter import BytesAttachment, HTMLBody

    snuffles_cid = make_msgid()
    rags_cid = make_msgid()

    html = HTMLBody(f"""
        <p>Look at the <em>pretty kitty</em>!

        <div class="align: center;">
            <img src="cid:{snuffles_cid[1:-1]}" width="500" height="500"
                 style="border: 1px solid blue;" />
        </div>

        <p>Now look at this <strong>dog</strong>.</p>

        <div class="align: center;">
            <img src="cid:{rags_cid[1:-1]}" width="500" height="200"
                 style="border: 1px solid red;" />
        </div>

        <p>Which one is <span style="color: pink">cuter</span>?</p>
    """)

    snuffles = BytesAttachment.from_file("snuffles.jpeg", inline=True, content_id=snuffles_cid)
    rags = BytesAttachment.from_file("rags.jpeg", inline=True, content_id=rags_cid)

    related = html ^ snuffles ^ rags

.. tip::

    You can remember the fact that :mimetype:`multipart/related` objects use
    ``^`` by association with :mailheader:`Content-ID`\\s, which are enclosed
    in ``<...>``, which look like a sideways ``^``!

Like mixed & alternative objects, ``related`` can then be converted to an
e-mail with the `~MailItem.compose()` method.  If you want, you can even use
``|`` to combine it with a mixed-text message before composing.


Sending E-mails
---------------

Once you've constructed your e-mail and turned it into an
`~email.message.EmailMessage` object, you can send it using Python's `smtplib`,
`imaplib`, or `mailbox` modules or using a compatible third-party library.
Actually doing this is beyond the scope of this tutorial & library, but may I
suggest outgoing_, by yours truly?

.. _outgoing: https://github.com/jwodder/outgoing


Decomposing Emails
------------------

.. versionadded:: 0.5.0

If you have an `email.message.EmailMessage` instance (either composed using
``eletter`` or acquired elsewhere) and you want to convert it into an
``eletter`` structure to make it easier to work with, ``eletter`` provides a
`decompose()` function for doing just that.  Calling `decompose()` on an
`~email.message.EmailMessage` produces an `Eletter` instance that has
attributes for all of the fields accepted by the `~MailItem.compose()` method
plus a `~Eletter.content` field containing an ``eletter`` class.

.. tip::

    If you want to decompose a message that is a plain `email.message.Message`
    instance but not an `~email.message.EmailMessage` instance, you need to
    first convert it into an `~email.message.EmailMessage` before passing it to
    `decompose()` or `decompose_simplify()`.  This can be done with the
    ``message2email()`` function from the mailbits_ package.

    .. _mailbits: https://github.com/jwodder/mailbits

If you want to decompose a message even further, you can call the
`decompose_simple()` function on an `~email.message.EmailMessage` or call the
`~Eletter.simplify()` method of an `Eletter` to produce a `SimpleEletter`
instance.  In place of a ``content`` attribute, a `SimpleEletter` has
`~SimpleEletter.text`, `~SimpleEletter.html`, and `~SimpleEletter.attachments`
attributes giving the original message's text and HTML bodies plus any
attachments.

Once you've decomposed and/or simplified a message, you can examine its parts
and do whatever you want with that information.  You can also manually modify
the `Eletter`/`SimpleEletter`'s various attributes and then call its
`~Eletter.compose()` method (which takes no arguments) to recompose the
instance into a modified `~email.message.EmailMessage`.  Note that the
attributes are of stricter types than what is accepted by the corresponding
arguments to the `compose()` function.  In particular, addresses must be
specified as `Address` instances, not as strings [1]_, the `~Eletter.from_` and
`~Eletter.reply_to` attributes must always be lists, and the values of the
`~Eletter.headers` attribute must always be lists.

.. note::

    Most `~email.message.EmailMessage` instances can be decomposed into
    `Eletter` instances; those that can't use :mailheader:`Content-Type`\s not
    supported by ``eletter``, i.e., :mimetype:`message` types other than
    :mimetype:`message/rfc822` or :mimetype:`multipart` types other than
    :mimetype:`multipart/alternative`, :mimetype:`multipart/mixed`, and
    :mimetype:`multipart/related`.

    On the other hand, considerably fewer `~email.message.EmailMessage`
    instances can be simplified into `SimpleEletter` instances.  Messages that
    cannot be simplified include messages without plain text or HTML parts,
    mixed messages that alternate between plain text & HTML without supplying
    both types for every body part, :mimetype:`multipart/related` messages with
    more than one part, :mimetype:`multipart/mixed` messages containing
    :mimetype:`multipart/alternative` parts that do not consist of a plain text
    body plus an HTML body, and other unusual things.  Trying to simplify such
    messages will produce `~eletter.errors.SimplificationError`\s.

    One category of messages can be simplified, but not without loss of
    information, and so they are not simplified by default: namely,
    :mimetype:`multipart/mixed` messages that alternate between bodies and
    attachments rather than placing all attachments at the end of the message.
    By default, trying to simplify such a message produces a
    `~eletter.errors.MixedContentError`; however, if the ``unmix`` argument to
    `decompose_simple()` or `Eletter.simplify()` is set to `True`, such
    messages will instead be simplified by separating the attachments from the
    bodies, which are then concatenated with no indication of where the
    attachments were located in the text.

.. [1] An e-mail address without a display name can be represented as an
       `Address` object by setting the display name to the empty string:
       ``Address("", "user@domain.nil")``.
