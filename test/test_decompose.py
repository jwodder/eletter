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
    Eletter,
    EmailAttachment,
    HTMLBody,
    Mixed,
    Related,
    TextAttachment,
    TextBody,
    decompose,
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
    "eml,decomposed",
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
                            content_type="Application/X-FixedRecord",
                            inline=False,
                            content_id="<950120.aaCC@XIson.com>",
                        ),
                        BytesAttachment(
                            content=b"Old MacDonald had a farm\nE I E I O\nAnd on his farm he had some ducks\nE I E I O\nWith a quack quack here,\na quack quack there,\nevery where a quack quack\nE I E I O\n",
                            filename=None,
                            content_type="Application/octet-stream",
                            inline=False,
                            content_id="<950120.aaCB@XIson.com>",
                        ),
                    ],
                    start="<950120.aaCC@XIson.com>",
                ),
            ),
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
        ),
    ],
)
def test_decompose(eml: str, decomposed: Eletter) -> None:
    with (EMAIL_DIR / eml).open("rb") as fp:
        msg = email.message_from_binary_file(fp, policy=policy.default)
    assert isinstance(msg, EmailMessage)
    assert decompose(msg) == decomposed


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
