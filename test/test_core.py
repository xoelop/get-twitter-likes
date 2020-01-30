from src.core import parse_date, get_likes_ids, split_list_sublists
import numpy as np


def test_parse_date():
    assert parse_date('Wed Jan 22 18:14:34 +0000 2020') == '2020-01-22T18:14:34.000Z'


def test_get_likes_ids():
    ids = get_likes_ids()
    print(len(ids))
    assert len(ids)


def test_split_list_sublists():
    ids = np.arange(1, 10000)
    sublists = split_list_sublists(ids)
    print(len(sublists))
    assert sum([len(l) for l in sublists]) == len(ids)

