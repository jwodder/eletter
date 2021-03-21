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
| `Documentation <https://eletter.readthedocs.io>`_
| `Issues <https://github.com/jwodder/eletter/issues>`_
| `Changelog <https://github.com/jwodder/eletter/blob/master/CHANGELOG.md>`_

``eletter`` provides functionality for constructing & deconstructing
``email.message.EmailMessage`` instances without having to touch the needlessly
complicated ``EmailMessage`` class itself.  A simple function enables
composition of e-mails with text and/or HTML bodies plus attachments, and
classes are provided for composing more complex multipart e-mails.


Installation
============
``eletter`` requires Python 3.6 or higher.  Just use `pip
<https://pip.pypa.io>`_ for Python 3 (You have pip, right?) to install
``eletter`` and its dependencies::

    python3 -m pip install eletter


Examples
========

Constructing an e-mail with the ``compose()`` function:

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

``msg`` can then be sent like any other ``EmailMessage``, say, by using
outgoing_.

.. _outgoing: https://github.com/jwodder/outgoing

For more complex e-mails, a set of classes is provided.  Here is the equivalent
of the HTML-with-image e-mail with alternative plain text version from the
``email`` `examples page`__ in the Python docs:

__ https://docs.python.org/3/library/email.examples.html

.. code:: python

    from email.utils import make_msgid
    import eletter

    text = eletter.TextBody(
        "Salut!\n"
        "\n"
        "Cela ressemble à un excellent recipie[1] déjeuner.\n"
        "\n"
        "[1] http://www.yummly.com/recipe/Roasted-Asparagus-Epicurious-203718\n"
        "\n"
        "--Pepé\n"
    )

    asparagus_cid = make_msgid()

    html = eletter.HTMLBody(
        "<html>\n"
        "  <head></head>\n"
        "  <body>\n"
        "    <p>Salut!</p>\n"
        "    <p>Cela ressemble à un excellent\n"
        '        <a href="http://www.yummly.com/recipe/Roasted-Asparagus-'
        'Epicurious-203718">\n'
        "            recipie\n"
        "        </a> déjeuner.\n"
        "    </p>\n"
        f'    <img src="cid:{asparagus_cid[1:-1]}" />\n'
        "  </body>\n"
        "</html>\n"
    )

    image = eletter.BytesAttachment.from_file(
        "roasted-asparagus.jpg",
        inline=True,
        content_id=asparagus_cid,
    )

    msg = (text | (html ^ image)).compose(
        subject="Ayons asperges pour le déjeuner",
        from_=eletter.Address("Pepé Le Pew", "pepe@example.com"),
        to=[
            eletter.Address("Penelope Pussycat", "penelope@example.com"),
            eletter.Address("Fabrette Pussycat", "fabrette@example.com"),
        ],
    )
