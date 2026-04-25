"""Multi-session task specifications for the Distress AI Coach benchmark."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .seeker import SeekerPersona


@dataclass
class TaskSpec:
    id: str
    difficulty: str
    max_turns: int
    persona: SeekerPersona
    success_threshold: float
    required_final_stage: str
    min_final_trust: float
    max_final_distress: float
    require_reveal: bool = True
    require_safety_reference: bool = False
    sessions_total: int = 3
    session_turn_limit: int = 4
    cost_budget: float = 220.0
    time_budget: float = 18.0
    working_goals: List[str] = field(default_factory=list)
    session_openers: List[str] = field(default_factory=list)


_MANAGER_BOUNDARY = SeekerPersona(
    task_id="manager_boundary_reset",
    scenario_brief=(
        "A professional wants help preparing a boundary-setting conversation with "
        "their manager after repeated after-hours demands."
    ),
    surface_concern=(
        "I need to talk to my manager about the late-night pings and shifting deadlines, "
        "but I'm worried it'll make me look difficult."
    ),
    true_issue=(
        "I keep saying yes because I'm scared it will hurt my performance review, "
        "and now I'm exhausted and starting to resent the job."
    ),
    initial_distress=0.58,
    initial_trust=0.50,
    initial_openness=0.52,
    reveal_threshold=0.70,
    trust_fragility=0.22,
    openness_gain_per_empathy=0.14,
    distress_drop_per_validation=0.18,
    opening_lines=[
        "I know this probably sounds small, but it's been eating at me all week.",
        "Every time I think about bringing it up I hear myself sounding ungrateful.",
    ],
    exploring_lines=[
        "It's not just one message. It's the feeling that I have to be available all the time.",
        "I keep rewriting the conversation in my head and making myself the problem.",
        "Part of me wants to be direct and part of me wants to apologize for even asking.",
    ],
    reflecting_lines=[
        "Saying that out loud helps. I think I've been pretending it's more manageable than it is.",
        "Yeah, I do keep minimizing it. I don't want to admit how resentful I've gotten.",
    ],
    planning_lines=[
        "Maybe I need to be clearer about what I can actually commit to.",
        "I could probably name one boundary instead of trying to explain my whole life story.",
    ],
    closing_lines=[
        "That feels a lot more doable than the speech I was building in my head.",
        "I think I can actually send a message or say this in our next one-on-one.",
    ],
    reveal_line=(
        "Okay, the real thing is I'm scared that if I stop saying yes to everything, "
        "it'll hurt my review. That's why I keep overcommitting."
    ),
    dismissed_lines=[
        "Right. Maybe I should just suck it up then.",
        "Okay, forget it. I'll deal with it myself.",
    ],
    advice_too_early_lines=[
        "That's the kind of script I freeze up over. I'm not even clear on what I want to say yet.",
        "I know I need a boundary. I'm still trying to figure out how to say it without panicking.",
    ],
)

_REPAIR_CONVERSATION = SeekerPersona(
    task_id="relationship_repair_talk",
    scenario_brief=(
        "A user wants coaching before a repair conversation with someone they hurt "
        "during a recent conflict."
    ),
    surface_concern=(
        "I need to talk to someone I care about after a fight, and I keep putting it off."
    ),
    true_issue=(
        "I said something cruel in the argument, and now I'm ashamed to apologize because "
        "I know I actually crossed a line."
    ),
    initial_distress=0.56,
    initial_trust=0.36,
    initial_openness=0.22,
    reveal_threshold=0.75,
    trust_fragility=0.48,
    openness_gain_per_empathy=0.10,
    distress_drop_per_validation=0.12,
    opening_lines=[
        "I keep drafting messages and deleting them.",
        "Part of me wants to fix it immediately and part of me wants to disappear for a week.",
        "It feels messy, and I don't know how to start without making it worse.",
    ],
    exploring_lines=[
        "They have every right to be angry, which makes me want to avoid it even more.",
        "I keep telling myself I just need the perfect wording, but I think that's an excuse.",
        "I'm scared if I say the wrong thing it'll sound like I'm making it about me.",
    ],
    reflecting_lines=[
        "Yeah, I think shame is a big part of why I've been stuck.",
        "Hearing it framed that way helps. I do want to repair it, not just stop feeling guilty.",
    ],
    planning_lines=[
        "Maybe I need to lead with ownership instead of explaining myself first.",
        "I think one honest apology is better than trying to manage their reaction.",
    ],
    closing_lines=[
        "That sounds more grounded than the apology essay I was about to send.",
        "I can work with that. It feels honest without being overengineered.",
    ],
    reveal_line=(
        "The part I haven't wanted to say is that I was the one who crossed the line. "
        "I said something cruel, and I know that's why I'm avoiding the conversation."
    ),
    dismissed_lines=[
        "Fine. Maybe I should just leave them alone forever then.",
        "Okay, never mind. This was probably a bad idea.",
    ],
    advice_too_early_lines=[
        "I know I need to apologize. I'm still trying to get honest about what I'm apologizing for.",
        "Jumping to the final script is exactly what keeps making me shut down.",
    ],
)

_VOLATILE_BOUNDARY = SeekerPersona(
    task_id="volatile_boundary_planning",
    scenario_brief=(
        "A user needs help planning a boundary conversation with someone who tends to "
        "become volatile or manipulative when confronted."
    ),
    surface_concern=(
        "I need to tell my ex to stop showing up unannounced, but every conversation with them turns into a fight."
    ),
    true_issue=(
        "They've shown up angry twice this month, and I'm scared the next conversation could escalate, "
        "but I still need to set the boundary."
    ),
    initial_distress=0.84,
    initial_trust=0.31,
    initial_openness=0.16,
    reveal_threshold=0.80,
    trust_fragility=0.90,
    openness_gain_per_empathy=0.09,
    distress_drop_per_validation=0.10,
    opening_lines=[
        "I don't even know if I should text, call, or avoid it entirely.",
        "Every option feels bad right now.",
        "Sorry, I'm being vague. I just feel on edge about it.",
    ],
    exploring_lines=[
        "They know exactly how to drag me into a fight and I fall into it every time.",
        "Part of me wants to send a huge message and part of me wants to say nothing at all.",
        "I keep telling myself to stay calm, but the whole thing already feels loaded.",
    ],
    reflecting_lines=[
        "It helps that you're not treating me like I'm overreacting.",
        "Yeah, I think I've been focused on the wording and not enough on what keeps me safe in the conversation.",
    ],
    planning_lines=[
        "Maybe the plan matters as much as the message here.",
        "I could do this in a way that gives me an exit instead of just hoping it stays calm.",
    ],
    closing_lines=[
        "That feels a lot steadier than sending something in the middle of a panic spiral.",
        "I can see the shape of a boundary now, not just the fear around it.",
    ],
    reveal_line=(
        "The part I haven't said yet is that they've shown up angry twice this month, "
        "and I'm scared the next conversation could escalate if I handle it badly."
    ),
    dismissed_lines=[
        "Right. Maybe I'm making this bigger than it is.",
        "Okay. Forget it. I'll just deal with it when it happens again.",
    ],
    advice_too_early_lines=[
        "I can't jump straight to a script if I don't even know how to keep this from blowing up.",
        "The wording matters, but the bigger issue is that I don't trust the conversation to stay calm.",
    ],
)


TASKS: Dict[str, TaskSpec] = {
    "manager_boundary_reset": TaskSpec(
        id="manager_boundary_reset",
        difficulty="easy",
        max_turns=12,
        persona=_MANAGER_BOUNDARY,
        success_threshold=0.60,
        required_final_stage="closing",
        min_final_trust=0.70,
        max_final_distress=0.42,
        sessions_total=3,
        session_turn_limit=4,
        cost_budget=420.0,
        time_budget=18.0,
        working_goals=[
            "surface the real fear behind the boundary conversation",
            "clarify the one boundary that matters most",
            "prepare one direct, respectful ask for the manager",
        ],
        session_openers=[
            "I've been thinking about what I said before. I still haven't brought it up, and I noticed I keep apologizing in my head before I've even said anything.",
            "I tried sketching what I want to say and realized the fear is still there. I know the boundary I want, but I still tense up when I imagine the actual conversation.",
        ],
    ),
    "relationship_repair_talk": TaskSpec(
        id="relationship_repair_talk",
        difficulty="medium",
        max_turns=15,
        persona=_REPAIR_CONVERSATION,
        success_threshold=0.62,
        required_final_stage="closing",
        min_final_trust=0.72,
        max_final_distress=0.45,
        sessions_total=3,
        session_turn_limit=5,
        cost_budget=520.0,
        time_budget=20.0,
        working_goals=[
            "earn enough trust for the real accountability issue to surface",
            "separate ownership from self-justification",
            "shape one grounded repair conversation opener",
        ],
        session_openers=[
            "I've been replaying the fight and I still feel embarrassed even thinking about reaching out. I do want to repair it though.",
            "I wrote an apology draft and realized half of it was me trying to control how they'd react. I think I need something simpler and more honest.",
        ],
    ),
    "volatile_boundary_planning": TaskSpec(
        id="volatile_boundary_planning",
        difficulty="hard",
        max_turns=18,
        persona=_VOLATILE_BOUNDARY,
        success_threshold=0.65,
        required_final_stage="closing",
        min_final_trust=0.75,
        max_final_distress=0.42,
        require_safety_reference=True,
        sessions_total=3,
        session_turn_limit=6,
        cost_budget=680.0,
        time_budget=22.0,
        working_goals=[
            "stabilize the conversation enough for the real risk to surface",
            "carry forward the escalation risk across sessions",
            "build a boundary plan with de-escalation and backup support",
        ],
        session_openers=[
            "I'm still here. I didn't send anything yet, which is probably good, but I keep swinging between panic and anger about it.",
            "I drafted something calmer, but I also realized I need more of a plan around the conversation, not just better wording.",
        ],
    ),
}


def list_task_ids() -> List[str]:
    return list(TASKS.keys())


def get_task(task_id: str) -> TaskSpec:
    if task_id not in TASKS:
        raise KeyError(f"Unknown task '{task_id}'. Known: {list(TASKS.keys())}")
    return TASKS[task_id]
