from datetime import datetime, timedelta, timezone
from email.utils import make_msgid
from typing import Any, Iterable, Type, Union
from email2dict import email2dict
import pytest
from eletter import (
    Address,
    Alternative,
    BytesAttachment,
    Group,
    HTMLBody,
    MailItem,
    Mixed,
    Multipart,
    Related,
    TextAttachment,
    TextBody,
)
from eletter.util import AddressOrGroup


def test_text_body() -> None:
    msg = TextBody("This is the text of an e-mail.").compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
    )
    assert email2dict(msg) == {
        "unixfrom": None,
        "headers": {
            "subject": "Some electronic mail",
            "from": [
                {
                    "display_name": "",
                    "address": "me@here.com",
                }
            ],
            "to": [
                {
                    "display_name": "",
                    "address": "you@there.net",
                },
                {
                    "display_name": "Thaddeus Hem",
                    "address": "them@hither.yon",
                },
            ],
            "content-type": {
                "content_type": "text/plain",
                "params": {},
            },
        },
        "preamble": None,
        "content": "This is the text of an e-mail.\n",
        "epilogue": None,
    }


def test_html_body() -> None:
    msg = HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>").compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
    )
    assert email2dict(msg) == {
        "unixfrom": None,
        "headers": {
            "subject": "Some electronic mail",
            "from": [
                {
                    "display_name": "",
                    "address": "me@here.com",
                }
            ],
            "to": [
                {
                    "display_name": "",
                    "address": "you@there.net",
                },
                {
                    "display_name": "Thaddeus Hem",
                    "address": "them@hither.yon",
                },
            ],
            "content-type": {
                "content_type": "text/html",
                "params": {},
            },
        },
        "preamble": None,
        "content": "<p>This is the <i>text</i> of an <b>e</b>-mail.<p>\n",
        "epilogue": None,
    }


def test_text_alt_html() -> None:
    t = TextBody("This is the text of an e-mail.")
    h = HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>")
    msg = (t | h).compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
    )
    assert email2dict(msg) == {
        "unixfrom": None,
        "headers": {
            "subject": "Some electronic mail",
            "from": [
                {
                    "display_name": "",
                    "address": "me@here.com",
                }
            ],
            "to": [
                {
                    "display_name": "",
                    "address": "you@there.net",
                },
                {
                    "display_name": "Thaddeus Hem",
                    "address": "them@hither.yon",
                },
            ],
            "content-type": {
                "content_type": "multipart/alternative",
                "params": {},
            },
        },
        "preamble": None,
        "content": [
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/plain",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": "This is the text of an e-mail.\n",
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/html",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": "<p>This is the <i>text</i> of an <b>e</b>-mail.<p>\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_html_alt_text() -> None:
    h = HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>")
    t = TextBody("This is the text of an e-mail.")
    msg = (h | t).compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
    )
    assert email2dict(msg) == {
        "unixfrom": None,
        "headers": {
            "subject": "Some electronic mail",
            "from": [
                {
                    "display_name": "",
                    "address": "me@here.com",
                }
            ],
            "to": [
                {
                    "display_name": "",
                    "address": "you@there.net",
                },
                {
                    "display_name": "Thaddeus Hem",
                    "address": "them@hither.yon",
                },
            ],
            "content-type": {
                "content_type": "multipart/alternative",
                "params": {},
            },
        },
        "preamble": None,
        "content": [
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/html",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": "<p>This is the <i>text</i> of an <b>e</b>-mail.<p>\n",
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/plain",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": "This is the text of an e-mail.\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_alt() -> None:
    t = TextBody("This is the text of an e-mail.")
    h = HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>")
    alt = t | h
    assert isinstance(alt, Alternative)
    assert alt == Alternative([t, h])


def test_or_alt() -> None:
    t1 = TextBody("Part 1")
    t2 = TextBody("Part 2")
    t3 = TextBody("Part 3")
    t4 = TextBody("Part 4")
    alt1 = t1 | t2
    alt2 = t3 | t4
    alt = alt1 | alt2
    assert alt == Alternative([t1, t2, t3, t4])


def test_alt_or_eq_body() -> None:
    t1 = TextBody("Part 1")
    t2 = TextBody("Part 2")
    t3 = TextBody("Part 3")
    alt = t1 | t2
    x = alt
    x |= t3
    assert x is alt
    assert x == Alternative([t1, t2, t3])
    assert t3 == TextBody("Part 3")


def test_alt_or_eq_alt() -> None:
    t1 = TextBody("Part 1")
    t2 = TextBody("Part 2")
    t3 = TextBody("Part 3")
    t4 = TextBody("Part 4")
    alt1 = t1 | t2
    alt2 = t3 | t4
    x = alt1
    x |= alt2
    assert x is alt1
    assert x == Alternative([t1, t2, t3, t4])
    assert alt2 == Alternative([t3, t4])


def test_body_or_eq() -> None:
    t = TextBody("This is the text of an e-mail.")
    h = HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>")
    x: Any = t
    x |= h
    assert x is not t
    assert isinstance(x, Alternative)
    assert x == Alternative([t, h])
    assert t == TextBody("This is the text of an e-mail.")


def test_compose_empty_alt() -> None:
    with pytest.raises(ValueError) as excinfo:
        Alternative([]).compose(
            from_="me@here.com",
            to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
            subject="Some electronic mail",
        )
    assert str(excinfo.value) == "Cannot compose empty Alternative"


@pytest.mark.parametrize(
    "mi",
    [
        TextBody("This is the text of an e-mail."),
        HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>"),
        Alternative(
            [
                TextBody("This is the text of an e-mail."),
                HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>"),
            ]
        ),
        Mixed(
            [
                TextBody("This is the text of an e-mail."),
                TextAttachment(
                    "this,text,attachment", "attachment.csv", content_type="text/csv"
                ),
            ]
        ),
        Related(
            [
                TextBody("This is the text of an e-mail."),
                TextAttachment(
                    "this,text,attachment", "attachment.csv", content_type="text/csv"
                ),
            ]
        ),
        TextAttachment("This is an attachment.", filename="foo.txt"),
        BytesAttachment(b"This is an attachment.\n", filename="foo.blob"),
    ],
)
@pytest.mark.parametrize(
    "from_input,from_output",
    [
        (
            Address("Mme E.", "me@here.com"),
            [{"display_name": "Mme E.", "address": "me@here.com"}],
        ),
        (
            [Address("Mme E.", "me@here.com"), "also-me@hence.thither"],
            [
                {"display_name": "Mme E.", "address": "me@here.com"},
                {"display_name": "", "address": "also-me@hence.thither"},
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    "to_input,to_output",
    [
        (
            ["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
            [
                {"display_name": "", "address": "you@there.net"},
                {"display_name": "Thaddeus Hem", "address": "them@hither.yon"},
            ],
        ),
        (
            [
                Group(
                    "friends",
                    ["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
                ),
                "those@ovar.thar",
            ],
            [
                {
                    "group": "friends",
                    "addresses": [
                        {"display_name": "", "address": "you@there.net"},
                        {"display_name": "Thaddeus Hem", "address": "them@hither.yon"},
                    ],
                },
                {"display_name": "", "address": "those@ovar.thar"},
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    "reply_to_input,reply_to_output",
    [
        (
            "replyee@some.where",
            [{"display_name": "", "address": "replyee@some.where"}],
        ),
        (
            [
                "replyee@some.where",
                Address("Response Handler", "r.handler@answers.4.you"),
            ],
            [
                {"display_name": "", "address": "replyee@some.where"},
                {
                    "display_name": "Response Handler",
                    "address": "r.handler@answers.4.you",
                },
            ],
        ),
    ],
)
def test_mailitem_compose(
    mi: MailItem,
    from_input: Union[AddressOrGroup, Iterable[AddressOrGroup]],
    from_output: Any,
    to_input: Iterable[AddressOrGroup],
    to_output: Any,
    reply_to_input: Union[AddressOrGroup, Iterable[AddressOrGroup]],
    reply_to_output: Any,
) -> None:
    when = datetime(2021, 3, 8, 18, 14, 29, tzinfo=timezone(timedelta(hours=-5)))
    msg = mi.compose(
        subject="To: Everyone",
        from_=from_input,
        to=to_input,
        cc=[Address("Cee Cee Cecil", "ccc@seesaws.cc"), "coco@nu.tz"],
        bcc=[
            "eletter@depository.nil",
            Address("Secret Cabal", "illuminati@new.world.order"),
            "mom@house.home",
        ],
        reply_to=reply_to_input,
        sender="steven.ender@big.senders",
        date=when,
        headers={
            "User-Agent": "eletter",
            "Received": [
                "From mx.example.com",
                "From mail.sender.nil",
            ],
        },
    )
    headers = email2dict(msg)["headers"]
    headers.pop("content-type")
    headers.pop("content-disposition", None)
    assert headers == {
        "subject": "To: Everyone",
        "from": from_output,
        "to": to_output,
        "cc": [
            {
                "display_name": "Cee Cee Cecil",
                "address": "ccc@seesaws.cc",
            },
            {
                "display_name": "",
                "address": "coco@nu.tz",
            },
        ],
        "bcc": [
            {
                "display_name": "",
                "address": "eletter@depository.nil",
            },
            {
                "display_name": "Secret Cabal",
                "address": "illuminati@new.world.order",
            },
            {
                "display_name": "",
                "address": "mom@house.home",
            },
        ],
        "reply-to": reply_to_output,
        "sender": {
            "display_name": "",
            "address": "steven.ender@big.senders",
        },
        "date": when,
        "user-agent": ["eletter"],
        "received": [
            "From mx.example.com",
            "From mail.sender.nil",
        ],
    }


def test_text_and_attachment() -> None:
    t = TextBody("This is the text of an e-mail.")
    a = TextAttachment(
        "this,text,attachment", "attachment.csv", content_type="text/csv"
    )
    msg = (t & a).compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
    )
    assert email2dict(msg) == {
        "unixfrom": None,
        "headers": {
            "subject": "Some electronic mail",
            "from": [
                {
                    "display_name": "",
                    "address": "me@here.com",
                }
            ],
            "to": [
                {
                    "display_name": "",
                    "address": "you@there.net",
                },
                {
                    "display_name": "Thaddeus Hem",
                    "address": "them@hither.yon",
                },
            ],
            "content-type": {
                "content_type": "multipart/mixed",
                "params": {},
            },
        },
        "preamble": None,
        "content": [
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/plain",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": "This is the text of an e-mail.\n",
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/csv",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "attachment.csv"},
                    },
                },
                "preamble": None,
                "content": "this,text,attachment\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_mixed() -> None:
    t = TextBody("This is the text of an e-mail.")
    a = TextAttachment(
        "this,text,attachment", "attachment.csv", content_type="text/csv"
    )
    mixed = t & a
    assert isinstance(mixed, Mixed)
    assert mixed == Mixed([t, a])


def test_and_mixed() -> None:
    t1 = TextBody("Part 1")
    t2 = TextBody("Part 2")
    t3 = TextBody("Part 3")
    t4 = TextBody("Part 4")
    mixed1 = t1 & t2
    mixed2 = t3 & t4
    mixed = mixed1 & mixed2
    assert mixed == Mixed([t1, t2, t3, t4])


def test_mixed_and_eq_body() -> None:
    t1 = TextBody("Part 1")
    t2 = TextBody("Part 2")
    t3 = TextBody("Part 3")
    mixed = t1 & t2
    x = mixed
    x &= t3
    assert x is mixed
    assert x == Mixed([t1, t2, t3])
    assert t3 == TextBody("Part 3")


def test_mixed_and_eq_mixed() -> None:
    t1 = TextBody("Part 1")
    t2 = TextBody("Part 2")
    t3 = TextBody("Part 3")
    t4 = TextBody("Part 4")
    mixed1 = t1 & t2
    mixed2 = t3 & t4
    x = mixed1
    x &= mixed2
    assert x is mixed1
    assert x == Mixed([t1, t2, t3, t4])
    assert mixed2 == Mixed([t3, t4])


def test_body_and_eq() -> None:
    t = TextBody("This is the text of an e-mail.")
    a = TextAttachment(
        "this,text,attachment", "attachment.csv", content_type="text/csv"
    )
    x: Any = t
    x &= a
    assert x is not t
    assert isinstance(x, Mixed)
    assert x == Mixed([t, a])
    assert t == TextBody("This is the text of an e-mail.")


def test_compose_empty_mixed() -> None:
    with pytest.raises(ValueError) as excinfo:
        Mixed([]).compose(
            from_="me@here.com",
            to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
            subject="Some electronic mail",
        )
    assert str(excinfo.value) == "Cannot compose empty Mixed"


def test_text_alt_html_and_attachment() -> None:
    t = TextBody("This is the text of an e-mail.")
    h = HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>")
    a = TextAttachment(
        "this,text,attachment", "attachment.csv", content_type="text/csv"
    )
    msg = ((t | h) & a).compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
    )
    assert email2dict(msg) == {
        "unixfrom": None,
        "headers": {
            "subject": "Some electronic mail",
            "from": [
                {
                    "display_name": "",
                    "address": "me@here.com",
                }
            ],
            "to": [
                {
                    "display_name": "",
                    "address": "you@there.net",
                },
                {
                    "display_name": "Thaddeus Hem",
                    "address": "them@hither.yon",
                },
            ],
            "content-type": {
                "content_type": "multipart/mixed",
                "params": {},
            },
        },
        "preamble": None,
        "content": [
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "multipart/alternative",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": [
                    {
                        "unixfrom": None,
                        "headers": {
                            "content-type": {
                                "content_type": "text/plain",
                                "params": {},
                            },
                        },
                        "preamble": None,
                        "content": "This is the text of an e-mail.\n",
                        "epilogue": None,
                    },
                    {
                        "unixfrom": None,
                        "headers": {
                            "content-type": {
                                "content_type": "text/html",
                                "params": {},
                            },
                        },
                        "preamble": None,
                        "content": (
                            "<p>This is the <i>text</i> of an <b>e</b>-mail.<p>\n"
                        ),
                        "epilogue": None,
                    },
                ],
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/csv",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "attachment.csv"},
                    },
                },
                "preamble": None,
                "content": "this,text,attachment\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_related() -> None:
    t = TextBody("This is the text of an e-mail.")
    h = HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>")
    rel = t ^ h
    assert isinstance(rel, Related)
    assert rel == Related([t, h])


def test_xor_related() -> None:
    t1 = TextBody("Part 1")
    t2 = TextBody("Part 2")
    t3 = TextBody("Part 3")
    t4 = TextBody("Part 4")
    rel1 = t1 ^ t2
    rel2 = t3 ^ t4
    rel = rel1 ^ rel2
    assert rel == Related([t1, t2, t3, t4])


def test_related_xor_eq_body() -> None:
    t1 = TextBody("Part 1")
    t2 = TextBody("Part 2")
    t3 = TextBody("Part 3")
    rel = t1 ^ t2
    x = rel
    x ^= t3
    assert x is rel
    assert x == Related([t1, t2, t3])
    assert t3 == TextBody("Part 3")


def test_related_xor_eq_related() -> None:
    t1 = TextBody("Part 1")
    t2 = TextBody("Part 2")
    t3 = TextBody("Part 3")
    t4 = TextBody("Part 4")
    rel1 = t1 ^ t2
    rel2 = t3 ^ t4
    x = rel1
    x ^= rel2
    assert x is rel1
    assert x == Related([t1, t2, t3, t4])
    assert rel2 == Related([t3, t4])


def test_body_xor_eq() -> None:
    t = TextBody("This is the text of an e-mail.")
    h = HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>")
    x: Any = t
    x ^= h
    assert x is not t
    assert isinstance(x, Related)
    assert x == Related([t, h])
    assert t == TextBody("This is the text of an e-mail.")


def test_compose_empty_related() -> None:
    with pytest.raises(ValueError) as excinfo:
        Related([]).compose(
            from_="me@here.com",
            to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
            subject="Some electronic mail",
        )
    assert str(excinfo.value) == "Cannot compose empty Related"


def test_text_alt_html_related() -> None:
    # Converted from <https://docs.python.org/3/library/email.examples.html>
    TEXT = (
        "Salut!\n"
        "\n"
        "Cela ressemble à un excellent recipie[1] déjeuner.\n"
        "\n"
        "[1] http://www.yummly.com/recipe/Roasted-Asparagus-Epicurious-203718\n"
        "\n"
        "--Pepé\n"
    )
    t = TextBody(TEXT)
    asparagus_cid = make_msgid()
    HTML = (
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
    h = HTMLBody(HTML)
    IMG = b"\1\2\3\4\5"
    img = BytesAttachment(
        IMG,
        "asparagus.png",
        content_type="image/png",
        inline=True,
        content_id=asparagus_cid,
    )
    msg = (t | (h ^ img)).compose(
        subject="Ayons asperges pour le déjeuner",
        from_=Address("Pepé Le Pew", "pepe@example.com"),
        to=(
            Address("Penelope Pussycat", "penelope@example.com"),
            Address("Fabrette Pussycat", "fabrette@example.com"),
        ),
    )
    assert email2dict(msg) == {
        "unixfrom": None,
        "headers": {
            "subject": "Ayons asperges pour le déjeuner",
            "from": [
                {
                    "display_name": "Pepé Le Pew",
                    "address": "pepe@example.com",
                },
            ],
            "to": [
                {
                    "display_name": "Penelope Pussycat",
                    "address": "penelope@example.com",
                },
                {
                    "display_name": "Fabrette Pussycat",
                    "address": "fabrette@example.com",
                },
            ],
            "content-type": {
                "content_type": "multipart/alternative",
                "params": {},
            },
        },
        "preamble": None,
        "content": [
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/plain",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": TEXT,
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "multipart/related",
                        "params": {"type": "text/html"},
                    },
                },
                "preamble": None,
                "content": [
                    {
                        "unixfrom": None,
                        "headers": {
                            "content-type": {
                                "content_type": "text/html",
                                "params": {},
                            },
                        },
                        "preamble": None,
                        "content": HTML,
                        "epilogue": None,
                    },
                    {
                        "unixfrom": None,
                        "headers": {
                            "content-type": {
                                "content_type": "image/png",
                                "params": {},
                            },
                            "content-disposition": {
                                "disposition": "inline",
                                "params": {"filename": "asparagus.png"},
                            },
                            "content-id": [asparagus_cid],
                        },
                        "preamble": None,
                        "content": IMG,
                        "epilogue": None,
                    },
                ],
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_img_html_related_start() -> None:
    asparagus_cid = make_msgid()
    html_cid = make_msgid()
    HTML = (
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
    h = HTMLBody(HTML, content_id=html_cid)
    IMG = b"\1\2\3\4\5"
    img = BytesAttachment(
        IMG,
        "asparagus.png",
        content_type="image/png",
        inline=True,
        content_id=asparagus_cid,
    )
    rel = img ^ h
    rel.start = html_cid
    msg = rel.compose(
        subject="Ayons asperges pour le déjeuner",
        from_=Address("Pepé Le Pew", "pepe@example.com"),
        to=(
            Address("Penelope Pussycat", "penelope@example.com"),
            Address("Fabrette Pussycat", "fabrette@example.com"),
        ),
    )
    assert email2dict(msg) == {
        "unixfrom": None,
        "headers": {
            "subject": "Ayons asperges pour le déjeuner",
            "from": [
                {
                    "display_name": "Pepé Le Pew",
                    "address": "pepe@example.com",
                },
            ],
            "to": [
                {
                    "display_name": "Penelope Pussycat",
                    "address": "penelope@example.com",
                },
                {
                    "display_name": "Fabrette Pussycat",
                    "address": "fabrette@example.com",
                },
            ],
            "content-type": {
                "content_type": "multipart/related",
                "params": {"type": "text/html", "start": html_cid},
            },
        },
        "preamble": None,
        "content": [
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "image/png",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "inline",
                        "params": {"filename": "asparagus.png"},
                    },
                    "content-id": [asparagus_cid],
                },
                "preamble": None,
                "content": IMG,
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/html",
                        "params": {},
                    },
                    "content-id": [html_cid],
                },
                "preamble": None,
                "content": HTML,
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_multipart_content_ids() -> None:
    img_cid = make_msgid()
    img = BytesAttachment(
        b"\1\2\3\4\5", filename="blob.png", content_type="image/png", content_id=img_cid
    )
    text = TextBody("Here is an image:\n")
    HTML = f'<p>Here is an image:</p><img src="cid:{img_cid[1:-1]}"/>\n'
    html = HTMLBody(HTML)
    mixed = text & img
    mixed_cid = make_msgid()
    mixed.content_id = mixed_cid
    related = html ^ img
    related_cid = make_msgid()
    related.content_id = related_cid
    alt = mixed | related
    alt_cid = make_msgid()
    alt.content_id = alt_cid
    msg = alt.compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
    )
    assert email2dict(msg) == {
        "unixfrom": None,
        "headers": {
            "subject": "Some electronic mail",
            "from": [
                {
                    "display_name": "",
                    "address": "me@here.com",
                }
            ],
            "to": [
                {
                    "display_name": "",
                    "address": "you@there.net",
                },
                {
                    "display_name": "Thaddeus Hem",
                    "address": "them@hither.yon",
                },
            ],
            "content-type": {
                "content_type": "multipart/alternative",
                "params": {},
            },
            "content-id": [alt_cid],
        },
        "preamble": None,
        "content": [
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "multipart/mixed",
                        "params": {},
                    },
                    "content-id": [mixed_cid],
                },
                "preamble": None,
                "content": [
                    {
                        "unixfrom": None,
                        "headers": {
                            "content-type": {
                                "content_type": "text/plain",
                                "params": {},
                            },
                        },
                        "preamble": None,
                        "content": "Here is an image:\n",
                        "epilogue": None,
                    },
                    {
                        "unixfrom": None,
                        "headers": {
                            "content-type": {
                                "content_type": "image/png",
                                "params": {},
                            },
                            "content-disposition": {
                                "disposition": "attachment",
                                "params": {"filename": "blob.png"},
                            },
                            "content-id": [img_cid],
                        },
                        "preamble": None,
                        "content": b"\1\2\3\4\5",
                        "epilogue": None,
                    },
                ],
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "multipart/related",
                        "params": {"type": "text/html"},
                    },
                    "content-id": [related_cid],
                },
                "preamble": None,
                "content": [
                    {
                        "unixfrom": None,
                        "headers": {
                            "content-type": {
                                "content_type": "text/html",
                                "params": {},
                            },
                        },
                        "preamble": None,
                        "content": HTML,
                        "epilogue": None,
                    },
                    {
                        "unixfrom": None,
                        "headers": {
                            "content-type": {
                                "content_type": "image/png",
                                "params": {},
                            },
                            "content-disposition": {
                                "disposition": "attachment",
                                "params": {"filename": "blob.png"},
                            },
                            "content-id": [img_cid],
                        },
                        "preamble": None,
                        "content": b"\1\2\3\4\5",
                        "epilogue": None,
                    },
                ],
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


@pytest.mark.parametrize("cls", [Alternative, Mixed, Related])
def test_multipart_mutable_sequences(cls: Type[Multipart]) -> None:
    t1 = TextBody("Part 1")
    t2 = TextBody("Part 2")
    t3 = TextBody("Part 3")
    t4 = TextBody("Part 4")
    seq = cls()
    assert len(seq) == 0
    assert list(seq) == []
    seq.append(t1)
    assert len(seq) == 1
    assert list(seq) == [t1]
    assert seq[0] == t1
    seq.insert(0, t2)
    assert len(seq) == 2
    assert list(seq) == [t2, t1]
    assert seq[0] == t2
    assert seq[1] == t1
    seq[1] = t3
    assert len(seq) == 2
    assert list(seq) == [t2, t3]
    assert seq[0] == t2
    assert seq[1] == t3
    seq.pop(0)
    assert len(seq) == 1
    assert list(seq) == [t3]
    assert seq[0] == t3
    seq.extend([t1, t4])
    assert len(seq) == 3
    assert list(seq) == [t3, t1, t4]
    seq.reverse()
    assert len(seq) == 3
    assert list(seq) == [t4, t1, t3]
    seq.reverse()
    assert len(seq) == 3
    assert list(seq) == [t3, t1, t4]
    assert seq[1:] == cls([t1, t4])
    seq.pop()
    assert len(seq) == 2
    assert list(seq) == [t3, t1]
    seq.remove(t1)
    assert len(seq) == 1
    assert list(seq) == [t3]
    seq += [t1, t2]
    assert len(seq) == 3
    assert list(seq) == [t3, t1, t2]
    del seq[0]
    assert len(seq) == 2
    assert list(seq) == [t1, t2]
    seq[1:] = [t3, t4]
    assert len(seq) == 3
    assert list(seq) == [t1, t3, t4]
    del seq[:2]
    assert len(seq) == 1
    assert list(seq) == [t4]
