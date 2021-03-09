from datetime import datetime, timedelta, timezone
from email2dict import email2dict
import pytest
from eletter import Address, BytesAttachment, ContentType, TextAttachment, compose


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
        sender="steven.ender@big.senders",
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
            "sender": {
                "display_name": "",
                "address": "steven.ender@big.senders",
            },
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


def test_compose_headers() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        headers={
            "User-Agent": "eletter",
            "Received": [
                "From mx.example.com",
                "From mail.sender.nil",
            ],
        },
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
            "user-agent": ["eletter"],
            "received": [
                "From mx.example.com",
                "From mail.sender.nil",
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


def test_compose_text_bytes_attachment_custom_content_type() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[
            BytesAttachment(
                b"\xFE\xED\xFA\xCE",
                filename="blob.dat",
                content_type="application/x-feedface",
            )
        ],
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
                        "content_type": "application/x-feedface",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.dat"},
                    },
                },
                "preamble": None,
                "content": b"\xFE\xED\xFA\xCE",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_bytes_attachment_set_custom_content_type() -> None:
    attach = BytesAttachment(b"\xFE\xED\xFA\xCE", filename="blob.dat")
    attach.content_type = "application/x-feedface; face=pretty"
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[attach],
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
                        "content_type": "application/x-feedface",
                        "params": {"face": "pretty"},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.dat"},
                    },
                },
                "preamble": None,
                "content": b"\xFE\xED\xFA\xCE",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_bytes_attachment_custom_main_type() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[
            BytesAttachment(
                b"\xFE\xED\xFA\xCE",
                filename="blob.dat",
                content_type="image/x-feedface",
            )
        ],
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
                        "content_type": "image/x-feedface",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.dat"},
                    },
                },
                "preamble": None,
                "content": b"\xFE\xED\xFA\xCE",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_html_bytes_attachment() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        html="<p>This is the <i>text</i> of an <b>e</b>-mail.<p>",
        attachments=[
            BytesAttachment(
                b"\xFE\xED\xFA\xCE",
                filename="blob.dat",
                content_type="application/x-feedface",
            )
        ],
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
                        "content_type": "application/x-feedface",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.dat"},
                    },
                },
                "preamble": None,
                "content": b"\xFE\xED\xFA\xCE",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_bytes_attachment_default_content_type() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[
            BytesAttachment(
                b"\xFE\xED\xFA\xCE",
                filename="blob.dat",
            )
        ],
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
                        "content_type": "application/octet-stream",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.dat"},
                    },
                },
                "preamble": None,
                "content": b"\xFE\xED\xFA\xCE",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_bytes_attachment_paramed_content_type() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[
            BytesAttachment(
                b"\xFE\xED\xFA\xCE",
                filename="blob.dat",
                content_type="application/x-feedface; face=pretty",
            )
        ],
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
                        "content_type": "application/x-feedface",
                        "params": {"face": "pretty"},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.dat"},
                    },
                },
                "preamble": None,
                "content": b"\xFE\xED\xFA\xCE",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_bytes_attachment_inline() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[
            BytesAttachment(
                b"\xFE\xED\xFA\xCE",
                filename="blob.dat",
                content_type="application/x-feedface",
                inline=True,
            )
        ],
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
                        "content_type": "application/x-feedface",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "inline",
                        "params": {"filename": "blob.dat"},
                    },
                },
                "preamble": None,
                "content": b"\xFE\xED\xFA\xCE",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_text_attachment_default_content_type() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[TextAttachment("This is a text document.", filename="blob.txt")],
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
                        "content_type": "text/plain",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.txt"},
                    },
                },
                "preamble": None,
                "content": "This is a text document.\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_text_attachment_custom_content_type() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[
            TextAttachment(
                "This is a text document.",
                filename="blob.md",
                content_type="text/markdown",
            )
        ],
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
                        "content_type": "text/markdown",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.md"},
                    },
                },
                "preamble": None,
                "content": "This is a text document.\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_text_attachment_set_custom_content_type() -> None:
    attach = TextAttachment("This is a text document.", filename="blob.md")
    attach.content_type = "text/markdown; variant=CommonMark"
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[attach],
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
                        "content_type": "text/markdown",
                        "params": {"variant": "CommonMark"},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.md"},
                    },
                },
                "preamble": None,
                "content": "This is a text document.\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_text_attachment_paramed_content_type() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[
            TextAttachment(
                "This is a text document.",
                filename="blob.md",
                content_type="text/markdown; variant=CommonMark",
            )
        ],
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
                        "content_type": "text/markdown",
                        "params": {"variant": "CommonMark"},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.md"},
                    },
                },
                "preamble": None,
                "content": "This is a text document.\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_compose_text_text_attachment_inline() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[
            TextAttachment("This is a text document.", filename="blob.txt", inline=True)
        ],
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
                        "content_type": "text/plain",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "inline",
                        "params": {"filename": "blob.txt"},
                    },
                },
                "preamble": None,
                "content": "This is a text document.\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }


def test_text_attachment_non_text_content_type() -> None:
    with pytest.raises(ValueError) as excinfo:
        TextAttachment("[]", filename="foo.json", content_type="application/json")
    assert str(excinfo.value) == "content_type must be text/*"


def test_text_attachment_set_non_text_content_type() -> None:
    a = TextAttachment("[]", filename="foo.json")
    with pytest.raises(ValueError) as excinfo:
        a.content_type = "application/json"
    assert str(excinfo.value) == "content_type must be text/*"
    assert a.content_type == "text/plain"
    assert a._ct == ContentType("text", "plain", {})


def test_text_attachment_bad_content_type() -> None:
    with pytest.raises(ValueError) as excinfo:
        TextAttachment("[]", filename="foo.json", content_type="application-json")
    assert str(excinfo.value) == "application-json"


def test_text_attachment_set_bad_content_type() -> None:
    a = TextAttachment("[]", filename="foo.json")
    with pytest.raises(ValueError) as excinfo:
        a.content_type = "application-json"
    assert str(excinfo.value) == "application-json"
    assert a.content_type == "text/plain"
    assert a._ct == ContentType("text", "plain", {})


def test_bytes_attachment_bad_content_type() -> None:
    with pytest.raises(ValueError) as excinfo:
        BytesAttachment(b"[]", filename="foo.json", content_type="application-json")
    assert str(excinfo.value) == "application-json"


def test_bytes_attachment_set_bad_content_type() -> None:
    a = BytesAttachment(b"[]", filename="foo.json")
    with pytest.raises(ValueError) as excinfo:
        a.content_type = "application-json"
    assert str(excinfo.value) == "application-json"
    assert a.content_type == "application/octet-stream"
    assert a._ct == ContentType("application", "octet-stream", {})


def test_compose_text_text_attachment_charset() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="This is the text of an e-mail.",
        attachments=[
            TextAttachment(
                "This is a text document.",
                filename="blob.txt",
                content_type="text/plain; charset=iso-8859-1",
            )
        ],
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
                        "content_type": "text/plain",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.txt"},
                    },
                },
                "preamble": None,
                "content": "This is a text document.\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }
    assert email2dict(msg, include_all=True)["content"][1]["headers"]["content-type"][
        "params"
    ] == {"charset": "iso-8859-1"}


def test_compose_html_bytes_attachment_text_attachment() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        html="<p>This is the <i>text</i> of an <b>e</b>-mail.<p>",
        attachments=[
            BytesAttachment(
                b"\xFE\xED\xFA\xCE",
                filename="blob.dat",
                content_type="application/x-feedface",
            ),
            TextAttachment("This is a text document.", filename="foo.txt"),
        ],
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
                        "content_type": "application/x-feedface",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "blob.dat"},
                    },
                },
                "preamble": None,
                "content": b"\xFE\xED\xFA\xCE",
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/plain",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "foo.txt"},
                    },
                },
                "preamble": None,
                "content": "This is a text document.\n",
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }
