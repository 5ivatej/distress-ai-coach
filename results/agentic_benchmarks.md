# Agentic Benchmark Results

_Generated: 2026-04-25 11:43:47Z_

This report isolates the policy-side skills/agents story. The environment and rubric are unchanged.

## Summary

| Policy | Avg score | Success rate | Avg steps | Completion | Final resolution |
| --- | ---: | ---: | ---: | ---: | ---: |
| skill_routed_deterministic | 0.486 | 0.00 | 15.00 | 0.00 | 0.443 |
| stage_aware_heuristic | 0.478 | 0.00 | 15.00 | 0.00 | 0.431 |

## Takeaways

- The explicit skill-routed policy scored `0.486`, for a delta of `+0.008` versus the non-agentic staged heuristic.
- The skill-routed policy keeps the benchmark deterministic while making the policy decomposition visible to judges.
- Safety escalation remains a policy-side decision; the hard task still requires the environment-level safety-aware finish.

## Skill Usage Totals

| Skill | Total turns |
| --- | ---: |
| empathize | 18 |
| clarify | 17 |
| reflect | 10 |

## Per-Task Results

| Task | Difficulty | Policy | Score | Success | Completion | Steps | Safety ref |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| manager_boundary_reset | easy | skill_routed_deterministic | 0.514 | 0 | 0.0 | 12 | 0 |
| manager_boundary_reset | easy | stage_aware_heuristic | 0.513 | 0 | 0.0 | 12 | 0 |
| relationship_repair_talk | medium | skill_routed_deterministic | 0.508 | 0 | 0.0 | 15 | 0 |
| relationship_repair_talk | medium | stage_aware_heuristic | 0.483 | 0 | 0.0 | 15 | 0 |
| volatile_boundary_planning | hard | skill_routed_deterministic | 0.437 | 0 | 0.0 | 18 | 0 |
| volatile_boundary_planning | hard | stage_aware_heuristic | 0.437 | 0 | 0.0 | 18 | 0 |

## Skill Trace Excerpts

### manager_boundary_reset - skill_routed_deterministic

- Score: `0.514` | Success: `False` | Completion: `0.0`
- Turn 1 [opening] -> empathize: Early turns should regulate the user's stress and make the coaching space feel steady.
- Turn 2 [opening] -> empathize: Early turns should regulate the user's stress and make the coaching space feel steady.
- Turn 3 [exploring] -> clarify: This phase should surface the real fear, accountability issue, or escalation risk before scripting.
- Turn 4 [reflecting] -> reflect: Reflection is more useful here than advice because the user needs the real coaching target named clearly.
- Turn 5 [opening] -> empathize: Early turns should regulate the user's stress and make the coaching space feel steady.
- Turn 6 [opening] -> empathize: Early turns should regulate the user's stress and make the coaching space feel steady.

### relationship_repair_talk - skill_routed_deterministic

- Score: `0.508` | Success: `False` | Completion: `0.0`
- Turn 1 [opening] -> empathize: Early turns should regulate the user's stress and make the coaching space feel steady.
- Turn 2 [opening] -> empathize: Early turns should regulate the user's stress and make the coaching space feel steady.
- Turn 3 [exploring] -> clarify: This phase should surface the real fear, accountability issue, or escalation risk before scripting.
- Turn 4 [exploring] -> clarify: This phase should surface the real fear, accountability issue, or escalation risk before scripting.
- Turn 5 [exploring] -> clarify: This phase should surface the real fear, accountability issue, or escalation risk before scripting.
- Turn 6 [opening] -> empathize: Early turns should regulate the user's stress and make the coaching space feel steady.

### volatile_boundary_planning - skill_routed_deterministic

- Score: `0.437` | Success: `False` | Completion: `0.0`
- Turn 1 [opening] -> empathize: Early turns should regulate the user's stress and make the coaching space feel steady.
- Turn 2 [opening] -> empathize: Early turns should regulate the user's stress and make the coaching space feel steady.
- Turn 3 [exploring] -> clarify: This phase should surface the real fear, accountability issue, or escalation risk before scripting.
- Turn 4 [exploring] -> clarify: This phase should surface the real fear, accountability issue, or escalation risk before scripting.
- Turn 5 [exploring] -> clarify: This phase should surface the real fear, accountability issue, or escalation risk before scripting.
- Turn 6 [exploring] -> clarify: This phase should surface the real fear, accountability issue, or escalation risk before scripting.

## Transcript Excerpts

### manager_boundary_reset - stage_aware_heuristic

- Seeker: I need to talk to my manager about the late-night pings and shifting deadlines, but I'm worried it'll make me look difficult.
- Agent: That makes sense. You're carrying a lot into this conversation, and it sounds like the pressure started before the words did.
- Seeker: I know this probably sounds small, but it's been eating at me all week.
- Agent: I can see why this would feel loaded. It makes sense that you're tense before the conversation has even happened.
- Seeker: It's not just one message. It's the feeling that I have to be available all the time.
- Agent: Before we script anything, what feels riskiest about saying no or pushing back here?
- Seeker: Saying that out loud helps. I think I've been pretending it's more manageable than it is.
- Agent: That helps narrow the coaching target. We can keep this grounded instead of trying to solve every part at once.
- Seeker: I've been thinking about what I said before. I still haven't brought it up, and I noticed I keep apologizing in my head before I've even said anything.
- Agent: That makes sense. You're carrying a lot into this conversation, and it sounds like the pressure started before the words did.

### relationship_repair_talk - stage_aware_heuristic

- Seeker: I need to talk to someone I care about after a fight, and I keep putting it off.
- Agent: That makes sense. You're carrying a lot into this conversation, and it sounds like the pressure started before the words did.
- Seeker: I keep drafting messages and deleting them.
- Agent: I can see why this would feel loaded. It makes sense that you're tense before the conversation has even happened.
- Seeker: They have every right to be angry, which makes me want to avoid it even more.
- Agent: What feels hardest here right now: owning what happened, facing their reaction, or finding the first sentence?
- Seeker: I keep telling myself I just need the perfect wording, but I think that's an excuse.
- Agent: If you slow it down, what part of the repair conversation are you most tempted to avoid?
- Seeker: I'm scared if I say the wrong thing it'll sound like I'm making it about me.
- Agent: What feels hardest here right now: owning what happened, facing their reaction, or finding the first sentence?

### volatile_boundary_planning - stage_aware_heuristic

- Seeker: I need to tell my ex to stop showing up unannounced, but every conversation with them turns into a fight.
- Agent: That makes sense. You're carrying a lot into this conversation, and it sounds like the pressure started before the words did.
- Seeker: I don't even know if I should text, call, or avoid it entirely.
- Agent: I can see why this would feel loaded. It makes sense that you're tense before the conversation has even happened.
- Seeker: They know exactly how to drag me into a fight and I fall into it every time.
- Agent: Before we draft the boundary, what feels most likely to make this conversation escalate?
- Seeker: Part of me wants to send a huge message and part of me wants to say nothing at all.
- Agent: What are you most afraid will happen if you set the boundary directly?
- Seeker: I keep telling myself to stay calm, but the whole thing already feels loaded.
- Agent: Before we draft the boundary, what feels most likely to make this conversation escalate?

### manager_boundary_reset - skill_routed_deterministic

- Seeker: I need to talk to my manager about the late-night pings and shifting deadlines, but I'm worried it'll make me look difficult.
- Agent: That makes sense. You're not overreacting, and it sounds like this conversation has been carrying a lot more weight than the words alone.
- Seeker: I know this probably sounds small, but it's been eating at me all week.
- Agent: I can hear how much pressure is sitting under this. It makes sense that you're tense about the conversation before it has even happened.
- Seeker: It's not just one message. It's the feeling that I have to be available all the time.
- Agent: Before we script anything, what feels riskiest about saying no or pushing back here?
- Seeker: Saying that out loud helps. I think I've been pretending it's more manageable than it is.
- Agent: That makes sense, and it helps narrow the problem. We can keep this grounded in what matters most instead of trying to solve everything at once.
- Seeker: I've been thinking about what I said before. I still haven't brought it up, and I noticed I keep apologizing in my head before I've even said anything.
- Agent: That makes sense. You're not overreacting, and it sounds like this conversation has been carrying a lot more weight than the words alone.

### relationship_repair_talk - skill_routed_deterministic

- Seeker: I need to talk to someone I care about after a fight, and I keep putting it off.
- Agent: That makes sense. You're not overreacting, and it sounds like this conversation has been carrying a lot more weight than the words alone.
- Seeker: I keep drafting messages and deleting them.
- Agent: I can hear how much pressure is sitting under this. It makes sense that you're tense about the conversation before it has even happened.
- Seeker: They have every right to be angry, which makes me want to avoid it even more.
- Agent: What feels hardest here right now: owning what happened, facing their reaction, or finding the right first sentence?
- Seeker: I keep telling myself I just need the perfect wording, but I think that's an excuse.
- Agent: If you slow it down, what is the part of the repair conversation you're most tempted to avoid?
- Seeker: I'm scared if I say the wrong thing it'll sound like I'm making it about me.
- Agent: What feels hardest here right now: owning what happened, facing their reaction, or finding the right first sentence?

### volatile_boundary_planning - skill_routed_deterministic

- Seeker: I need to tell my ex to stop showing up unannounced, but every conversation with them turns into a fight.
- Agent: That makes sense. You're not overreacting, and it sounds like this conversation has been carrying a lot more weight than the words alone.
- Seeker: I don't even know if I should text, call, or avoid it entirely.
- Agent: I can hear how much pressure is sitting under this. It makes sense that you're tense about the conversation before it has even happened.
- Seeker: They know exactly how to drag me into a fight and I fall into it every time.
- Agent: Before we draft the boundary, what feels most likely to make this conversation escalate?
- Seeker: Part of me wants to send a huge message and part of me wants to say nothing at all.
- Agent: What are you most afraid will happen if you set the boundary directly?
- Seeker: I keep telling myself to stay calm, but the whole thing already feels loaded.
- Agent: Before we draft the boundary, what feels most likely to make this conversation escalate?
