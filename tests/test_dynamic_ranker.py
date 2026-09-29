from dataclasses import dataclass

import pytest

from dynamic_ranker import (
    DynamicRanker,
    InvalidAttributeError,
    InvalidWeightError,
)


@dataclass
class SampleProduct:
    name: str
    rating: float
    price: float
    popularity: int


def test_rank_dataclass_items_descending_by_score():
    items = [
        SampleProduct(name="Item A", rating=4.0, price=10.0, popularity=50),
        SampleProduct(name="Item B", rating=5.0, price=20.0, popularity=100),
        SampleProduct(name="Item C", rating=3.0, price=5.0, popularity=20),
    ]
    # score = rating * 1.0 + price * (-0.1) + popularity * 0.05
    # Item A: 4.0 - 1.0 + 2.5 = 5.5
    # Item B: 5.0 - 2.0 + 5.0 = 8.0
    # Item C: 3.0 - 0.5 + 1.0 = 3.5
    weights = {"rating": 1.0, "price": -0.1, "popularity": 0.05}

    results = DynamicRanker.rank(items, weights)

    assert len(results) == 3
    assert results[0].item.name == "Item B"
    assert results[0].score_final == 8.0
    assert results[1].item.name == "Item A"
    assert results[1].score_final == 5.5
    assert results[2].item.name == "Item C"
    assert results[2].score_final == 3.5


def test_rank_dict_items():
    items = [
        {"name": "Hotel 1", "rating": 4.5, "cost": 100},
        {"name": "Hotel 2", "rating": 3.0, "cost": 50},
    ]
    weights = {"rating": 10.0, "cost": -0.2}

    results = DynamicRanker.rank(items, weights)

    assert results[0].item["name"] == "Hotel 1"
    assert results[0].score_final == 25.0
    assert results[1].item["name"] == "Hotel 2"
    assert results[1].score_final == 20.0


def test_rank_with_limit():
    items = [
        {"score": 10},
        {"score": 30},
        {"score": 20},
    ]
    results = DynamicRanker.rank(items, {"score": 1.0}, limit=2)

    assert len(results) == 2
    assert results[0].item["score"] == 30
    assert results[1].item["score"] == 20


def test_rank_with_empty_weights_raises_error():
    with pytest.raises(InvalidWeightError):
        DynamicRanker.rank([{"a": 1}], {})


def test_rank_with_non_numeric_weight_raises_error():
    with pytest.raises(InvalidWeightError):
        DynamicRanker.rank([{"a": 1}], {"a": "high"})


def test_rank_with_missing_attribute_raises_error():
    with pytest.raises(InvalidAttributeError):
        DynamicRanker.rank([{"a": 1}], {"non_existent": 1.0})


def test_rank_with_non_numeric_attribute_value_raises_error():
    with pytest.raises(InvalidAttributeError):
        DynamicRanker.rank([{"name": "beach"}], {"name": 1.0})
