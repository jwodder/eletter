from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Union
from email2dict import email2dict
import pytest
from eletter import Address, Alternative, Composable, Group, HTMLBody, TextBody
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
    "comp",
    [
        TextBody("This is the text of an e-mail."),
        HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>"),
        Alternative(
            [
                TextBody("This is the text of an e-mail."),
                HTMLBody("<p>This is the <i>text</i> of an <b>e</b>-mail.<p>"),
            ]
        ),
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
def test_composable_compose(
    comp: Composable,
    from_input: Union[AddressOrGroup, Iterable[AddressOrGroup]],
    from_output: Any,
    to_input: Iterable[AddressOrGroup],
    to_output: Any,
    reply_to_input: Union[AddressOrGroup, Iterable[AddressOrGroup]],
    reply_to_output: Any,
) -> None:
    when = datetime(2021, 3, 8, 18, 14, 29, tzinfo=timezone(timedelta(hours=-5)))
    msg = comp.compose(
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
