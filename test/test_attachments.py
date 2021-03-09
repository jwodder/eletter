from pathlib import Path
import attr
from email2dict import email2dict
import pytest
from eletter import BytesAttachment, ContentType, EmailAttachment, TextAttachment

DATA_DIR = Path(__file__).with_name("data")

PNG = bytes.fromhex(
    "89 50 4e 47 0d 0a 1a 0a  00 00 00 0d 49 48 44 52"
    "00 00 00 10 00 00 00 10  08 06 00 00 00 1f f3 ff"
    "61 00 00 00 06 62 4b 47  44 00 ff 00 ff 00 ff a0"
    "bd a7 93 00 00 00 09 70  48 59 73 00 00 00 48 00"
    "00 00 48 00 46 c9 6b 3e  00 00 00 09 76 70 41 67"
    "00 00 00 10 00 00 00 10  00 5c c6 ad c3 00 00 00"
    "5b 49 44 41 54 38 cb c5  92 51 0a c0 30 08 43 7d"
    "b2 fb 5f 39 fb 12 da 61  a9 c3 8e f9 a7 98 98 48"
    "90 64 9d f2 16 da cc ae  b1 01 26 39 92 d8 11 10"
    "16 9e e0 8c 64 dc 89 b9  67 80 ca e5 f3 3f a8 5c"
    "cd 76 52 05 e1 b5 42 ea  1d f0 91 1f b4 09 78 13"
    "e5 52 0e 00 ad 42 f5 bf  85 4f 14 dc 46 b3 32 11"
    "6c b1 43 99 00 00 00 00  49 45 4e 44 ae 42 60 82"
)

PY = """\
def fibonacci(n):
    (a, b) = (0, 1)
    for _ in range(n):
        (a, b) = (b, a + b)
    return a
"""


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


def test_bytes_attachment_from_file() -> None:
    ba = BytesAttachment.from_file(DATA_DIR / "ternary.png")
    assert ba == BytesAttachment(
        PNG, filename="ternary.png", content_type="image/png", inline=False
    )


def test_bytes_attachment_from_file_content_type() -> None:
    ba = BytesAttachment.from_file(
        DATA_DIR / "ternary.png", content_type="application/x-ternary"
    )
    assert ba == BytesAttachment(
        PNG, filename="ternary.png", content_type="application/x-ternary", inline=False
    )


def test_text_attachment_from_file() -> None:
    ta = TextAttachment.from_file(DATA_DIR / "fibonacci.py")
    assert ta == TextAttachment(
        PY, filename="fibonacci.py", content_type="text/x-python", inline=False
    )


def test_text_attachment_from_file_content_type() -> None:
    ta = TextAttachment.from_file(
        DATA_DIR / "fibonacci.py", content_type="text/x-fibonacci; lang=python"
    )
    assert ta == TextAttachment(
        PY,
        filename="fibonacci.py",
        content_type="text/x-fibonacci; lang=python",
        inline=False,
    )


def test_email_attachment_from_file() -> None:
    ea = EmailAttachment.from_file(DATA_DIR / "sample.eml")
    assert attr.asdict(ea, filter=lambda attr, _: attr.name != "content") == {
        "filename": "sample.eml",
        "inline": False,
    }
    assert email2dict(ea.content) == {
        "unixfrom": None,
        "headers": {
            "from": [
                {
                    "display_name": "Steven E'Nder",
                    "address": "sender@example.nil",
                },
            ],
            "to": [
                {
                    "display_name": "",
                    "address": "recipient@redacted.nil",
                },
            ],
            "subject": "Seeking a job",
            "content-type": {
                "content_type": "multipart/mixed",
                "params": {},
            },
            "user-agent": [
                "Mutt/1.5.24 (2015-08-30)",
            ],
        },
        "preamble": "",
        "content": [
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/plain",
                        "params": {},
                    },
                    "content-disposition": {
                        "disposition": "inline",
                        "params": {},
                    },
                },
                "preamble": None,
                "content": "Please find my credentials attached.\n\n",
                "epilogue": None,
            },
            {
                "unixfrom": None,
                "headers": {
                    "content-type": {
                        "content_type": "text/plain",
                        "params": {"name": "résumé.txt"},
                    },
                    "content-disposition": {
                        "disposition": "attachment",
                        "params": {"filename": "résumé.txt"},
                    },
                },
                "preamble": None,
                "content": "- Wrote email2dict\n- Has a pulse (sometimes)\n",
                "epilogue": None,
            },
        ],
        "epilogue": "",
    }
