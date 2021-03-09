from typing import Any, Dict, Tuple
import pytest
from eletter import assemble_content_type, get_mime_type, parse_content_type


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
