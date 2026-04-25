"""Agentic skill-routed policies and durable policy memory."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Protocol

from .models import Observation


def _normalized(text: str) -> str:
    return " ".join(text.lower().split())


def _contains_any(text: str, markers: List[str]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


REVEAL_MARKERS: Dict[str, List[str]] = {
    "manager_boundary_reset": ["performance review", "keep saying yes"],
    "relationship_repair_talk": ["crossed the line", "cruel"],
    "volatile_boundary_planning": ["shown up angry", "could escalate"],
}


@dataclass
class SkillDecision:
    skill_name: str
    rationale: str


@dataclass
class AgentMemory:
    task_id: str = ""
    turns_seen: int = 0
    session_index: int = 1
    sessions_total: int = 1
    used_safety: bool = False
    seeker_revealed: bool = False
    rolling_summary: str = ""
    last_session_outcome: str = ""
    current_goal_hint: str = ""
    episode_budget_spent: float = 0.0
    episode_budget_limit: float = 0.0
    episode_time_spent: float = 0.0
    episode_time_limit: float = 0.0
    risk_markers: List[str] = field(default_factory=list)
    unresolved_threads: List[str] = field(default_factory=list)
    recent_messages: List[str] = field(default_factory=list)
    recent_skills: List[str] = field(default_factory=list)
    recent_turns: List[str] = field(default_factory=list)
    message_index_by_key: Dict[str, int] = field(default_factory=dict)
    skill_counts: Dict[str, int] = field(default_factory=dict)

    def reset(self, task_id: str) -> None:
        self.task_id = task_id
        self.turns_seen = 0
        self.session_index = 1
        self.sessions_total = 1
        self.used_safety = False
        self.seeker_revealed = False
        self.rolling_summary = ""
        self.last_session_outcome = ""
        self.current_goal_hint = ""
        self.episode_budget_spent = 0.0
        self.episode_budget_limit = 0.0
        self.episode_time_spent = 0.0
        self.episode_time_limit = 0.0
        self.risk_markers = []
        self.unresolved_threads = []
        self.recent_messages = []
        self.recent_skills = []
        self.recent_turns = []
        self.message_index_by_key = {}
        self.skill_counts = {}

    def observe(self, observation: Observation) -> None:
        self.task_id = observation.task_id
        self.turns_seen = observation.turn
        self.session_index = observation.session_index
        self.sessions_total = observation.sessions_total
        self.rolling_summary = observation.memory_summary or self.rolling_summary
        self.last_session_outcome = observation.last_session_outcome or self.last_session_outcome
        self.current_goal_hint = observation.current_goal_hint or self.current_goal_hint
        self.episode_budget_spent = float(observation.episode_budget_spent)
        self.episode_budget_limit = float(observation.episode_budget_limit)
        self.episode_time_spent = float(observation.episode_time_spent)
        self.episode_time_limit = float(observation.episode_time_limit)
        markers = REVEAL_MARKERS.get(observation.task_id, [])
        if _contains_any(observation.seeker_utterance, markers):
            self.seeker_revealed = True
        if "could escalate" in observation.seeker_utterance.lower() or "shown up angry" in observation.seeker_utterance.lower():
            self._add_unique(self.risk_markers, "de-escalation plan required")
        if observation.current_goal_hint:
            self._merge_goal_hint(observation.current_goal_hint)
        self._append_turn(f"User: {observation.seeker_utterance}")

    def remember(self, skill_name: str, message: str) -> None:
        normalized = _normalized(message)
        self.recent_messages.append(normalized)
        self.recent_messages = self.recent_messages[-8:]
        self.recent_skills.append(skill_name)
        self.recent_skills = self.recent_skills[-8:]
        self.skill_counts[skill_name] = self.skill_counts.get(skill_name, 0) + 1
        self._append_turn(f"Coach: {message}")
        if skill_name == "deescalate":
            self.used_safety = True
            self._add_unique(self.risk_markers, "pause, backup support, and exit plan")
        if "next step" in normalized or "first draft" in normalized or "one line" in normalized:
            self._add_unique(self.unresolved_threads, "follow through on the agreed next step")

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "AgentMemory":
        memory = cls()
        for key, value in data.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        return memory

    def prompt_context(self, observation: Observation) -> str:
        lines: List[str] = []
        if self.rolling_summary:
            lines.append("Conversation arc summary:")
            lines.append(self.rolling_summary)
        if self.last_session_outcome:
            lines.append("")
            lines.append("Last session outcome:")
            lines.append(self.last_session_outcome)
        if self.current_goal_hint:
            lines.append("")
            lines.append("Current coaching goal:")
            lines.append(self.current_goal_hint)
        if self.unresolved_threads:
            lines.append("")
            lines.append("Unresolved threads:")
            for item in self.unresolved_threads[:3]:
                lines.append(f"- {item}")
        if self.risk_markers:
            lines.append("")
            lines.append("Risk / guardrail reminders:")
            for item in self.risk_markers[:3]:
                lines.append(f"- {item}")
        if observation.episode_budget_limit > 0 or observation.episode_time_limit > 0:
            lines.append("")
            lines.append(
                "Budget status: "
                f"cost={observation.episode_budget_spent:.1f}/{observation.episode_budget_limit:.1f}, "
                f"time={observation.episode_time_spent:.1f}/{observation.episode_time_limit:.1f}"
            )
        lines.append("")
        lines.append("Recent local exchange:")
        if self.recent_turns:
            lines.extend(self.recent_turns[-6:])
        else:
            lines.append("(first turn)")
        return "\n".join(lines).strip()

    def checkpoint_summary(self) -> str:
        return self.rolling_summary or self.current_goal_hint or ""

    def _append_turn(self, text: str) -> None:
        self.recent_turns.append(text)
        self.recent_turns = self.recent_turns[-6:]

    def _add_unique(self, target: List[str], value: str) -> None:
        if value not in target:
            target.append(value)
            del target[:-4]

    def _merge_goal_hint(self, hint: str) -> None:
        normalized = hint.strip()
        if normalized:
            self._add_unique(self.unresolved_threads, normalized)


class ConversationSkill(Protocol):
    name: str
    brief: str

    def render(self, observation: Observation, memory: AgentMemory, decision: SkillDecision) -> str:
        """Produce the next deterministic message."""

    def llm_instruction(
        self,
        observation: Observation,
        memory: AgentMemory,
        decision: SkillDecision,
    ) -> str:
        """Return a short instruction block for an LLM-backed agent."""


class BaseSkill:
    name = ""
    brief = ""

    def _pick(self, memory: AgentMemory, key: str, options: List[str]) -> str:
        start = memory.message_index_by_key.get(key, 0)
        for offset in range(len(options)):
            idx = (start + offset) % len(options)
            candidate = options[idx]
            if _normalized(candidate) not in memory.recent_messages[-2:]:
                memory.message_index_by_key[key] = idx + 1
                return candidate
        candidate = options[start % len(options)]
        memory.message_index_by_key[key] = start + 1
        return candidate

    def llm_instruction(
        self,
        observation: Observation,
        memory: AgentMemory,
        decision: SkillDecision,
    ) -> str:
        return self.brief


class EmpathizeSkill(BaseSkill):
    name = "empathize"
    brief = (
        "Lead with calm, nonjudgmental attunement. Help the user feel understood "
        "before trying to script or solve the conversation."
    )

    def render(self, observation: Observation, memory: AgentMemory, decision: SkillDecision) -> str:
        return self._pick(
            memory,
            f"empathize_{observation.task_id}",
            [
                "That makes sense. You're not overreacting, and it sounds like this conversation has been carrying a lot more weight than the words alone.",
                "I can hear how much pressure is sitting under this. It makes sense that you're tense about the conversation before it has even happened.",
            ],
        )


class ClarifySkill(BaseSkill):
    name = "clarify"
    brief = (
        "Use one warm question to surface the real issue, fear, or constraint. "
        "Do not jump into a final script yet."
    )

    def render(self, observation: Observation, memory: AgentMemory, decision: SkillDecision) -> str:
        if observation.task_id == "manager_boundary_reset":
            return self._pick(
                memory,
                "clarify_manager",
                [
                    "Before we script anything, what feels riskiest about saying no or pushing back here?",
                    "What is the part of this conversation that feels hardest to name out loud to your manager?",
                ],
            )
        if observation.task_id == "relationship_repair_talk":
            return self._pick(
                memory,
                "clarify_repair",
                [
                    "What feels hardest here right now: owning what happened, facing their reaction, or finding the right first sentence?",
                    "If you slow it down, what is the part of the repair conversation you're most tempted to avoid?",
                ],
            )
        return self._pick(
            memory,
            "clarify_boundary",
            [
                "Before we draft the boundary, what feels most likely to make this conversation escalate?",
                "What are you most afraid will happen if you set the boundary directly?",
            ],
        )


class ReflectSkill(BaseSkill):
    name = "reflect"
    brief = (
        "Reflect the core issue back clearly. If the user just disclosed the real fear "
        "or accountability issue, name that shift and slow the conversation down."
    )

    def render(self, observation: Observation, memory: AgentMemory, decision: SkillDecision) -> str:
        seeker = observation.seeker_utterance.lower()
        if "performance review" in seeker or "keep saying yes" in seeker:
            return self._pick(
                memory,
                "reflect_manager_reveal",
                [
                    "That helps make the pressure clearer. This is not just about one awkward conversation, it's about fear that protecting your time could cost you professionally.",
                    "That lands differently. The real tension is that the boundary feels tied to your sense of safety at work, not just to one late-night message.",
                ],
            )
        if "crossed the line" in seeker or "cruel" in seeker:
            return self._pick(
                memory,
                "reflect_repair_reveal",
                [
                    "That sounds important to say plainly. The stuck point isn't only the wording, it's the shame that comes with knowing you actually hurt them.",
                    "That gets to the center of it. You're trying to repair something real, not just smooth over discomfort.",
                ],
            )
        if "could escalate" in seeker or "shown up angry" in seeker:
            return self._pick(
                memory,
                "reflect_boundary_reveal",
                [
                    "That changes the frame. This isn't just a wording problem, it's a boundary conversation that needs a de-escalation plan around it.",
                    "That makes sense. The real issue is not only what to say, but how to set the boundary without getting pulled into another unsafe spiral.",
                ],
            )
        return self._pick(
            memory,
            "reflect_general",
            [
                "That makes sense, and it helps narrow the problem. We can keep this grounded in what matters most instead of trying to solve everything at once.",
                "I can see the shape of the real tension more clearly now. That gives us something more specific to coach, not just a vague hard conversation.",
            ],
        )


class PlanSkill(BaseSkill):
    name = "plan"
    brief = (
        "Move toward one usable next step: a boundary line, repair opener, or draft message. "
        "Keep it concrete, calm, and low-drama."
    )

    def render(self, observation: Observation, memory: AgentMemory, decision: SkillDecision) -> str:
        if observation.task_id == "manager_boundary_reset":
            return self._pick(
                memory,
                "plan_manager",
                [
                    "A solid next step could be drafting one clear line about what you can do and what needs to move if the deadline stays. Keep it respectful and specific.",
                    "You do not need the perfect speech. One useful next step is to shape a short boundary: what is changing, what you can commit to, and where the tradeoff is.",
                ],
            )
        if observation.task_id == "relationship_repair_talk":
            return self._pick(
                memory,
                "plan_repair",
                [
                    "A grounded next step could be opening with ownership first, then stopping before you explain or defend. Keep it simple enough that it still sounds true.",
                    "You could draft one repair opener that does three things only: names what happened, owns your part, and leaves room for their response.",
                ],
            )
        return self._pick(
            memory,
            "plan_boundary",
            [
                "A useful next step could be drafting the boundary separately from the logistics: first what needs to stop, then how you will protect the conversation if it turns.",
                "You do not have to solve everything in one message. Start with one boundary line and one backup plan for how you will exit if the conversation heats up.",
            ],
        )


class DeescalateSkill(BaseSkill):
    name = "deescalate"
    brief = (
        "For high-risk conversations, explicitly center de-escalation: pause if needed, "
        "avoid live escalation, and involve a trusted person or safer setting."
    )

    def render(self, observation: Observation, memory: AgentMemory, decision: SkillDecision) -> str:
        return self._pick(
            memory,
            "deescalate_boundary",
            [
                "Before the wording, protect the setup. A safer plan could be sending it when you are calm, keeping a trusted person in the loop, and choosing an exit if the conversation starts to escalate.",
                "The boundary matters, but so does the container around it. A strong next step could be using a lower-conflict channel, telling someone you trust first, and deciding in advance how you will pause if it turns volatile.",
            ],
        )


class SkillRouter:
    """Deterministic routing logic over a small reusable skill library."""

    def choose(self, observation: Observation, memory: AgentMemory) -> SkillDecision:
        stage = observation.stage_hint

        if stage == "opening":
            return SkillDecision(
                skill_name="empathize",
                rationale="Early turns should regulate the user's stress and make the coaching space feel steady.",
            )

        if stage == "exploring":
            return SkillDecision(
                skill_name="clarify",
                rationale="This phase should surface the real fear, accountability issue, or escalation risk before scripting.",
            )

        if stage == "reflecting":
            return SkillDecision(
                skill_name="reflect",
                rationale="Reflection is more useful here than advice because the user needs the real coaching target named clearly.",
            )

        if stage == "planning":
            if observation.task_id == "volatile_boundary_planning" and not memory.used_safety:
                return SkillDecision(
                    skill_name="deescalate",
                    rationale="The hard task should explicitly address de-escalation and backup support before drafting the boundary.",
                )
            return SkillDecision(
                skill_name="plan",
                rationale="The user is ready to convert clarity into one concrete conversation step.",
            )

        return SkillDecision(
            skill_name="reflect",
            rationale="Closing turns should stabilize the plan and reinforce what the user now understands more clearly.",
        )


class SkillRoutedDeterministicPolicy:
    """Deterministic agentic baseline with explicit skill routing."""

    name = "skill_routed_deterministic"

    def __init__(self) -> None:
        self.router = SkillRouter()
        self.skills = build_default_skills()
        self.memory = AgentMemory()
        self.last_decision: SkillDecision | None = None
        self.decision_log: List[Dict[str, str]] = []

    def reset(self, task_id: str) -> None:
        self.memory.reset(task_id)
        self.last_decision = None
        self.decision_log = []

    def act(self, observation: Observation) -> str:
        self.memory.observe(observation)
        decision = self.router.choose(observation, self.memory)
        skill = self.skills[decision.skill_name]
        message = skill.render(observation, self.memory, decision)
        self.memory.remember(decision.skill_name, message)
        self.last_decision = decision
        self.decision_log.append(
            {
                "turn": str(observation.turn),
                "stage": observation.stage_hint,
                "skill": decision.skill_name,
                "reason": decision.rationale,
                "message": message,
            }
        )
        return message


def build_default_skills() -> Dict[str, ConversationSkill]:
    skills: List[ConversationSkill] = [
        EmpathizeSkill(),
        ClarifySkill(),
        ReflectSkill(),
        PlanSkill(),
        DeescalateSkill(),
    ]
    return {skill.name: skill for skill in skills}
