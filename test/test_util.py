from typing import Any, Dict, Tuple
import pytest
from eletter import parse_content_type


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
