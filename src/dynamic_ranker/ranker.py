from dataclasses import dataclass
from typing import Any


class DynamicRankerError(Exception):
    pass


class InvalidAttributeError(DynamicRankerError):
    pass


class InvalidWeightError(DynamicRankerError):
    pass


@dataclass
class RankedItem[T]:
    item: T
    score_final: float


class DynamicRanker:
    @staticmethod
    def _extract_attribute_value(item: Any, attribute_name: str) -> float:
        if isinstance(item, dict):
            if attribute_name not in item:
                raise InvalidAttributeError(f"Attribute '{attribute_name}' not found in item")
            raw_value = item[attribute_name]
        else:
            if not hasattr(item, attribute_name):
                raise InvalidAttributeError(f"Attribute '{attribute_name}' not found in item")
            raw_value = getattr(item, attribute_name)

        if not isinstance(raw_value, (int, float)) or isinstance(raw_value, bool):
            raise InvalidAttributeError(
                f"Attribute '{attribute_name}' must be numeric, got {type(raw_value).__name__}"
            )

        return float(raw_value)

    @classmethod
    def rank[T](
        cls,
        items: list[T],
        weights: dict[str, float],
        limit: int | None = None,
    ) -> list[RankedItem[T]]:
        if not weights:
            raise InvalidWeightError("Weights dictionary must not be empty")

        for attr_name, weight in weights.items():
            if not isinstance(weight, (int, float)) or isinstance(weight, bool):
                raise InvalidWeightError(f"Weight for '{attr_name}' must be numeric")

        ranked_results: list[RankedItem[T]] = []
        for item in items:
            score = 0.0
            for attr_name, weight in weights.items():
                value = cls._extract_attribute_value(item, attr_name)
                score += value * float(weight)

            ranked_results.append(RankedItem(item=item, score_final=round(score, 4)))

        ranked_results.sort(key=lambda r: r.score_final, reverse=True)

        if limit is not None and limit >= 0:
            return ranked_results[:limit]

        return ranked_results
