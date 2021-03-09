import pytest
from eletter import BytesAttachment, ContentType, TextAttachment


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
