from src.tinybird import append_likes_csv, get_all_likes_ids


def test_get_all_likes_ids():
    ids = get_all_likes_ids()
    assert ids
    assert type(ids) == list

def test_append_likes_csv():
    result = append_likes_csv(file='data/latest_likes.csv')
    assert result