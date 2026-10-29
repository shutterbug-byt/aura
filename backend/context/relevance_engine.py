from dataclasses import dataclass
from datetime import datetime
from typing import Any
from unittest import result

from backend.memory.memory_manager import Memory


@dataclass
class RankedMemory:
    memory: Memory
    score: float
    reasons: list[str]


class RelevanceEngine:

    def __init__(self):
        pass

    def calculate_score(
        self,
        memory: Memory,
        context: dict[str, Any],
    ) -> RankedMemory:

        score = 0.0
        reasons = []

        # ---------------------------------------------------------
        # 1. Scope
        # ---------------------------------------------------------

        if memory.scope == "global":
            score += 1.0
            reasons.append("global memory")

        elif memory.scope == "contextual":
            if self._context_matches(memory, context):
                score += 3.0
                reasons.append("context matches")
            else:
                return RankedMemory(
                    memory=memory,
                    score=0.0,
                    reasons=["context does not match"],
                )

        # ---------------------------------------------------------
        # 2. Importance
        # ---------------------------------------------------------

        importance_score = memory.importance * 3.0
        score += importance_score

        if memory.importance >= 0.8:
            reasons.append("high importance")

        # ---------------------------------------------------------
        # 3. Confidence
        # ---------------------------------------------------------

        confidence_score = memory.confidence * 2.0
        score += confidence_score

        if memory.confidence >= 0.8:
            reasons.append("high confidence")

        # ---------------------------------------------------------
        # 4. Recency
        # ---------------------------------------------------------

        recency_score = self._recency_score(memory)
        score += recency_score

        if recency_score > 0:
            reasons.append("recently created or used")

        return RankedMemory(
            memory=memory,
            score=score,
            reasons=reasons,
        )

    def rank_memories(
        self,
        memories: list[Memory],
        context: dict[str, Any],
        min_score: float = 0.0,
        max_results: int = 5,
    ) -> list[RankedMemory]:

        ranked = []

        for memory in memories:

            result = self.calculate_score(
                memory,
                context,
            )

            if result.score > min_score:
                ranked.append(result)
                
        ranked.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return ranked[:max_results]

    def _context_matches(
        self,
        memory: Memory,
        context: dict[str, Any],
    ) -> bool:

        if not memory.related_context:
            return False

        for key, expected_value in memory.related_context.items():

            if context.get(key) != expected_value:
                return False

        return True

    def _recency_score(
        self,
        memory: Memory,
    ) -> float:

        now = datetime.now()

        reference_time = (
            memory.last_used
            if memory.last_used is not None
            else memory.created_at
        )

        age_hours = (
            now - reference_time
        ).total_seconds() / 3600

        if age_hours <= 1:
            return 2.0

        if age_hours <= 24:
            return 1.0

        if age_hours <= 168:
            return 0.5

        return 0.0