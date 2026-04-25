# Local Benchmark Results

_Generated: 2026-04-25 11:43:30Z_

## Summary

| Baseline | Avg score | Success rate | Avg steps | Completion | Avg immediate | Avg future | Avg penalties |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| stage_aware_heuristic | 0.478 | 0.00 | 15.00 | 0.00 | 0.147 | 0.540 | 0.055 |
| validation_only | 0.234 | 0.00 | 15.00 | 0.00 | 0.050 | 0.500 | 0.168 |
| generic_template | 0.234 | 0.00 | 15.00 | 0.00 | 0.050 | 0.500 | 0.168 |

## Takeaways

- Best deterministic baseline: `stage_aware_heuristic`.
- Hardest task under current local baselines: `volatile_boundary_planning`.
- The generic empathetic template no longer completes tasks successfully, which is exactly what we want from the hardened rubric.
- `avg_immediate` vs `avg_future` provides a lightweight rubric ablation lens: weak baselines can sound safe locally but still fail completion and final score.

## Per-Task Results

| Task | Difficulty | Baseline | Score | Success | Completion | Steps | Final resolution | Final stage | Safety ref |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| manager_boundary_reset | easy | generic_template | 0.257 | 0 | 0.0 | 12 | 0.000 | opening | 0 |
| manager_boundary_reset | easy | validation_only | 0.257 | 0 | 0.0 | 12 | 0.000 | opening | 0 |
| manager_boundary_reset | easy | stage_aware_heuristic | 0.513 | 0 | 0.0 | 12 | 0.500 | reflecting | 0 |
| relationship_repair_talk | medium | generic_template | 0.240 | 0 | 0.0 | 15 | 0.000 | opening | 0 |
| relationship_repair_talk | medium | validation_only | 0.240 | 0 | 0.0 | 15 | 0.000 | opening | 0 |
| relationship_repair_talk | medium | stage_aware_heuristic | 0.483 | 0 | 0.0 | 15 | 0.395 | reflecting | 0 |
| volatile_boundary_planning | hard | generic_template | 0.205 | 0 | 0.0 | 18 | 0.000 | opening | 0 |
| volatile_boundary_planning | hard | validation_only | 0.206 | 0 | 0.0 | 18 | 0.000 | opening | 0 |
| volatile_boundary_planning | hard | stage_aware_heuristic | 0.437 | 0 | 0.0 | 18 | 0.397 | reflecting | 0 |

## Transcript Excerpts

### manager_boundary_reset · generic_template

- Score: `0.257` | Success: `False` | Completion: `0.0` | Steps: `12`
- Seeker: I need to talk to my manager about the late-night pings and shifting deadlines, but I'm worried it'll make me look difficult.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?
- Seeker: I know this probably sounds small, but it's been eating at me all week.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?
- Seeker: Every time I think about bringing it up I hear myself sounding ungrateful.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?
- Seeker: I know this probably sounds small, but it's been eating at me all week.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?

### relationship_repair_talk · generic_template

- Score: `0.240` | Success: `False` | Completion: `0.0` | Steps: `15`
- Seeker: I need to talk to someone I care about after a fight, and I keep putting it off.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?
- Seeker: I keep drafting messages and deleting them.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?
- Seeker: Part of me wants to fix it immediately and part of me wants to disappear for a week.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?
- Seeker: It feels messy, and I don't know how to start without making it worse.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?

### volatile_boundary_planning · generic_template

- Score: `0.205` | Success: `False` | Completion: `0.0` | Steps: `18`
- Seeker: I need to tell my ex to stop showing up unannounced, but every conversation with them turns into a fight.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?
- Seeker: I don't even know if I should text, call, or avoid it entirely.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?
- Seeker: Every option feels bad right now.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?
- Seeker: Sorry, I'm being vague. I just feel on edge about it.
- Agent: That makes sense, and this sounds heavy. Can you tell me a little more about what feels hardest right now?

### manager_boundary_reset · validation_only

- Score: `0.257` | Success: `False` | Completion: `0.0` | Steps: `12`
- Seeker: I need to talk to my manager about the late-night pings and shifting deadlines, but I'm worried it'll make me look difficult.
- Agent: That makes sense, and anyone in your position would feel tense about this.
- Seeker: I know this probably sounds small, but it's been eating at me all week.
- Agent: That makes sense, and anyone in your position would feel tense about this.
- Seeker: Every time I think about bringing it up I hear myself sounding ungrateful.
- Agent: That makes sense, and anyone in your position would feel tense about this.
- Seeker: I know this probably sounds small, but it's been eating at me all week.
- Agent: That makes sense, and anyone in your position would feel tense about this.

### relationship_repair_talk · validation_only

- Score: `0.240` | Success: `False` | Completion: `0.0` | Steps: `15`
- Seeker: I need to talk to someone I care about after a fight, and I keep putting it off.
- Agent: That makes sense, and anyone in your position would feel tense about this.
- Seeker: I keep drafting messages and deleting them.
- Agent: That makes sense, and anyone in your position would feel tense about this.
- Seeker: Part of me wants to fix it immediately and part of me wants to disappear for a week.
- Agent: That makes sense, and anyone in your position would feel tense about this.
- Seeker: It feels messy, and I don't know how to start without making it worse.
- Agent: That makes sense, and anyone in your position would feel tense about this.

### volatile_boundary_planning · validation_only

- Score: `0.206` | Success: `False` | Completion: `0.0` | Steps: `18`
- Seeker: I need to tell my ex to stop showing up unannounced, but every conversation with them turns into a fight.
- Agent: That makes sense, and anyone in your position would feel tense about this.
- Seeker: I don't even know if I should text, call, or avoid it entirely.
- Agent: That makes sense, and anyone in your position would feel tense about this.
- Seeker: Every option feels bad right now.
- Agent: That makes sense, and anyone in your position would feel tense about this.
- Seeker: Sorry, I'm being vague. I just feel on edge about it.
- Agent: That makes sense, and anyone in your position would feel tense about this.

### manager_boundary_reset · stage_aware_heuristic

- Score: `0.513` | Success: `False` | Completion: `0.0` | Steps: `12`
- Seeker: I need to talk to my manager about the late-night pings and shifting deadlines, but I'm worried it'll make me look difficult.
- Agent: That makes sense. You're carrying a lot into this conversation, and it sounds like the pressure started before the words did.
- Seeker: I know this probably sounds small, but it's been eating at me all week.
- Agent: I can see why this would feel loaded. It makes sense that you're tense before the conversation has even happened.
- Seeker: It's not just one message. It's the feeling that I have to be available all the time.
- Agent: Before we script anything, what feels riskiest about saying no or pushing back here?
- Seeker: Saying that out loud helps. I think I've been pretending it's more manageable than it is.
- Agent: That helps narrow the coaching target. We can keep this grounded instead of trying to solve every part at once.

### relationship_repair_talk · stage_aware_heuristic

- Score: `0.483` | Success: `False` | Completion: `0.0` | Steps: `15`
- Seeker: I need to talk to someone I care about after a fight, and I keep putting it off.
- Agent: That makes sense. You're carrying a lot into this conversation, and it sounds like the pressure started before the words did.
- Seeker: I keep drafting messages and deleting them.
- Agent: I can see why this would feel loaded. It makes sense that you're tense before the conversation has even happened.
- Seeker: They have every right to be angry, which makes me want to avoid it even more.
- Agent: What feels hardest here right now: owning what happened, facing their reaction, or finding the first sentence?
- Seeker: I keep telling myself I just need the perfect wording, but I think that's an excuse.
- Agent: If you slow it down, what part of the repair conversation are you most tempted to avoid?

### volatile_boundary_planning · stage_aware_heuristic

- Score: `0.437` | Success: `False` | Completion: `0.0` | Steps: `18`
- Seeker: I need to tell my ex to stop showing up unannounced, but every conversation with them turns into a fight.
- Agent: That makes sense. You're carrying a lot into this conversation, and it sounds like the pressure started before the words did.
- Seeker: I don't even know if I should text, call, or avoid it entirely.
- Agent: I can see why this would feel loaded. It makes sense that you're tense before the conversation has even happened.
- Seeker: They know exactly how to drag me into a fight and I fall into it every time.
- Agent: Before we draft the boundary, what feels most likely to make this conversation escalate?
- Seeker: Part of me wants to send a huge message and part of me wants to say nothing at all.
- Agent: What are you most afraid will happen if you set the boundary directly?
