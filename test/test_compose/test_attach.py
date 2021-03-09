from email2dict import email2dict
from eletter import Address, BytesAttachment, EmailAttachment, TextAttachment, compose


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


def test_compose_email_attachment() -> None:
    msg = compose(
        from_="me@here.com",
        to=["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
        subject="Some electronic mail",
        text="Here's that e-mail you wanted me to send.",
        attachments=[
            EmailAttachment(
                compose(
                    from_="somebody@some.where",
                    to=["me@here.com"],
                    subject="A pretty picture!",
                    text="Look at the pretty picture!  ... It came through, right?",
                    attachments=[
                        BytesAttachment(
                            b"\xFE\xED\xFA\xCE",
                            filename="blob.dat",
                            content_type="application/x-feedface",
                        )
                    ],
                ),
                filename="message.eml",
                inline=False,
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
                "content": "Here's that e-mail you wanted me to send.\n",
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "message/rfc822",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "message.eml"},
                    },
                },
                "preamble": None,
                "content": {
                    "unixfrom": None,
                    "headers": {
                        "subject": "A pretty picture!",
                        "from": [
                            {
                                "display_name": "",
                                "address": "somebody@some.where",
                            },
                        ],
                        "to": [
                            {
                                "display_name": "",
                                "address": "me@here.com",
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
                            "content": (
                                "Look at the pretty picture!  ... It came"
                                " through, right?\n"
                            ),
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
                },
                "epilogue": None,
            },
        ],
        "epilogue": None,
    }
