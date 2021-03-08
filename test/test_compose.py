from datetime import datetime, timedelta, timezone
from email2dict import email2dict
import pytest
from eletter import Address, compose


def test_compose_text() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
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


def test_compose_html() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        html="<p>This is the <i>text</i> of an <b>e</b>-mail.<p>",
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


def test_compose_text_html() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        html="<p>This is the <i>text</i> of an <b>e</b>-mail.<p>",
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


def test_compose_neither() -> None:
    with pytest.raises(ValueError) as excinfo:
        compose(
            from_="me@here.com",
            to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
            subject="Some electronic mail",
        )
    assert str(excinfo.value) == "At least one of text and html must be non-None"


def test_compose_addresses() -> None:
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
        subject="To: Everyone",
        text="This is the text of an e-mail.",
    )
    assert email2dict(msg) == {
        "unixfrom": None,
        "headers": {
            "subject": "To: Everyone",
            "from": [
                {
                    "display_name": "Mme E.",
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
            "reply-to": [
                {
                    "display_name": "",
                    "address": "replyee@some.where",
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


def test_compose_date() -> None:
    when = datetime(2021, 3, 8, 18, 14, 29, tzinfo=timezone(timedelta(hours=-5)))
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        date=when,
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
            "date": when,
            "content-type": {
                "content_type": "text/plain",
                "params": {},
            },
        },
        "preamble": None,
        "content": "This is the text of an e-mail.\n",
        "epilogue": None,
    }
