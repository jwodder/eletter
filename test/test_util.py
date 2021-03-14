from typing import Dict
import pytest
from eletter import assemble_content_type, reply_quote
from eletter.util import get_mime_type


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
