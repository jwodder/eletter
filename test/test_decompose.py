from datetime import datetime, timedelta, timezone
import email
from email import policy
from email.headerregistry import Address, Group
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import ANY
from mailbits import email2dict
import pytest
from eletter import (
    Alternative,
    BytesAttachment,
    DecompositionError,
    Eletter,
    EmailAttachment,
    HTMLBody,
    Mixed,
    MixedContentError,
    Related,
    SimpleEletter,
    SimplificationError,
    TextAttachment,
    TextBody,
    decompose,
    decompose_simple,
)

ATTACH_DIR = Path(__file__).with_name("data") / "attachments"
EMAIL_DIR = Path(__file__).with_name("data") / "emails"

# <https://github.com/googlefonts/noto-emoji/blob/main/png/32/emoji_u1f408.png>
CAT = (ATTACH_DIR / "cat.png").read_bytes()

# <https://github.com/googlefonts/noto-emoji/blob/main/png/32/emoji_u1f415.png>
DOG = (ATTACH_DIR / "dog.png").read_bytes()

# <https://www.clipartmax.com/middle/
#  m2i8i8G6N4i8G6G6_asparagus-clip-art-free-clip-art-asparagus/>
ASPARAGUS = (ATTACH_DIR / "asparagus.png").read_bytes()


@pytest.mark.parametrize(
    "eml,decomposed,recomposable",
    [
        (
            "addresses.eml",
            Eletter(
                subject="To: Everyone",
                to=[
                    Address("", addr_spec="you@there.net"),
                    Address("Thaddeus Hem", addr_spec="them@hither.yon"),
                ],
                from_=[Address("Mme E.", addr_spec="me@here.com")],
                cc=[
                    Address("Cee Cee Cecil", addr_spec="ccc@seesaws.cc"),
                    Address("", addr_spec="coco@nu.tz"),
                ],
                bcc=[
                    Address("", addr_spec="eletter@depository.nil"),
                    Address("Secret Cabal", addr_spec="illuminati@new.world.order"),
                    Address("", addr_spec="mom@house.home"),
                ],
                reply_to=[Address("", addr_spec="replyee@some.where")],
                sender=Address("", addr_spec="steven.ender@big.senders"),
                content=TextBody(
                    "Meeting tonight!  You know the place.  Bring pizza.\n"
                ),
            ),
            True,
        ),
        (
            "all-bytes.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=BytesAttachment(
                    CAT, "snuffles.png", content_type="image/png", inline=True
                ),
            ),
            True,
        ),
        (
            "alt-mixed.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Alternative(
                    [
                        Mixed(
                            [
                                TextBody("Look at the pretty kitty!\n"),
                                BytesAttachment(
                                    CAT,
                                    "snuffles.png",
                                    content_type="image/png",
                                    inline=True,
                                ),
                                TextBody("Now look at this dog.\n"),
                                BytesAttachment(
                                    DOG,
                                    "rags.png",
                                    content_type="image/png",
                                    inline=True,
                                ),
                                TextBody("Which one is cuter?\n"),
                            ]
                        ),
                        Mixed(
                            [
                                HTMLBody("<p>Look at the <em>pretty kitty</em>!</p>\n"),
                                BytesAttachment(
                                    CAT,
                                    "snuffles.png",
                                    content_type="image/png",
                                    inline=True,
                                ),
                                HTMLBody(
                                    "<p>Now look at this <strong>dog</strong>.</p>\n"
                                ),
                                BytesAttachment(
                                    DOG,
                                    "rags.png",
                                    content_type="image/png",
                                    inline=True,
                                ),
                                HTMLBody(
                                    "<p>Which one is <span style='color: pink'>"
                                    "cuter</span>?</p>\n"
                                ),
                            ]
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "alt.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Alternative(
                    [
                        TextBody("This is displayed on plain text clients.\n"),
                        HTMLBody("<p>This is displayed on graphical clients.<p>\n"),
                    ]
                ),
            ),
            True,
        ),
        (
            "asparagus.eml",
            Eletter(
                subject="Ayons asperges pour le déjeuner",
                from_=[Address("Pepé Le Pew", addr_spec="pepe@example.com")],
                to=[
                    Address("Penelope Pussycat", addr_spec="penelope@example.com"),
                    Address("Fabrette Pussycat", addr_spec="fabrette@example.com"),
                ],
                content=Alternative(
                    [
                        TextBody(
                            "Salut!\n"
                            "\n"
                            "Cela ressemble à un excellent recipie[1] déjeuner.\n"
                            "\n"
                            "[1] http://www.yummly.com/recipe/Roasted-Asparagus"
                            "-Epicurious-203718\n"
                            "\n"
                            "--Pepé\n"
                        ),
                        Related(
                            [
                                HTMLBody(
                                    "<html>\n"
                                    "  <head></head>\n"
                                    "  <body>\n"
                                    "    <p>Salut!</p>\n"
                                    "    <p>Cela ressemble à un excellent\n"
                                    '        <a href="http://www.yummly.com/'
                                    'recipe/Roasted-Asparagus-Epicurious-203718">\n'
                                    "            recipie\n"
                                    "        </a> déjeuner.\n"
                                    "    </p>\n"
                                    '    <img src="cid:161590180540.18149.'
                                    '10562777424476183580@example.nil" />\n'
                                    "  </body>\n"
                                    "</html>\n"
                                ),
                                BytesAttachment(
                                    ASPARAGUS,
                                    "asparagus.png",
                                    content_type="image/png",
                                    inline=True,
                                    content_id=(
                                        "<161590180540.18149."
                                        "10562777424476183580@example.nil>"
                                    ),
                                ),
                            ]
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "attachments.eml",
            Eletter(
                subject="That data you wanted",
                to=[Address("", addr_spec="recipient@domain.com")],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        TextBody(
                            "Here's that data you wanted, sir.  And also the"
                            " ... other thing.\n"
                        ),
                        TextAttachment(
                            "date,item,price\n"
                            "2021-01-01,diamonds,500\n"
                            "2021-02-02,gold,1000\n"
                            "2021-03-03,dirt,1000000\n",
                            "income.csv",
                            content_type="text/csv",
                            inline=False,
                        ),
                        BytesAttachment(
                            CAT, "cat.png", content_type="image/png", inline=False
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "groups.eml",
            Eletter(
                subject=None,
                from_=[Address("Pete", addr_spec="pete@silly.example")],
                to=[
                    Group(
                        "A Group",
                        (
                            Address("Ed Jones", addr_spec="c@a.test"),
                            Address("", addr_spec="joe@where.test"),
                            Address("John", addr_spec="jdoe@one.test"),
                        ),
                    )
                ],
                cc=[Group("Undisclosed recipients", ())],
                date=datetime(
                    1969,
                    2,
                    13,
                    23,
                    32,
                    54,
                    tzinfo=timezone(-timedelta(hours=3, minutes=30)),
                ),
                headers={"message-id": ["<testabcd.1234@silly.example>"]},
                content=TextBody(
                    "Testing.\n\n-- \nTaken from RFC 5322, section A.1.3.\n"
                ),
            ),
            True,
        ),
        (
            "headers.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                date=datetime(
                    2021, 3, 10, 17, 56, 36, tzinfo=timezone(timedelta(hours=-5))
                ),
                headers={
                    "user-agent": ["My Mail Application v.1"],
                    "priority": ["urgent"],
                    "comments": [
                        "I like e-mail.",
                        "But no one ever looks at e-mails' sources, so no one"
                        " will ever know.",
                    ],
                },
                content=TextBody(
                    "This is the body of the e-mail.  Write what you want here!\n"
                ),
            ),
            True,
        ),
        (
            "html.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=HTMLBody(
                    "<p>This is the <strong>body</strong> of the <em>e</em>-mail."
                    "  <span style='color: red;'>Write what you want here!</span></p>\n"
                ),
            ),
            True,
        ),
        (
            "html-plus-alt.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        HTMLBody(
                            "<p>This is the <strong>all-HTML</strong> start of the message.</p>\n"
                        ),
                        Alternative(
                            [
                                TextBody(
                                    "This is the text version of the second part of the message.\n"
                                ),
                                HTMLBody(
                                    "<p>This is the HTML version of the <em>second</em> part of the message.</p>\n"
                                ),
                            ]
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "mdalt.eml",
            Eletter(
                subject="Text vs. Markdown",
                to=[Address("", addr_spec="recipient@domain.com")],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Alternative(
                    [
                        TextBody("This is the plain text version of the message.\n"),
                        Mixed(
                            [
                                TextAttachment(
                                    "This is the *Markdown* version of the message.\n",
                                    filename=None,
                                    content_type="text/markdown",
                                    inline=True,
                                ),
                                BytesAttachment(
                                    DOG,
                                    "dog.png",
                                    content_type="image/png",
                                    inline=False,
                                ),
                            ]
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "mixed.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        TextBody("Look at the pretty kitty!\n"),
                        BytesAttachment(
                            CAT, "snuffles.png", content_type="image/png", inline=True
                        ),
                        TextBody("Now look at this dog.\n"),
                        BytesAttachment(
                            DOG, "rags.png", content_type="image/png", inline=True
                        ),
                        TextBody("Which one is cuter?\n"),
                    ]
                ),
            ),
            True,
        ),
        (
            "mixed-alt.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        Alternative(
                            [
                                TextBody("Look at the pretty kitty!\n"),
                                HTMLBody("<p>Look at the <em>pretty kitty</em>!</p>\n"),
                            ]
                        ),
                        BytesAttachment(
                            CAT, "snuffles.png", content_type="image/png", inline=True
                        ),
                        Alternative(
                            [
                                TextBody("Now look at this dog.\n"),
                                HTMLBody(
                                    "<p>Now look at this <strong>dog</strong>.</p>\n"
                                ),
                            ]
                        ),
                        BytesAttachment(
                            DOG, "rags.png", content_type="image/png", inline=True
                        ),
                        Alternative(
                            [
                                TextBody("Which one is cuter?\n"),
                                HTMLBody(
                                    "<p>Which one is <span style='color: pink'>"
                                    "cuter</span>?</p>\n"
                                ),
                            ]
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "mixed-alt-text.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Alternative(
                    [
                        Mixed(
                            [
                                Alternative(
                                    [
                                        TextBody(
                                            "This is the first part of the less-preferred version.\n"
                                        ),
                                        HTMLBody(
                                            "<p>This is the first part of the <em>less-preferred</em> version.</p>\n"
                                        ),
                                    ]
                                ),
                                Alternative(
                                    [
                                        TextBody(
                                            "This is the second part of the less-preferred version.\n"
                                        ),
                                        HTMLBody(
                                            "<p>This is the second part of the <em>less-preferred</em> version.</p>\n"
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        TextBody("This is the more-preferred version.\n"),
                    ]
                ),
            ),
            True,
        ),
        (
            "mixed-attach.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        BytesAttachment(
                            b"\xFE\xED\xFA\xCE",
                            filename="blob.dat",
                            content_type="application/x-feedface",
                        ),
                        BytesAttachment(
                            b"\xDE\xAD\xBE\xEF",
                            filename="dead.beef",
                            content_type="application/x-deadbeef",
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "mixed-html.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        HTMLBody("<p>Look at the <em>pretty kitty</em>!</p>\n"),
                        BytesAttachment(
                            CAT, "snuffles.png", content_type="image/png", inline=True
                        ),
                        HTMLBody("<p>Now look at this <strong>dog</strong>.</p>\n"),
                        BytesAttachment(
                            DOG, "rags.png", content_type="image/png", inline=True
                        ),
                        HTMLBody(
                            "<p>Which one is <span style='color: pink'>"
                            "cuter</span>?</p>\n"
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "mixed-mdalt.eml",
            Eletter(
                subject="Text plus Text vs. Markdown",
                to=[Address("", addr_spec="recipient@domain.com")],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        TextBody("This is the start of the message.\n"),
                        Alternative(
                            [
                                TextBody(
                                    "This is the plain text version of the message.\n"
                                ),
                                TextAttachment(
                                    "This is the *Markdown* version of the message.\n",
                                    filename=None,
                                    content_type="text/markdown",
                                    inline=True,
                                ),
                            ]
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "mixed-related.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        Related(
                            [
                                HTMLBody(
                                    "<p>Look at the <em>pretty kitty</em>!\n"
                                    '<div class="align: center;">\n'
                                    '    <img src="cid:161652570180.16119.6180689265099732111@example.nil" width="500" height="500"\n'
                                    '         style="border: 1px solid blue;" />\n'
                                    "</div>\n"
                                ),
                                BytesAttachment(
                                    CAT,
                                    "snuffles.png",
                                    content_type="image/png",
                                    inline=True,
                                    content_id="<161652570180.16119.6180689265099732111@example.nil>",
                                ),
                            ]
                        )
                    ]
                ),
            ),
            True,
        ),
        (
            "multi-html-alt.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Alternative(
                    [
                        HTMLBody("<p>Version <strong>1</strong></p>\n"),
                        HTMLBody("<p>Version <strong>2</strong></p>\n"),
                    ]
                ),
            ),
            True,
        ),
        (
            "multi-text-alt.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Alternative(
                    [
                        TextBody("Version 1\n"),
                        TextBody("Version 2\n"),
                    ]
                ),
            ),
            True,
        ),
        (
            "name-in-type.eml",
            Eletter(
                subject="A pretty kitty!",
                from_=[Address("", addr_spec="kitties@r.us")],
                to=[Address("", addr_spec="kitty@lov.er")],
                content=Related(
                    [
                        HTMLBody(
                            "<p>Look at the <em>pretty kitty</em>!\n"
                            '<div class="align: center;">\n'
                            '    <img src="cid:161592191396.26443.11558378911136694407@example.nil" width="500" height="500"\n'
                            '         style="border: 1px solid blue;" />\n'
                            "</div>\n"
                        ),
                        BytesAttachment(
                            CAT,
                            "snuffles.png",
                            content_type='image/png; name="snuffles.png"',
                            inline=False,
                            content_id="<161592191396.26443.11558378911136694407@example.nil>",
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "no-newline-html.eml",
            Eletter(
                subject="HTML without a terminating newline",
                from_=[Address("", addr_spec="sender@domain.com")],
                to=[Address("", addr_spec="recipient@domain.com")],
                content=Mixed(
                    [
                        HTMLBody(
                            "<p>This <em>doesn't</em> end with a <code>newline</code>!</p>"
                        ),
                        HTMLBody(
                            "<p><strong>But</strong> one will be inserted in the middle.</p>"
                        ),
                    ]
                ),
            ),
            False,
        ),
        (
            "no-newline-text.eml",
            Eletter(
                subject="Text without a terminating newline",
                from_=[Address("", addr_spec="sender@domain.com")],
                to=[Address("", addr_spec="recipient@domain.com")],
                content=Mixed(
                    [
                        TextBody("This doesn't end with a newline!"),
                        TextBody("But one will be inserted in the middle."),
                    ]
                ),
            ),
            False,
        ),
        (
            "null-filename.eml",
            Eletter(
                subject="Some electronic mail",
                from_=[Address("", addr_spec="me@here.com")],
                to=[
                    Address("", addr_spec="you@there.net"),
                    Address("Thaddeus Hem", addr_spec="them@hither.yon"),
                ],
                content=Mixed(
                    [
                        TextBody("This is the text of an e-mail.\n"),
                        BytesAttachment(
                            b"\xFE\xED\xFA\xCE",
                            filename=None,
                            content_type="application/x-feedface",
                            inline=False,
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "one-related.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Related(
                    [
                        HTMLBody(
                            "<p>This is <code>multipart/related</code>, but it's not related <em>to</em> anything!</p>\n"
                        )
                    ]
                ),
            ),
            True,
        ),
        (
            "related.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Related(
                    [
                        HTMLBody(
                            "\n"
                            "<p>Look at the <em>pretty kitty</em>!\n"
                            "\n"
                            '<div class="align: center;">\n'
                            '    <img src="cid:161590179505.18130.'
                            '10614940658401659339@example.nil" width="500"'
                            ' height="500"\n'
                            '         style="border: 1px solid blue;" />\n'
                            "</div>\n"
                            "\n"
                            "<p>Now look at this <strong>dog</strong>.</p>\n"
                            "\n"
                            '<div class="align: center;">\n'
                            '    <img src="cid:161590179505.18130.'
                            '674587844016752526@example.nil" width="500"'
                            ' height="200"\n'
                            '         style="border: 1px solid red;" />\n'
                            "</div>\n"
                            "\n"
                            '<p>Which one is <span style="color: pink">cuter</span>?\n'
                        ),
                        BytesAttachment(
                            CAT,
                            "snuffles.png",
                            content_type="image/png",
                            inline=True,
                            content_id="<161590179505.18130.10614940658401659339@example.nil>",
                        ),
                        BytesAttachment(
                            DOG,
                            "rags.png",
                            content_type="image/png",
                            inline=True,
                            content_id="<161590179505.18130.674587844016752526@example.nil>",
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "related-in-mixed.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        HTMLBody(
                            "<p>There's a <strong>pretty kitty</strong> coming up!</p>\n"
                        ),
                        Related(
                            [
                                HTMLBody(
                                    "<p>Look at the <em>pretty kitty</em>!\n"
                                    '<div class="align: center;">\n'
                                    '    <img src="cid:161668323565.35409.10635783721556797858@example.nil" width="500" height="500"\n'
                                    '         style="border: 1px solid blue;" />\n'
                                    "</div>\n"
                                ),
                                BytesAttachment(
                                    CAT,
                                    "snuffles.png",
                                    content_type="image/png",
                                    inline=True,
                                    content_id="<161668323565.35409.10635783721556797858@example.nil>",
                                ),
                            ]
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "related-start.eml",
            Eletter(
                subject=None,
                from_=[],
                to=[],
                headers={"comment": ["Taken from (errata'ed) RFC 2387, section 5.1"]},
                content=Related(
                    [
                        BytesAttachment(
                            content=b"25\n10\n34\n10\n25\n21\n26\n10",
                            filename=None,
                            content_type="application/x-fixedrecord",
                            inline=True,
                            content_id="<950120.aaCC@XIson.com>",
                        ),
                        BytesAttachment(
                            content=b"Old MacDonald had a farm\nE I E I O\nAnd on his farm he had some ducks\nE I E I O\nWith a quack quack here,\na quack quack there,\nevery where a quack quack\nE I E I O\n",
                            filename=None,
                            content_type="application/octet-stream",
                            inline=True,
                            content_id="<950120.aaCB@XIson.com>",
                        ),
                    ],
                    start="<950120.aaCC@XIson.com>",
                ),
            ),
            True,
        ),
        (
            "reverse-alt.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Alternative(
                    [
                        HTMLBody("<p>This is displayed on graphical clients.<p>\n"),
                        TextBody("This is displayed on plain text clients.\n"),
                    ]
                ),
            ),
            True,
        ),
        (
            "text.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=TextBody(
                    "This is the body of the e-mail.  Write what you want here!\n"
                ),
            ),
            True,
        ),
        (
            "text-plus-alt.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        TextBody("This is the all-text start of the message.\n"),
                        Alternative(
                            [
                                TextBody(
                                    "This is the text version of the second part of the message.\n"
                                ),
                                HTMLBody(
                                    "<p>This is the HTML version of the <em>second</em> part of the message.</p>\n"
                                ),
                            ]
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "text-plus-html.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        TextBody("This is the first part.\n"),
                        HTMLBody("<p>This is the <strong>second</strong> part.</p>\n"),
                    ]
                ),
            ),
            True,
        ),
        (
            "twine_release.eml",
            Eletter(
                subject="[Distutils] Twine 3.3.0 released",
                to=[Address("", addr_spec="distutils-sig@python.org")],
                from_=[Address("Brian Rutledge", addr_spec="bhrutledge@gmail.com")],
                date=datetime(
                    2020, 12, 24, 6, 11, 59, tzinfo=timezone(timedelta(hours=-5))
                ),
                headers={
                    "message-id": [
                        "<CAKQj8i4mZQGGtmLe+rHAZNBXNv2Hw6dg5cHtzQL6e71mnZkanA@mail.gmail.com>"
                    ],
                    "x-mailfrom": ["bhrutledge@gmail.com"],
                    "x-mailman-rule-hits": ["member-moderation"],
                    "x-mailman-rule-misses": [
                        "dmarc-mitigation; no-senders; approved; emergency; loop; banned-address"
                    ],
                    "message-id-hash": ["5FC6OKCCVOJZGRYTKAK7CA5RC2XVX24Z"],
                    "x-message-id-hash": ["5FC6OKCCVOJZGRYTKAK7CA5RC2XVX24Z"],
                    "x-mailman-approved-at": ["Mon, 28 Dec 2020 10:06:20 -0500"],
                    "x-mailman-version": ["3.3.3b1"],
                    "precedence": ["list"],
                    "list-id": [
                        '"Python packaging ecosystem SIG'
                        ' (PyPI/pip/twine/wheel/setuptools/distutils/etc)"'
                        " <distutils-sig.python.org>"
                    ],
                    "archived-at": [
                        "<https://mail.python.org/archives/list/distutils-sig@"
                        "python.org/message/5FC6OKCCVOJZGRYTKAK7CA5RC2XVX24Z/>"
                    ],
                    "list-archive": [
                        "<https://mail.python.org/archives/list/distutils-sig@"
                        "python.org/>"
                    ],
                    "list-help": [
                        "<mailto:distutils-sig-request@python.org?subject=help>"
                    ],
                    "list-post": ["<mailto:distutils-sig@python.org>"],
                    "list-subscribe": ["<mailto:distutils-sig-join@python.org>"],
                    "list-unsubscribe": ["<mailto:distutils-sig-leave@python.org>"],
                },
                content=Mixed(
                    [
                        Alternative(
                            [
                                TextBody(
                                    "https://pypi.org/project/twine/3.3.0/\n"
                                    "\n"
                                    "Changelog (now via towncrier):\n"
                                    "https://twine.readthedocs.io/en/latest/"
                                    "changelog.html\n"
                                    "\n"
                                    "Notable improvements include more `twine"
                                    " upload --verbose` output, and a\n"
                                    "`--strict` option for `twine check`.\n"
                                ),
                                HTMLBody(
                                    '<div dir="ltr"><div><a href="https://pypi.org/project/twine/3.3.0/">https://pypi.org/project/twine/3.3.0/</a></div><div><br></div><div>Changelog (now via towncrier): <a href="https://twine.readthedocs.io/en/latest/changelog.html">https://twine.readthedocs.io/en/latest/changelog.html</a></div><div><br></div><div>Notable improvements include more `twine upload --verbose` output, and a `--strict` option for `twine check`.</div></div>\n'
                                ),
                            ]
                        ),
                        TextBody(
                            "--\nDistutils-SIG mailing list -- distutils-sig@python.org\nTo unsubscribe send an email to distutils-sig-leave@python.org\nhttps://mail.python.org/mailman3/lists/distutils-sig.python.org/\nMessage archived at https://mail.python.org/archives/list/distutils-sig@python.org/message/5FC6OKCCVOJZGRYTKAK7CA5RC2XVX24Z/\n"
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "twisted.eml",
            Eletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                content=Mixed(
                    [
                        Alternative(
                            [
                                HTMLBody("<p>This is the <em>first</em> part.</p>\n"),
                                TextBody("This is the first part.\n"),
                            ]
                        ),
                        Alternative(
                            [
                                TextBody("This is the second part.\n"),
                                HTMLBody(
                                    "<p>This is the <strong>second</strong> part.</p>\n"
                                ),
                            ]
                        ),
                    ]
                ),
            ),
            True,
        ),
        (
            "unattached-vcard.eml",
            Eletter(
                subject="Invitation: Create eletter decomposition tests @ Tue Mar 16, 2021 2pm - 3pm (EDT)",
                from_=[Address("", addr_spec="organizer@sender.nil")],
                to=[Address("", addr_spec="recipient@example.nil")],
                reply_to=[Address("", addr_spec="organizer@sender.nil")],
                sender=Address(
                    "Google Calendar", addr_spec="calendar-notification@google.com"
                ),
                date=datetime(2021, 3, 16, 18, 23, 15, tzinfo=timezone.utc),
                headers={"message-id": ["<000000000000b9dd4705bdab7532@google.com>"]},
                content=Mixed(
                    [
                        Alternative(
                            [
                                TextBody(
                                    "You have been invited to the following event.\n"
                                    "\n"
                                    "Title: Create eletter decomposition tests\n"
                                    "When: Tue Mar 16, 2021 2pm – 3pm Eastern Time - New York\n"
                                ),
                                HTMLBody(
                                    "<h2>You have been invited to the following event.</h2><table><tr><th>Title:</th><td>Create eletter decomposition tests</td></tr><tr><th>When:</th><td>Tue Mar 16, 2021 2pm – 3pm Eastern Time - New York</td></tr></table>\n"
                                ),
                                TextAttachment(
                                    "BEGIN:VCALENDAR\n"
                                    "PRODID:-//Google Inc//Google Calendar 70.9054//EN\n"
                                    "VERSION:2.0\n"
                                    "CALSCALE:GREGORIAN\n"
                                    "METHOD:REQUEST\n"
                                    "BEGIN:VEVENT\n"
                                    "DTSTART:20210316T180000Z\n"
                                    "DTEND:20210316T190000Z\n"
                                    "DTSTAMP:20210316T182315Z\n"
                                    "ORGANIZER;CN=organizer@sender.nil:mailto:organizer@sender.nil\n"
                                    "UID:06iihhb86aebbk9q558m4ucnir@google.com\n"
                                    "ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=\n"
                                    " TRUE;CN=recipient@example.nil;X-NUM-GUESTS=0:mailto:recipient@example.nil\n"
                                    "X-MICROSOFT-CDO-OWNERAPPTID:-356041672\n"
                                    "CREATED:20210316T182312Z\n"
                                    "LAST-MODIFIED:20210316T182313Z\n"
                                    "LOCATION:\n"
                                    "SEQUENCE:0\n"
                                    "STATUS:CONFIRMED\n"
                                    "SUMMARY:Create eletter decomposition tests\n"
                                    "TRANSP:OPAQUE\n"
                                    "END:VEVENT\n"
                                    "END:VCALENDAR\n",
                                    filename=None,
                                    content_type='text/calendar; method="REQUEST"',
                                    inline=True,
                                ),
                            ]
                        ),
                        BytesAttachment(
                            b"BEGIN:VCALENDAR\n"
                            b"PRODID:-//Google Inc//Google Calendar 70.9054//EN\n"
                            b"VERSION:2.0\n"
                            b"CALSCALE:GREGORIAN\n"
                            b"METHOD:REQUEST\n"
                            b"BEGIN:VEVENT\n"
                            b"DTSTART:20210316T180000Z\n"
                            b"DTEND:20210316T190000Z\n"
                            b"DTSTAMP:20210316T182315Z\n"
                            b"ORGANIZER;CN=organizer@sender.nil:mailto:organizer@sender.nil\n"
                            b"UID:06iihhb86aebbk9q558m4ucnir@google.com\n"
                            b"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=\n"
                            b" TRUE;CN=recipient@example.nil;X-NUM-GUESTS=0:mailto:recipient@example.nil\n"
                            b"X-MICROSOFT-CDO-OWNERAPPTID:-356041672\n"
                            b"CREATED:20210316T182312Z\n"
                            b"LAST-MODIFIED:20210316T182313Z\n"
                            b"LOCATION:\n"
                            b"SEQUENCE:0\n"
                            b"STATUS:CONFIRMED\n"
                            b"SUMMARY:Create eletter decomposition tests\n"
                            b"TRANSP:OPAQUE\n"
                            b"END:VEVENT\n"
                            b"END:VCALENDAR\n",
                            filename="invite.ics",
                            content_type='application/ics; name="invite.ics"',
                            inline=False,
                        ),
                    ]
                ),
            ),
            True,
        ),
    ],
)
def test_decompose(eml: str, decomposed: Eletter, recomposable: bool) -> None:
    with (EMAIL_DIR / eml).open("rb") as fp:
        msg = email.message_from_binary_file(fp, policy=policy.default)
    assert isinstance(msg, EmailMessage)
    assert decompose(msg) == decomposed
    if recomposable:
        assert decompose(decomposed.compose()) == decomposed


def test_decompose_email_attachment() -> None:
    with (EMAIL_DIR / "has_rfc822.eml").open("rb") as fp:
        msg = email.message_from_binary_file(fp, policy=policy.default)
    assert isinstance(msg, EmailMessage)
    decomposed = decompose(msg)
    assert decomposed == Eletter(
        subject="Fwd: Your confirmed booking",
        from_=[Address("Steven E'Nder", addr_spec="sender@example.nil")],
        to=[Address("", addr_spec="recipient@redacted.nil")],
        date=datetime(2018, 8, 18, 3, 11, 52, tzinfo=timezone.utc),
        headers={
            "message-id": ["<20180818031152.GA7082@example.nil>"],
            "user-agent": ["Mutt/1.5.24 (2015-08-30)"],
        },
        content=Mixed(
            [
                TextBody("Here's that e-mail you wanted:\n\n"),
                EmailAttachment(content=ANY, filename=None, inline=True),
            ]
        ),
    )
    submsg = decomposed.content[1].content  # type: ignore
    assert isinstance(submsg, EmailMessage)
    assert email2dict(submsg) == {
        "unixfrom": None,
        "headers": {
            "delivered-to": [
                "sender@example.nil",
            ],
            "date": datetime(2018, 8, 18, 3, 8, 20, tzinfo=timezone.utc),
            "sender": {
                "display_name": "",
                "address": "hi.booker.com@company.out.foobar.qq",
            },
            "message-id": "<abcdefghijklmnopqrstuv@smtpd.sendgrid.net>",
            "to": [
                {
                    "display_name": "",
                    "address": "sender@example.nil",
                },
            ],
            "from": [
                {
                    "display_name": "Booking Company",
                    "address": "hi.booker.com@company.out.foobar.qq",
                },
            ],
            "subject": "Your confirmed booking",
            "content-type": {
                "content_type": "text/plain",
                "params": {},
            },
        },
        "preamble": None,
        "content": "We have great news! Your booking has been finalized and confirmed. Enjoy your trip, and please let us know if we can be helpful in any way. \n",
        "epilogue": None,
    }


def test_decompose_bad_content_type() -> None:
    with (EMAIL_DIR / "signed.eml").open("rb") as fp:
        msg = email.message_from_binary_file(fp, policy=policy.default)
    assert isinstance(msg, EmailMessage)
    with pytest.raises(DecompositionError) as excinfo:
        decompose(msg)
    assert str(excinfo.value) == "Unsupported Content-Type: multipart/signed"


@pytest.mark.parametrize(
    "eml,decomposed,recomposable",
    [
        (
            "addresses.eml",
            SimpleEletter(
                subject="To: Everyone",
                to=[
                    Address("", addr_spec="you@there.net"),
                    Address("Thaddeus Hem", addr_spec="them@hither.yon"),
                ],
                from_=[Address("Mme E.", addr_spec="me@here.com")],
                cc=[
                    Address("Cee Cee Cecil", addr_spec="ccc@seesaws.cc"),
                    Address("", addr_spec="coco@nu.tz"),
                ],
                bcc=[
                    Address("", addr_spec="eletter@depository.nil"),
                    Address("Secret Cabal", addr_spec="illuminati@new.world.order"),
                    Address("", addr_spec="mom@house.home"),
                ],
                reply_to=[Address("", addr_spec="replyee@some.where")],
                sender=Address("", addr_spec="steven.ender@big.senders"),
                text="Meeting tonight!  You know the place.  Bring pizza.\n",
            ),
            True,
        ),
        (
            "alt.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                text="This is displayed on plain text clients.\n",
                html="<p>This is displayed on graphical clients.<p>\n",
            ),
            True,
        ),
        (
            "attachments.eml",
            SimpleEletter(
                subject="That data you wanted",
                to=[Address("", addr_spec="recipient@domain.com")],
                from_=[Address("", addr_spec="sender@domain.com")],
                text=(
                    "Here's that data you wanted, sir.  And also the"
                    " ... other thing.\n"
                ),
                attachments=[
                    TextAttachment(
                        "date,item,price\n"
                        "2021-01-01,diamonds,500\n"
                        "2021-02-02,gold,1000\n"
                        "2021-03-03,dirt,1000000\n",
                        "income.csv",
                        content_type="text/csv",
                        inline=False,
                    ),
                    BytesAttachment(
                        CAT, "cat.png", content_type="image/png", inline=False
                    ),
                ],
            ),
            True,
        ),
        (
            "groups.eml",
            SimpleEletter(
                subject=None,
                from_=[Address("Pete", addr_spec="pete@silly.example")],
                to=[
                    Group(
                        "A Group",
                        (
                            Address("Ed Jones", addr_spec="c@a.test"),
                            Address("", addr_spec="joe@where.test"),
                            Address("John", addr_spec="jdoe@one.test"),
                        ),
                    )
                ],
                cc=[Group("Undisclosed recipients", ())],
                date=datetime(
                    1969,
                    2,
                    13,
                    23,
                    32,
                    54,
                    tzinfo=timezone(-timedelta(hours=3, minutes=30)),
                ),
                headers={"message-id": ["<testabcd.1234@silly.example>"]},
                text="Testing.\n\n-- \nTaken from RFC 5322, section A.1.3.\n",
            ),
            True,
        ),
        (
            "headers.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                date=datetime(
                    2021, 3, 10, 17, 56, 36, tzinfo=timezone(timedelta(hours=-5))
                ),
                headers={
                    "user-agent": ["My Mail Application v.1"],
                    "priority": ["urgent"],
                    "comments": [
                        "I like e-mail.",
                        "But no one ever looks at e-mails' sources, so no one"
                        " will ever know.",
                    ],
                },
                text="This is the body of the e-mail.  Write what you want here!\n",
            ),
            True,
        ),
        (
            "html.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                html=(
                    "<p>This is the <strong>body</strong> of the <em>e</em>-mail."
                    "  <span style='color: red;'>Write what you want here!</span></p>\n"
                ),
            ),
            True,
        ),
        (
            "no-newline-html.eml",
            SimpleEletter(
                subject="HTML without a terminating newline",
                from_=[Address("", addr_spec="sender@domain.com")],
                to=[Address("", addr_spec="recipient@domain.com")],
                html=(
                    "<p>This <em>doesn't</em> end with a <code>newline</code>!</p>\n"
                    "<p><strong>But</strong> one will be inserted in the middle.</p>"
                ),
            ),
            False,
        ),
        (
            "no-newline-text.eml",
            SimpleEletter(
                subject="Text without a terminating newline",
                from_=[Address("", addr_spec="sender@domain.com")],
                to=[Address("", addr_spec="recipient@domain.com")],
                text=(
                    "This doesn't end with a newline!\n"
                    "But one will be inserted in the middle."
                ),
            ),
            False,
        ),
        (
            "null-filename.eml",
            SimpleEletter(
                subject="Some electronic mail",
                from_=[Address("", addr_spec="me@here.com")],
                to=[
                    Address("", addr_spec="you@there.net"),
                    Address("Thaddeus Hem", addr_spec="them@hither.yon"),
                ],
                text="This is the text of an e-mail.\n",
                attachments=[
                    BytesAttachment(
                        b"\xFE\xED\xFA\xCE",
                        filename=None,
                        content_type="application/x-feedface",
                        inline=False,
                    ),
                ],
            ),
            True,
        ),
        (
            "one-related.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                html="<p>This is <code>multipart/related</code>, but it's not related <em>to</em> anything!</p>\n",
            ),
            True,
        ),
        (
            "reverse-alt.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                text="This is displayed on plain text clients.\n",
                html="<p>This is displayed on graphical clients.<p>\n",
            ),
            True,
        ),
        (
            "text.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                text="This is the body of the e-mail.  Write what you want here!\n",
            ),
            True,
        ),
        (
            "twisted.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                text=("This is the first part.\n" "This is the second part.\n"),
                html=(
                    "<p>This is the <em>first</em> part.</p>\n"
                    "<p>This is the <strong>second</strong> part.</p>\n"
                ),
            ),
            True,
        ),
    ],
)
@pytest.mark.parametrize("unmix", [False, True])
def test_simple_decompose(
    eml: str, decomposed: SimpleEletter, recomposable: bool, unmix: bool
) -> None:
    with (EMAIL_DIR / eml).open("rb") as fp:
        msg = email.message_from_binary_file(fp, policy=policy.default)
    assert isinstance(msg, EmailMessage)
    assert decompose_simple(msg, unmix=unmix) == decomposed
    if recomposable:
        assert decompose_simple(decomposed.compose()) == decomposed


def test_simple_decompose_email_attachment() -> None:
    with (EMAIL_DIR / "has_rfc822.eml").open("rb") as fp:
        msg = email.message_from_binary_file(fp, policy=policy.default)
    assert isinstance(msg, EmailMessage)
    decomposed = decompose_simple(msg)
    assert decomposed == SimpleEletter(
        subject="Fwd: Your confirmed booking",
        from_=[Address("Steven E'Nder", addr_spec="sender@example.nil")],
        to=[Address("", addr_spec="recipient@redacted.nil")],
        date=datetime(2018, 8, 18, 3, 11, 52, tzinfo=timezone.utc),
        headers={
            "message-id": ["<20180818031152.GA7082@example.nil>"],
            "user-agent": ["Mutt/1.5.24 (2015-08-30)"],
        },
        text="Here's that e-mail you wanted:\n\n",
        attachments=[EmailAttachment(content=ANY, filename=None, inline=True)],
    )
    submsg = decomposed.attachments[0].content  # type: ignore
    assert isinstance(submsg, EmailMessage)
    assert email2dict(submsg) == {
        "unixfrom": None,
        "headers": {
            "delivered-to": [
                "sender@example.nil",
            ],
            "date": datetime(2018, 8, 18, 3, 8, 20, tzinfo=timezone.utc),
            "sender": {
                "display_name": "",
                "address": "hi.booker.com@company.out.foobar.qq",
            },
            "message-id": "<abcdefghijklmnopqrstuv@smtpd.sendgrid.net>",
            "to": [
                {
                    "display_name": "",
                    "address": "sender@example.nil",
                },
            ],
            "from": [
                {
                    "display_name": "Booking Company",
                    "address": "hi.booker.com@company.out.foobar.qq",
                },
            ],
            "subject": "Your confirmed booking",
            "content-type": {
                "content_type": "text/plain",
                "params": {},
            },
        },
        "preamble": None,
        "content": "We have great news! Your booking has been finalized and confirmed. Enjoy your trip, and please let us know if we can be helpful in any way. \n",
        "epilogue": None,
    }


@pytest.mark.parametrize(
    "eml,errmsg",
    [
        ("all-bytes.eml", "Body is an attachment"),
        ("asparagus.eml", "Cannot simplify multipart/related"),
        ("html-plus-alt.eml", "Text + HTML alternative follows HTML-only body"),
        ("mdalt.eml", "Alternative part contains neither text/plain nor text/html"),
        (
            "mixed-alt-text.eml",
            "Alternative part contains both text/plain and text/html",
        ),
        ("mixed-attach.eml", "No text or HTML bodies in message"),
        (
            "mixed-mdalt.eml",
            "multipart/alternative inside multipart/mixed is not a text/plain part plus a text/html part",
        ),
        ("mixed-related.eml", "Cannot simplify multipart/related"),
        ("multi-html-alt.eml", "Multiple text/html parts in multipart/alternative"),
        ("multi-text-alt.eml", "Multiple text/plain parts in multipart/alternative"),
        ("name-in-type.eml", "Cannot simplify multipart/related"),
        ("related.eml", "Cannot simplify multipart/related"),
        ("related-in-mixed.eml", "Cannot simplify multipart/related"),
        ("related-start.eml", "Cannot simplify multipart/related"),
        ("text-plus-alt.eml", "Text + HTML alternative follows text-only body"),
        ("text-plus-html.eml", "No matching text alternative for HTML part"),
        ("twine_release.eml", "No matching HTML alternative for text part"),
        (
            "unattached-vcard.eml",
            "multipart/alternative inside multipart/mixed is not a text/plain part plus a text/html part",
        ),
    ],
)
def test_simple_error(eml: str, errmsg: str) -> None:
    with (EMAIL_DIR / eml).open("rb") as fp:
        msg = email.message_from_binary_file(fp, policy=policy.default)
    assert isinstance(msg, EmailMessage)
    with pytest.raises(SimplificationError) as excinfo:
        decompose_simple(msg)
    assert str(excinfo.value) == errmsg


@pytest.mark.parametrize(
    "eml",
    ["alt-mixed.eml", "mixed.eml", "mixed-alt.eml", "mixed-html.eml"],
)
def test_simple_mixed_content_error(eml: str) -> None:
    with (EMAIL_DIR / eml).open("rb") as fp:
        msg = email.message_from_binary_file(fp, policy=policy.default)
    assert isinstance(msg, EmailMessage)
    with pytest.raises(MixedContentError) as excinfo:
        decompose_simple(msg)
    assert str(excinfo.value) == "Message intersperses attachments with text"


@pytest.mark.parametrize(
    "eml,decomposed",
    [
        (
            "alt-mixed.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                text=(
                    "Look at the pretty kitty!\n"
                    "Now look at this dog.\n"
                    "Which one is cuter?\n"
                ),
                html=(
                    "<p>Look at the <em>pretty kitty</em>!</p>\n"
                    "<p>Now look at this <strong>dog</strong>.</p>\n"
                    "<p>Which one is <span style='color: pink'>"
                    "cuter</span>?</p>\n"
                ),
                attachments=[
                    BytesAttachment(
                        CAT,
                        "snuffles.png",
                        content_type="image/png",
                        inline=True,
                    ),
                    BytesAttachment(
                        DOG,
                        "rags.png",
                        content_type="image/png",
                        inline=True,
                    ),
                ],
            ),
        ),
        (
            "mixed.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                text=(
                    "Look at the pretty kitty!\n"
                    "Now look at this dog.\n"
                    "Which one is cuter?\n"
                ),
                attachments=[
                    BytesAttachment(
                        CAT, "snuffles.png", content_type="image/png", inline=True
                    ),
                    BytesAttachment(
                        DOG, "rags.png", content_type="image/png", inline=True
                    ),
                ],
            ),
        ),
        (
            "mixed-alt.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                text=(
                    "Look at the pretty kitty!\n"
                    "Now look at this dog.\n"
                    "Which one is cuter?\n"
                ),
                html=(
                    "<p>Look at the <em>pretty kitty</em>!</p>\n"
                    "<p>Now look at this <strong>dog</strong>.</p>\n"
                    "<p>Which one is <span style='color: pink'>"
                    "cuter</span>?</p>\n"
                ),
                attachments=[
                    BytesAttachment(
                        CAT, "snuffles.png", content_type="image/png", inline=True
                    ),
                    BytesAttachment(
                        DOG, "rags.png", content_type="image/png", inline=True
                    ),
                ],
            ),
        ),
        (
            "mixed-html.eml",
            SimpleEletter(
                subject="The subject of the e-mail",
                to=[
                    Address("", addr_spec="recipient@domain.com"),
                    Address("", addr_spec="another.recipient@example.nil"),
                ],
                from_=[Address("", addr_spec="sender@domain.com")],
                html=(
                    "<p>Look at the <em>pretty kitty</em>!</p>\n"
                    "<p>Now look at this <strong>dog</strong>.</p>\n"
                    "<p>Which one is <span style='color: pink'>"
                    "cuter</span>?</p>\n"
                ),
                attachments=[
                    BytesAttachment(
                        CAT, "snuffles.png", content_type="image/png", inline=True
                    ),
                    BytesAttachment(
                        DOG, "rags.png", content_type="image/png", inline=True
                    ),
                ],
            ),
        ),
    ],
)
def test_simple_decompose_unmix(eml: str, decomposed: SimpleEletter) -> None:
    with (EMAIL_DIR / eml).open("rb") as fp:
        msg = email.message_from_binary_file(fp, policy=policy.default)
    assert isinstance(msg, EmailMessage)
    assert decompose_simple(msg, unmix=True) == decomposed
