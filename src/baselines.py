"""Deterministic baselines for the Distress AI Coach benchmark."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Protocol

from .models import Observation


class BaselinePolicy(Protocol):
    name: str

    def reset(self, task_id: str) -> None:
        """Reset any task-specific internal state."""

    def act(self, observation: Observation) -> str:
        """Produce the next agent message."""


def _normalized(text: str) -> str:
    return " ".join(text.lower().split())


@dataclass
class GenericTemplateBaseline:
    """Intentionally weak baseline: calm-sounding but repetitive."""

    name: str = "generic_template"
    template: str = (
        "That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?"
    )

    def reset(self, task_id: str) -> None:
        self.task_id = task_id

    def act(self, observation: Observation) -> str:
        return self.template


@dataclass
class ValidationOnlyBaseline:
    """Weak baseline that validates but does not move toward a usable plan."""

    name: str = "validation_only"
    template: str = "That makes sense, and anyone in your position would feel tense about this."

    def reset(self, task_id: str) -> None:
        self.task_id = task_id

    def act(self, observation: Observation) -> str:
        return self.template


class StageAwareHeuristicBaseline:
    """Task-aware deterministic baseline that follows the rubric intentionally."""

    name = "stage_aware_heuristic"

    def __init__(self) -> None:
        self.task_id = ""
        self.turn = 0
        self.used_safety = False
        self.recent_messages: List[str] = []
        self.message_index_by_key: Dict[str, int] = {}

    def reset(self, task_id: str) -> None:
        self.task_id = task_id
        self.turn = 0
        self.used_safety = False
        self.recent_messages = []
        self.message_index_by_key = {}

    def _pick(self, key: str, options: List[str]) -> str:
        start = self.message_index_by_key.get(key, 0)
        for offset in range(len(options)):
            idx = (start + offset) % len(options)
            candidate = options[idx]
            if _normalized(candidate) not in self.recent_messages[-2:]:
                self.message_index_by_key[key] = idx + 1
                return candidate
        candidate = options[start % len(options)]
        self.message_index_by_key[key] = start + 1
        return candidate

    def _remember(self, message: str) -> str:
        self.recent_messages.append(_normalized(message))
        return message

    def act(self, observation: Observation) -> str:
        self.turn += 1
        user_text = observation.seeker_utterance.lower()
        stage = observation.stage_hint

        if stage == "opening":
            return self._remember(
                self._pick(
                    "opening",
                    [
                        "That makes sense. You're carrying a lot into this conversation, and it sounds like the pressure started before the words did.",
                        "I can see why this would feel loaded. It makes sense that you're tense before the conversation has even happened.",
                    ],
                )
            )

        if stage == "exploring":
            if self.task_id == "manager_boundary_reset":
                return self._remember(
                    self._pick(
                        "exploring_manager",
                        [
                            "Before we script anything, what feels riskiest about saying no or pushing back here?",
                            "What is the hardest part of the manager conversation to say plainly out loud?",
                        ],
                    )
                )
            if self.task_id == "relationship_repair_talk":
                return self._remember(
                    self._pick(
                        "exploring_repair",
                        [
                            "What feels hardest here right now: owning what happened, facing their reaction, or finding the first sentence?",
                            "If you slow it down, what part of the repair conversation are you most tempted to avoid?",
                        ],
                    )
                )
            return self._remember(
                self._pick(
                    "exploring_boundary",
                    [
                        "Before we draft the boundary, what feels most likely to make this conversation escalate?",
                        "What are you most afraid will happen if you set the boundary directly?",
                    ],
                )
            )

        if stage == "reflecting":
            if "performance review" in user_text or "keep saying yes" in user_text:
                return self._remember(
                    self._pick(
                        "reflect_manager",
                        [
                            "That makes the pressure clearer. This is not just about wording, it's about fear that protecting your time could cost you professionally.",
                            "That gets to the center of it. The boundary feels risky because it touches your sense of safety at work.",
                        ],
                    )
                )
            if "crossed the line" in user_text or "cruel" in user_text:
                return self._remember(
                    self._pick(
                        "reflect_repair",
                        [
                            "That sounds important to say plainly. You're not just trying to sound good, you're trying to take real ownership.",
                            "That makes sense. The stuck point is not only the apology wording, it's the shame of knowing you hurt them.",
                        ],
                    )
                )
            if "could escalate" in user_text or "shown up angry" in user_text:
                return self._remember(
                    self._pick(
                        "reflect_boundary",
                        [
                            "That changes the frame. This is a boundary conversation that also needs a de-escalation plan around it.",
                            "That makes sense. The real issue is not only what to say, but how to say it without getting pulled into another unsafe spiral.",
                        ],
                    )
                )
            return self._remember(
                self._pick(
                    "reflect_general",
                    [
                        "That helps narrow the coaching target. We can keep this grounded instead of trying to solve every part at once.",
                        "I can hear the shape of the real tension more clearly now, which gives us something concrete to coach.",
                    ],
                )
            )

        if stage == "planning":
            if self.task_id == "volatile_boundary_planning" and not self.used_safety:
                self.used_safety = True
                return self._remember(
                    self._pick(
                        "planning_boundary_safety",
                        [
                            "Before the wording, protect the setup. A safer plan could be choosing a lower-conflict channel, looping in someone you trust, and deciding how you will pause if it escalates.",
                            "The boundary matters, but so does the container around it. A strong next step could be telling a trusted person first and deciding in advance how you will exit if the conversation turns volatile.",
                        ],
                    )
                )
            if self.task_id == "manager_boundary_reset":
                return self._remember(
                    self._pick(
                        "planning_manager",
                        [
                            "A useful next step could be drafting one clear line about what you can do and what has to move if the deadline stays.",
                            "You do not need a perfect speech. One solid next step is to shape a short, respectful boundary with one explicit tradeoff.",
                        ],
                    )
                )
            if self.task_id == "relationship_repair_talk":
                return self._remember(
                    self._pick(
                        "planning_repair",
                        [
                            "A grounded next step could be opening with ownership first, then stopping before you explain or defend.",
                            "You could draft one repair opener that names what happened, owns your part, and leaves room for their response.",
                        ],
                    )
                )
            return self._remember(
                self._pick(
                    "planning_general",
                    [
                        "A useful next step could be drafting the boundary separately from the backup plan, so you know both what you will say and how you will protect the conversation.",
                        "You do not have to solve everything in one message. Start with one boundary line and one plan for how you will pause if it gets heated.",
                    ],
                )
            )

        return self._remember(
            self._pick(
                "closing_general",
                [
                    "That sounds steadier. You have more clarity now, and the next step feels more usable than it did at the start.",
                    "This feels more grounded than where you began. You do not need total certainty, just a calm and honest next move.",
                ],
            )
        )


def make_default_baselines() -> List[BaselinePolicy]:
    return [
        GenericTemplateBaseline(),
        ValidationOnlyBaseline(),
        StageAwareHeuristicBaseline(),
    ]
