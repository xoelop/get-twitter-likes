from src.tinybird import get_all_likes_ids


def test_get_all_likes_ids():
    ids = get_all_likes_ids()
    assert ids
    assert type(ids) == list