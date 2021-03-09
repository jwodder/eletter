from typing import Any, Dict, List, Tuple, Union
import pytest
from eletter import (
    Address,
    Group,
    assemble_content_type,
    format_addresses,
    get_mime_type,
    parse_content_type,
    reply_quote,
)


@pytest.mark.parametrize(
    "s,ct",
    [
        ("text/plain", ("text", "plain", {})),
        ("TEXT/PLAIN", ("text", "plain", {})),
        ("text/plain; charset=utf-8", ("text", "plain", {"charset": "utf-8"})),
        ('text/plain; charset="utf-8"', ("text", "plain", {"charset": "utf-8"})),
        (
            "text/markdown; charset=utf-8; variant=GFM",
            ("text", "markdown", {"charset": "utf-8", "variant": "GFM"}),
        ),
        (
            'text/plain; charset="utf-\u2603"',
            ("text", "plain", {"charset": "utf-\u2603"}),
        ),
        (
            "text/plain; charset*=utf-8''utf-%E2%98%83",
            ("text", "plain", {"charset": "utf-\u2603"}),
        ),
    ],
)
def test_parse_content_type(s: str, ct: Tuple[str, str, Dict[str, Any]]) -> None:
    assert parse_content_type(s) == ct


@pytest.mark.parametrize(
    "s",
    [
        "text",
        "text/",
        "/plain",
        "text/plain, charset=utf-8",
    ],
)
def test_parse_content_type_error(s: str) -> None:
    with pytest.raises(ValueError):
        parse_content_type(s)


@pytest.mark.parametrize(
    "maintype,subtype,params,ct",
    [
        ("text", "plain", {}, "text/plain"),
        ("TEXT", "PLAIN", {}, "TEXT/PLAIN"),
        ("text", "plain", {"charset": "utf-8"}, 'text/plain; charset="utf-8"'),
        ("text", "plain", {"name": "résumé.txt"}, 'text/plain; name="résumé.txt"'),
        ("text", "plain", {"name": 'foo"bar'}, 'text/plain; name="foo\\"bar"'),
        (
            "text",
            "markdown",
            {"charset": "utf-8", "variant": "GFM"},
            'text/markdown; charset="utf-8"; variant="GFM"',
        ),
    ],
)
def test_assemble_content_type(
    maintype: str, subtype: str, params: Dict[str, str], ct: str
) -> None:
    assert assemble_content_type(maintype, subtype, **params) == ct


@pytest.mark.parametrize(
    "maintype,subtype",
    [
        ("text/plain", "plain"),
        ("text", ""),
        ("text/", "plain"),
    ],
)
def test_assemble_content_type_error(maintype: str, subtype: str) -> None:
    with pytest.raises(ValueError) as excinfo:
        assemble_content_type(maintype, subtype)
    assert str(excinfo.value) == f"{maintype}/{subtype}"


@pytest.mark.parametrize(
    "filename,mtype",
    [
        ("foo.txt", "text/plain"),
        ("foo", "application/octet-stream"),
        ("foo.gz", "application/gzip"),
        ("foo.tar.gz", "application/gzip"),
        ("foo.tgz", "application/gzip"),
        ("foo.taz", "application/gzip"),
        ("foo.svg.gz", "application/gzip"),
        ("foo.svgz", "application/gzip"),
        ("foo.Z", "application/x-compress"),
        ("foo.tar.Z", "application/x-compress"),
        ("foo.bz2", "application/x-bzip2"),
        ("foo.tar.bz2", "application/x-bzip2"),
        ("foo.tbz2", "application/x-bzip2"),
        ("foo.xz", "application/x-xz"),
        ("foo.tar.xz", "application/x-xz"),
        ("foo.txz", "application/x-xz"),
    ],
)
def test_get_mime_type(filename: str, mtype: str) -> None:
    assert get_mime_type(filename) == mtype


@pytest.mark.parametrize(
    "inp,output",
    [
        ("", "> \n"),
        ("\n", "> \n"),
        ("Insert output here.", "> Insert output here.\n"),
        ("Insert output here.\n", "> Insert output here.\n"),
        (
            "Insert output here.\nOutsert input there.",
            "> Insert output here.\n> Outsert input there.\n",
        ),
        (
            "Insert output here.\nOutsert input there.\n",
            "> Insert output here.\n> Outsert input there.\n",
        ),
        (
            "Insert output here.\r\nOutsert input there.\r\n",
            "> Insert output here.\r\n> Outsert input there.\r\n",
        ),
        (
            "Insert output here.\rOutsert input there.\r",
            "> Insert output here.\r> Outsert input there.\r",
        ),
        (
            "Insert output here.\n\nOutsert input there.\n",
            "> Insert output here.\n> \n> Outsert input there.\n",
        ),
        (
            "> Insert output here.\n> \n> Outsert input there.\n",
            ">> Insert output here.\n>> \n>> Outsert input there.\n",
        ),
    ],
)
def test_reply_quote(inp: str, output: str) -> None:
    assert reply_quote(inp) == output


def test_reply_quote_custom_prefix() -> None:
    assert (
        reply_quote("Insert output here.\n\n: Outsert input there.\n", ": ")
        == ": Insert output here.\n: \n:: Outsert input there.\n"
    )


@pytest.mark.parametrize(
    "addresses,fmt",
    [
        ([], ""),
        (["foo@example.com"], "foo@example.com"),
        (["foo@example.com", "bar@example.org"], "foo@example.com, bar@example.org"),
        ([Address("Fabian Oo", "foo@example.com")], "Fabian Oo <foo@example.com>"),
        (
            [
                Address("Fabian Oo", "foo@example.com"),
                Address("Bastian Arrr", "bar@example.org"),
            ],
            "Fabian Oo <foo@example.com>, Bastian Arrr <bar@example.org>",
        ),
        (
            [Address("Fabian O. Oh", "foo@example.com")],
            '"Fabian O. Oh" <foo@example.com>',
        ),
        (
            [Address("Zoë Façade", "zoe.facade@naïveté.fr")],
            "Zoë Façade <zoe.facade@naïveté.fr>",
        ),
        (
            [
                Group("undisclosed recipients", []),
                "luser@example.nil",
                Group(
                    "friends",
                    ["you@there.net", Address("Thaddeus Hem", "them@hither.yon")],
                ),
            ],
            "undisclosed recipients:;, luser@example.nil,"
            " friends: you@there.net, Thaddeus Hem <them@hither.yon>;",
        ),
    ],
)
def test_format_addresses(
    addresses: List[Union[str, Address, Group]], fmt: str
) -> None:
    assert format_addresses(addresses) == fmt
