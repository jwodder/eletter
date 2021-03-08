from email2dict import email2dict
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
