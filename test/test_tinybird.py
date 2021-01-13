from src.tinybird import append_likes_csv


def test_append_likes_csv():
    result = append_likes_csv(file='data/latest_likes.csv')
    assert result
