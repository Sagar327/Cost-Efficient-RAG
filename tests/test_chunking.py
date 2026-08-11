from app.chunking import chunk_text

def test_idempotent_ids():
    a=chunk_text("hello world. "*200, "a.md", 100, 20)
    b=chunk_text("hello world. "*200, "a.md", 100, 20)
    assert [x.id for x in a] == [x.id for x in b]

def test_overlap_validation():
    import pytest
    with pytest.raises(ValueError):
        chunk_text("abc", "a.md", 10, 10)
