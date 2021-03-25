import pytest
from eletter import Alternative, MailItem, Mixed, Related, TextBody
from eletter.decompose import smooth


@pytest.mark.parametrize(
    "rough,polished",
    [
        (TextBody("foo\n"), TextBody("foo\n")),
        (Mixed([]), Mixed([])),
        (Mixed([TextBody("foo\n")]), TextBody("foo\n")),
        (
            Mixed(
                [
                    TextBody("foo\n"),
                    Mixed([TextBody("bar\n"), TextBody("baz\n")]),
                    TextBody("quux\n"),
                ]
            ),
            Mixed(
                [
                    TextBody("foo\n"),
                    TextBody("bar\n"),
                    TextBody("baz\n"),
                    TextBody("quux\n"),
                ]
            ),
        ),
        (
            Mixed(
                [
                    TextBody("foo\n"),
                    Alternative([TextBody("bar\n"), TextBody("baz\n")]),
                    TextBody("quux\n"),
                ]
            ),
            Mixed(
                [
                    TextBody("foo\n"),
                    Alternative([TextBody("bar\n"), TextBody("baz\n")]),
                    TextBody("quux\n"),
                ]
            ),
        ),
        (
            Mixed(
                [
                    TextBody("foo\n"),
                    Alternative([TextBody("bar\n")]),
                    TextBody("quux\n"),
                ]
            ),
            Mixed([TextBody("foo\n"), TextBody("bar\n"), TextBody("quux\n")]),
        ),
        (
            Mixed([TextBody("foo\n"), Alternative([]), TextBody("quux\n")]),
            Mixed([TextBody("foo\n"), TextBody("quux\n")]),
        ),
        (
            Related(
                [
                    TextBody("foo\n"),
                    Related([TextBody("bar\n"), TextBody("baz\n")]),
                    TextBody("quux\n"),
                ]
            ),
            Related(
                [
                    TextBody("foo\n"),
                    Related([TextBody("bar\n"), TextBody("baz\n")]),
                    TextBody("quux\n"),
                ]
            ),
        ),
        (
            Related(
                [TextBody("foo\n"), Related([TextBody("bar\n")]), TextBody("quux\n")]
            ),
            Related([TextBody("foo\n"), TextBody("bar\n"), TextBody("quux\n")]),
        ),
        (
            Alternative([Mixed([])]),
            Alternative(),
        ),
        (
            Alternative([Mixed([TextBody("foo\n")])]),
            TextBody("foo\n"),
        ),
        (
            Alternative([Mixed([]), Mixed([TextBody("foo\n")])]),
            TextBody("foo\n"),
        ),
    ],
)
def test_smooth(rough: MailItem, polished: MailItem) -> None:
    assert smooth(rough) == polished
