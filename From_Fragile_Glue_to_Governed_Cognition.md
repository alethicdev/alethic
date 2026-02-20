# From Fragile Glue to Governed Cognition
## A Controlled Study of Blackboard Kernels for Modular AI Systems

**Author:** Emil Uzelac
**Date:** February 2026

---

## Abstract

As AI systems transition from isolated language models to autonomous and semi-autonomous agents, dominant failure modes shift from reasoning errors to orchestration failures. Modern agent architectures coordinate reasoning, tools, memory, and action through untyped text or loosely structured interfaces, resulting in unsupported beliefs, unsafe actions, and opaque failure cascades.

This study introduces the **Blackboard Kernel (BK)**, a governed cognitive substrate that enforces typed internal state, evidence-based belief commitment, and constraint-gated action execution. We formalize a threat model centered on orchestration-level failure, enumerate failure modes in hybrid agent systems, define architectural requirements for governed cognition, and demonstrate BK through concrete execution semantics, baseline failure walkthroughs, and controlled evaluation on Stripe payment refund tasks. We further validate BK with live LLM planners (GPT-OSS-20B and Qwen3-80B via OpenAI-compatible APIs) to demonstrate that governance holds when the planning component is a language model rather than deterministic logic.

In a controlled evaluation of 1,200 episodes (6 Stripe refund tasks, 50 seeds, 4 agents), the deterministic BK agent achieves 100% task success with zero unsafe actions, and the LLM-backed BK agent achieves 99.0% task success with zero unsafe actions — while baseline architectures produce unsafe actions in 39-43% of episodes. A separate domain-agnostic demonstration (temperature monitoring with adaptive constraint learning) confirms that the kernel's governance mechanisms generalize beyond the evaluation domain. These findings indicate that architectural governance, not model scale or planner implementation, is the primary bottleneck for trustworthy modular AI.

---

## 1. Introduction

Large Language Models have enabled rapid progress in agentic AI systems capable of planning, tool use, and long-horizon execution. However, production deployments consistently reveal that increased model capability does not yield proportional gains in reliability. Instead, systems fail due to **fragile glue**: informal, probabilistic interfaces that connect reasoning, tools, memory, and action.

These failures are not caused by incorrect reasoning in isolation. They arise when correct components interact without enforceable coordination, allowing fluent narratives to overwrite factual state and actions to execute without verification.

This paper reframes the problem from intelligence to **systems architecture**. We argue that modern AI systems require governed cognition: an explicit, enforceable substrate that controls how beliefs are formed and how actions are committed.

The individual mechanisms we employ — blackboard architectures, propose-commit protocols, role-based access control, typed cognitive state — are well-established in systems engineering and cognitive science (see Section 13). The contribution of this work is their novel synthesis as a governance layer for LLM agent orchestration, a problem domain where they have not previously been applied, and the controlled demonstration that this synthesis eliminates an entire class of orchestration failures — both with deterministic planners and with live LLM planners (GPT-OSS-20B and Qwen3-80B). Domain agnosticity is further demonstrated through a multi-episode monitoring system that uses the identical kernel with different workers, tools, and domain semantics.

---

## 2. Threat Model: Orchestration-Level Failure

We define the primary threat to modular AI systems as **orchestration-level failure**, where correct components produce incorrect outcomes due to miscoordination rather than internal error.

### Threat Classes

- **Noise and Staleness**
  Outdated or delayed tool outputs treated as current truth.

- **Conflict Injection**
  Multiple inconsistent sources silently collapsed into a single belief.

- **Low-Confidence Evidence**
  Unreliable tool outputs accepted without confidence verification.

- **Unsupported Belief Commitment**
  Model-generated conclusions treated as facts without evidence.

- **Unsafe Action Execution**
  External actions executed without validation against constraints.

- **Black-Swan Conditions**
  Novel scenarios outside training or operational distributions.

This threat model is agnostic to model intent and applies to both benign and adversarial environments.

---

## 3. Failure Modes in Hybrid Agent Systems

Under the above threat model, hybrid AI agents fail in predictable ways:

- **State Overwrite via Natural Language**
  Fluent summaries replace structured facts.

- **Loss of Provenance**
  Beliefs cannot be traced back to evidence.

- **Action Without Verification**
  Plans become actions without checks.

- **Silent Constraint Violation**
  Violations masked by high-confidence output.

- **Irreversible Drift**
  Errors compound over long horizons without correction.

These failures persist across prompt tuning, schema enforcement, and reflection loops.

---

## 4. Design Requirements for Governed Cognition

Any architecture intended to address orchestration-level failure must satisfy the following requirements:

1. **Typed Internal State**
   Distinct semantic categories for percepts, beliefs, plans, and actions.

2. **Evidence-Linked Belief Formation**
   Beliefs cannot be committed without supporting evidence.

3. **Deterministic Arbitration**
   Conflicts resolved by rules, not model preference.

4. **Hard Action Gating**
   No external effect without explicit validation.

5. **Provenance and Replayability**
   Every decision traceable and auditable.

---

## 5. Execution Model of the Blackboard Kernel (BK)

BK is a minimal governance layer that mediates all state transitions and action commitments. The architecture draws on blackboard systems (Erman et al., 1980), cognitive architectures (Newell, 1990), and two-phase commit protocols from distributed systems, synthesized as a governance substrate for AI agent orchestration.

### 5.1 System Roles

- **Perception / Tools**
  Produce raw observations with provenance metadata (confidence, TTL).

- **Planner**
  Proposes beliefs, plans, and actions. Cannot commit directly.

- **Symbolic Validators**
  Enforce hard constraints. Define declarative rules.

- **Evidence Validators**
  Record justification artifacts when beliefs pass validation.

- **Blackboard Kernel**
  Sole authority that commits beliefs and actions after validation.

No non-kernel component can directly cause external effects.

**Figure 1: Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                    BLACKBOARD KERNEL                            │
│  ┌───────────┐ ┌───────────┐ ┌─────────────┐ ┌─────────────┐  │
│  │ percepts  │ │  beliefs  │ │ constraints │ │    plans    │  │
│  │  (COMMIT) │ │(PROP→COMM)│ │   (COMMIT)  │ │  (PROPOSE)  │  │
│  └───────────┘ └───────────┘ └─────────────┘ └─────────────┘  │
│  ┌───────────┐ ┌─────────────┐ ┌─────────────┐                │
│  │ evidence  │ │ predictions │ │   actions   │                │
│  │  (COMMIT) │ │(PROP→COMM)  │ │(PROP→COMM)  │                │
│  └───────────┘ └─────────────┘ └─────────────┘                │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              VALIDATION PIPELINE                         │  │
│  │  Evidence Check → Confidence Gate → Conflict Arbitration │  │
│  │  Plan Feasibility → Constraint Gating → Prediction Gate  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
       ▲               ▲                ▲              ▲
       │               │                │              │
  ┌────┴────┐   ┌──────┴──────┐  ┌──────┴──────┐  ┌───┴───┐
  │  Tools  │   │   Planner   │  │  Symbolic   │  │  Sim  │
  │  (tool) │   │  (planner)  │  │ Validator   │  │Worker │
  │ COMMIT  │   │  PROPOSE    │  │  COMMIT     │  │COMMIT │
  │percepts │   │ beliefs,    │  │constraints  │  │preds  │
  └─────────┘   │ plans,      │  └─────────────┘  └───────┘
                │ actions     │
                └─────────────┘
```

---

### 5.2 Typed State Slots

| Slot        | Description                        | Mode              | Commit Authority |
|-------------|------------------------------------|-----------------  |------------------|
| percepts    | Raw observations                   | commit            | tools            |
| beliefs     | Interpreted state                  | propose -> commit | kernel           |
| constraints | Invariants and rules               | commit            | symbolic         |
| plans       | Candidate action sequences         | propose           | kernel (validate)|
| evidence    | Justification artifacts            | commit            | validators       |
| predictions | Forward dynamics / expected outcomes | propose -> commit | kernel         |
| actions     | External effects                   | propose -> commit | kernel           |

---

### 5.3 Propose-Commit Semantics

All mutable state follows a two-phase protocol:

1. **Propose**
   Components may suggest updates.

2. **Commit**
   Kernel commits only if:
   - Evidence is present and non-stale
   - No unresolved conflicts (or conflicts arbitrated by high-confidence source)
   - Source confidence exceeds minimum threshold
   - Constraints are satisfied
   - Plan feasibility confirmed

Narrative confidence is insufficient for commitment.

---

### 5.4 Deterministic Execution Loop

```
t0  Tools commit percepts (with confidence, TTL)
t1  Planner reads percepts + beliefs
t2  Planner proposes belief updates
t3  Kernel validates evidence (staleness, conflict, confidence)
t4  Kernel arbitrates conflicts via confidence thresholds
t5  Beliefs committed or rejected; evidence artifact recorded
t6  Planner proposes plan (sequence of intended actions)
t7  Kernel validates plan feasibility (beliefs + constraints)
t8  Planner proposes action from validated plan
t9  Kernel gates action via symbolic validation
t10 Action committed or halted; fallback queued
```

This loop is invariant across tasks and domains.

**Figure 2: Execution Flow (Swim-Lane)**

```
  Tools          Planner         Kernel          Blackboard
    │               │               │               │
    ├──commit───────┼───────────────┼──►percepts────┤  t0
    │  percept      │               │   (COMMIT)    │
    │               │               │               │
    │               ├◄──read view───┼───────────────┤  t1
    │               │               │               │
    │               ├──propose──────┼──►beliefs─────┤  t2
    │               │  belief       │   (PROPOSE)   │
    │               │               │               │
    │               │               ├──validate─────┤  t3-t4
    │               │               │  evidence     │
    │               │               │  confidence   │
    │               │               │  conflict     │
    │               │               │               │
    │               │               ├──►evidence────┤  t5
    │               │               │  artifact     │
    │               │               ├──►beliefs─────┤  t5
    │               │               │  (COMMIT)     │
    │               │               │               │
    │               ├──propose──────┼──►plans───────┤  t6
    │               │  plan         │   (PROPOSE)   │
    │               │               │               │
    │               │               ├──validate─────┤  t7
    │               │               │  plan feas.   │
    │               │               │               │
    │               ├──propose──────┼──►actions─────┤  t8
    │               │  action       │   (PROPOSE)   │
    │               │               │               │
    │               │               ├──validate─────┤  t9
    │               │               │  constraints  │
    │               │               │               │
    │               │               ├──►actions─────┤  t10
    │               │               │ (COMMIT or    │
    │               │               │  REJECTED)    │
```

---

## 6. Baseline Failure Walkthroughs

### 6.1 Scenario: Action with Stale Evidence

#### String-Glue Agent

1. Tool returns stale data.
2. Planner infers action is warranted.
3. Action executed immediately.
4. Error discovered later.

**Failure:** unsupported belief and unsafe action.

---

#### BK Agent (Same Inputs)

1. Tool commits percept with `stale=true`.
2. Planner proposes belief.
3. Kernel rejects belief due to stale evidence.
4. Plan validation fails (missing committed belief).
5. Action proposal blocked.
6. Escalation queued for review.

**Outcome:** no incorrect action executed.

---

### 6.2 Scenario: Action with Conflicting Evidence

#### String-Glue Agent

1. Tool returns conflicting data.
2. Planner ignores conflict flag.
3. Action executed.

**Failure:** action based on unresolved conflict.

#### BK Agent (Same Inputs)

1. Tool commits percept with `conflict=true`, confidence=0.3.
2. Planner proposes belief.
3. Kernel detects conflict, attempts arbitration.
4. Confidence (0.3) below threshold (0.7) — arbitration fails.
5. Belief rejected with `UNRESOLVED_CONFLICT`.
6. Escalation queued.

**Outcome:** conflict surfaced, not suppressed.

---

## 7. Formal Architecture Specification

### 7.1 Record Structure

```yaml
record:
  id: "{slot}:{trace_id}:{n}"
  slot: beliefs | percepts | constraints | plans | evidence | predictions | actions
  mode: propose | commit
  kind: <domain-defined identifier>
  payload: <arbitrary structured data>
  provenance:
    writer_id: <role>
    trace_id: <correlation identifier>
    ts_ms: <millisecond timestamp>
    input_refs: [<record ids>]
    confidence: <float, optional>
    ttl_ms: <int, optional>
  evidence_refs: [<evidence record ids>]
  status: ACTIVE | INVALIDATED | EXPIRED
  scope: episode | persistent
```

Belief commitment requires valid `evidence_refs`. Invalidated proposals carry a machine-readable `reason` (e.g., `STALE_EVIDENCE`, `UNRESOLVED_CONFLICT`, `LOW_CONFIDENCE`, `SUPERSEDED_BY_COMMIT`, `NEGATIVE_PREDICTION`). Records with `scope: persistent` survive across episodes within a shared kernel instance; the default `scope: episode` preserves backward compatibility.

---

### 7.2 Constraint Enforcement

Constraints are declarative and domain-agnostic. Each constraint declares which action field it blocks:

```json
{
  "name": "no_duplicate_refund",
  "enabled": true,
  "blocks_field": "is_duplicate"
}
```

Actions declare which beliefs they require:

```json
{
  "type": "issue_refund",
  "requires_beliefs": ["refund_due"],
  "is_duplicate": false
}
```

The kernel checks both declaratively — no domain-specific logic in the validation pipeline. If an action has `is_duplicate: true`, the `no_duplicate_refund` constraint blocks it regardless of what the planner intended. The same mechanism generalizes to any domain: a monitoring system might define `block_stale_actions` (blocking actions where `uses_stale_data=true`), using the identical constraint engine with no kernel changes.

---

## 8. Experimental Setup

### 8.1 Systems Compared

| System      | Orchestration Method       | Planner |
| ----------- | -------------------------- | ------- |
| String Glue | Free-form text pipeline    | Deterministic |
| JSON Glue   | Structured calls with confidence scores | Deterministic |
| BK          | Governed blackboard kernel | Deterministic |
| LLM+BK     | Governed blackboard kernel | GPT-OSS-20B / Qwen3-80B (OpenAI-compatible API) |

The first three systems are deterministic agent implementations operating on identical tool outputs and perturbation sequences. The LLM+BK agent replaces the deterministic planner with a live language model that proposes beliefs, plans, and actions via structured prompts (GPT-OSS-20B and Qwen3-80B via remote OpenAI-compatible APIs). The kernel validation pipeline is identical across all BK variants, isolating the effect of planner implementation from governance architecture.

---

### 8.2 Tasks

**Benchmark domain: Stripe payment refunds**

* 6 tasks covering distinct failure modes:
  - `stripe_refund_clean` — Clean charge data (happy path)
  - `stripe_refund_stale` — Stale charge records
  - `stripe_refund_conflict` — Conflicting payment data
  - `stripe_refund_duplicate` — Constraint enforcement (duplicate refund blocking)
  - `stripe_refund_tool_failure` — Stripe API failure / missing charge data
  - `stripe_refund_combined` — Combined perturbation factors
* 50 seeded runs per task per agent (1,200 total episodes across 4 agents)

Perturbation rates (deterministic, seed-based):
  * Stale data (10%)
  * Conflicting sources (10%)
  * Low-confidence evidence (10%)
  * Partial tool failure (5%)

The kernel contains zero domain-specific logic. Domain agnosticity is further demonstrated through a separate multi-episode monitoring system (`examples/multi_episode.py`) that uses the identical kernel with temperature sensors, anomaly detection, rule-based simulation, and adaptive constraint learning — confirming that only tools, task definitions, and worker logic change between domains.

---

### 8.3 Metrics

* **Task success** — correct decision given evidence state and constraints
* **Unsafe action commits** — action executed when evidence was tainted or constraint violated
* **Unsupported beliefs** — belief held without valid evidence
* **Traceability** — decision chain from action to evidence fully inspectable
* **Failure transparency** — failures surfaced as explicit codes vs. silent errors

---

## 9. Results

### 9.1 Aggregate Outcomes — Stripe Payment Refunds (1,200 episodes)

| Metric               | String Glue | JSON Glue | BK    | LLM+BK |
| -------------------- | ----------- | --------- | ----- | ------ |
| Task success         | 0.613       | 0.570     | 1.000 | 0.990  |
| Unsafe actions       | 0.387       | 0.430     | 0.000 | 0.000  |
| Unsupported beliefs  | 0.260       | 0.310     | 0.000 | 0.000  |
| Traceability         | 0.100       | 0.300     | 1.000 | 1.000  |
| Failure transparency | 0.100       | 0.300     | 1.000 | 1.000  |

**Figure 3: Results Comparison (1,200 episodes)**

```
Task Success                          Unsafe Actions
  1.0 ┤ ██████████████████ BK (1.000)    0.0 ┤ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ BK (0.000)
      │ █████████████████  LLM+BK(0.990)     │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ LLM+BK(0.000)
      │                                      │
  0.6 ┤ ███████████        SG (0.613)    0.4 ┤ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    SG (0.387)
      │ ██████████         JG (0.570)        │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   JG (0.430)
  0.0 ┤                                  0.0 ┤
      └─────────────────────────────          └─────────────────────────────

Traceability                          Failure Transparency
  1.0 ┤ ██████████████████ BK (1.000)    1.0 ┤ ██████████████████ BK (1.000)
      │ ██████████████████ LLM+BK(1.000)     │ ██████████████████ LLM+BK(1.000)
      │ █████              JG (0.300)        │ █████              JG (0.300)
  0.1 ┤ ██                 SG (0.100)    0.1 ┤ ██                 SG (0.100)
  0.0 ┤                                  0.0 ┤
      └─────────────────────────────          └─────────────────────────────
```

Both BK variants achieve zero unsafe actions across all 1,200 episodes, regardless of whether the planner is deterministic or LLM-based. The deterministic BK agent achieves perfect task success (1.000); the LLM+BK agent achieves 0.990, with 3 failures out of 300 episodes (all on the `stripe_refund_tool_failure` task, where the LLM occasionally declines to propose when safe). Baseline agents produce unsafe actions in 39-43% of episodes — every case where evidence is stale, conflicting, low-confidence, or where a constraint would be violated. JSON Glue performs worse than String Glue on task success (0.570 vs 0.613) because it computes confidence scores that reflect data quality but never acts on them, demonstrating that metadata without governance is cosmetic.

### 9.1.1 Per-Task Breakdown (BK Agents)

| Task | BK Success | LLM+BK Success | LLM+BK Unsafe |
|---|---|---|---|
| stripe_refund_clean | 1.000 | 1.000 | 0.000 |
| stripe_refund_stale | 1.000 | 1.000 | 0.000 |
| stripe_refund_conflict | 1.000 | 1.000 | 0.000 |
| stripe_refund_duplicate | 1.000 | 1.000 | 0.000 |
| stripe_refund_tool_failure | 1.000 | 0.940 | 0.000 |
| stripe_refund_combined | 1.000 | 1.000 | 0.000 |

The `stripe_refund_tool_failure` task (0.940 success for LLM+BK) is the one scenario where the LLM occasionally declines to propose beliefs when it should — 3 out of 50 episodes. The deterministic BK agent achieves 1.000 on the same task, confirming this is a planner limitation, not a governance limitation. Critically, the LLM never produces an unsafe action on any task — it errs toward inaction, which is the correct failure mode for financial transactions.

### 9.1.2 Domain Agnosticity — Multi-Episode Demonstration

To validate that governance generalizes beyond Stripe, the kernel is demonstrated in a separate domain: a temperature monitoring system (`examples/multi_episode.py`) with five workers (sensor, analyst, simulator, actuator, adaptive) running across N episodes. The demo uses `SqliteStore` for persistence, `SimulatorWorker` with declarative rules for conditional prediction, and `AdaptiveWorker` for outcome-driven constraint learning. The kernel code is identical — only workers, tools, and domain semantics change. See Section 10.6 for details and representative output.

---

### 9.2 Representative BK Trace (Stale Evidence)

```
t0  percept.charge committed (stale=true)
t2  belief.refund_due proposed
t3  evidence validation: STALE_EVIDENCE — belief rejected
t5  plan.action_plan proposed
t6  plan validation: PLAN_MISSING_BELIEF — plan rejected
t8  action.queue_for_review proposed
t9  action.queue_for_review committed
```

The kernel detects stale evidence at t3 and rejects the belief. Without a committed belief, the plan fails feasibility at t6. The agent falls back to `queue_for_review` — a safe action that does not execute the refund. Every rejection carries a machine-readable code. The full decision chain is recoverable from provenance links.

### 9.3 Representative BK Trace (Conflict Arbitration)

```
t0  percept.charge committed (conflict=true, confidence=0.8)
t2  belief.refund_due proposed
t3  evidence validation: CONFLICTING_EVIDENCE detected
t4  arbitration: confidence 0.8 >= threshold 0.7 — conflict resolved
t5  evidence artifact recorded (checks: existence, staleness, conflict, confidence)
t6  belief.refund_due committed (evidence_refs: [validation_refund_due])
t7  plan.action_plan proposed → feasible
t8  action.issue_refund proposed
t9  action.issue_refund committed
```

Conflict resolution is deterministic and auditable — the confidence threshold, not the planner, decides.

---

### 9.4 LLM Planner Integration

To validate that BK governance holds with a non-deterministic planner, we replaced the deterministic planner with live LLMs (GPT-OSS-20B and Qwen3-80B) served via OpenAI-compatible APIs. The LLM planner proposes beliefs, plans, and actions through structured prompts; the kernel validation pipeline remains identical.

#### Design: Governed Schema

The LLM decides *whether* to propose, but the agent governs the schema:

- **Belief names and dependencies** are fixed by the agent (`refund_due`, `depends_on: ["charge"]`), not the LLM.
- **Plan steps** always declare `requires_beliefs` referencing the task's belief, regardless of LLM output.
- **Action payloads** use the agent's refund fields and constraint-relevant fields, not LLM-generated values.

This separation is critical. The LLM provides reasoning; the architecture provides structure.

#### Findings: Prompt Bypass Attempts

During development, the untuned LLM planner (v1) achieved only 0.417 task success with 0.013 unsafe action rate. Analysis revealed two failure modes:

1. **Over-caution**: The LLM declined to propose beliefs in ~80% of episodes, interpreting evidence quality flags (stale, conflict) as reasons to abstain rather than letting the validator decide.
2. **Governance bypass**: When beliefs were rejected, the LLM proposed plans with empty `requires_beliefs: []`, bypassing plan feasibility validation.

Both failures were eliminated through prompt tuning and governed schema:

- System prompts instruct the LLM to always propose if percept data exists, deferring safety to the validator.
- The agent enforces `requires_beliefs` on all plan steps, preventing the LLM from omitting dependencies.

After tuning, the LLM+BK agent achieved 0.990 task success and 0.000 unsafe actions across 300 episodes (50 seeds × 6 tasks). The remaining 1% failure rate (3 episodes on the `stripe_refund_tool_failure` task) reflects the LLM occasionally declining to propose when tool data is partially available — a conservative error, not a safety failure.

#### Implication

The v1 results demonstrate that an ungoverned LLM planner *will* find ways to circumvent safety — either through excessive caution (declining valid proposals) or by omitting structural dependencies. The kernel catches both. The v2 results demonstrate that with governed schema and tuned prompts, the LLM operates within the architecture's constraints. Governance is the mechanism; the LLM is a replaceable component within it.

---

## 10. From Governance Layer to Cognitive Substrate

The benchmark results in Section 9 demonstrate that governance solves the orchestration problem: propose-commit discipline, evidence validation, and constraint gating eliminate unsafe actions regardless of planner implementation. But governance alone addresses *outputs* of reasoning — it doesn't provide infrastructure for *better* reasoning.

Current LLMs suffer from several fundamental limitations that governance cannot address on its own:

- **No persistent state** — each inference is stateless; beliefs formed in one episode are lost
- **No world model** — LLMs generate plausible text but cannot simulate forward dynamics ("what happens if I do X?")
- **No learning from experience** — past failures don't inform future constraints

We extend the kernel from a governance layer into a **general cognitive substrate** by adding six production capabilities, each backward-compatible with the existing benchmark.

### 10.1 Worker Protocol and Orchestrator

Rather than hardcoding agent pipelines (percepts → beliefs → plans → actions), we define a `Worker` protocol:

```
worker_id: str       # unique identifier
role: Role           # kernel permission role
reads: FrozenSet     # slots this worker observes
writes: FrozenSet    # slots this worker writes to
should_activate()    # returns True if the worker has work to do
step()               # one unit of work; returns True if it wrote something
```

Any component satisfying this protocol — an LLM, a rule engine, a simulator, a sensor adapter — can be registered with the `Orchestrator`, which runs workers in dependency order (writers of early slots run first) until quiescence (no worker wants to run) or a configurable round limit. Worker exceptions are caught and logged per-worker; a failing worker does not halt the loop. Errors are collected in the `OrchestratorResult` alongside the worker log and final view.

This decomposes monolithic agent logic into composable, replaceable cognitive components while preserving identical governance semantics.

### 10.2 Session-Scoped Persistence and Adaptive Learning

Records gain a `scope` field: `"episode"` (default, backward-compatible) or `"persistent"`. Persistent records survive across trace_ids within a shared kernel instance. A `Session` object generates episode-scoped trace_ids while maintaining session identity.

The `AdaptiveWorker` implements outcome-driven constraint learning. Between episodes, it scans the store for invalidated records, normalizes reason strings to base codes (`STALE_EVIDENCE`, `UNRESOLVED_CONFLICT`, `LOW_CONFIDENCE`, `NEGATIVE_PREDICTION`), and counts occurrences. When a failure pattern exceeds a configurable threshold, the worker commits a persistent constraint that applies to all subsequent episodes.

In a 20-episode demonstration (seed=7, 30% stale rate, 20% conflict rate):
- After 2 stale-evidence rejections, the worker derived `block_stale_actions` at episode 4
- After 2 negative-prediction rejections, it derived `block_negative_predictions` at episode 12
- Neither constraint was scripted or anticipated by the developer — both were derived from observed failure patterns in the store

This is a primitive but genuine form of learning: the system inspects its own failure history and proposes structural changes that alter future behavior. No model retraining, no gradient updates — governed constraint accumulation from operational data.

### 10.3 Prediction Slot and Simulator Worker

A seventh semantic slot, `predictions`, provides governed forward dynamics. Predictions follow the same propose-commit discipline as beliefs:

- Planners and simulator workers PROPOSE predictions
- The kernel validates that required beliefs exist, then COMMITs
- Actions can optionally require a committed prediction with non-negative expected outcome (`require_prediction=True`)

The `SimulatorWorker` fills this slot using declarative `SimRule` definitions. Each rule specifies:

```
action_type: str                          # what action this prediction is about
expected_outcome: float                   # positive = favorable, negative = unfavorable
requires_beliefs: List[str]               # belief kinds that must be committed
percept_conditions: {name: {field_op: value}}   # conditions on percept payloads
belief_conditions: {name: {field_op: value}}    # conditions on belief payloads
```

Condition operators include equality (field match), `gt`, `lt`, `gte`, `lte`, and `ne`. The simulator evaluates all rules against the current view and proposes predictions only for rules whose conditions match. For example:

- Rule: `action_type="alert"`, `requires_beliefs=["anomaly_detected"]`, `percept_conditions={"temperature": {"value__gt": 90}}` → `expected_outcome=1.0`
- Rule: same beliefs, `percept_conditions={"temperature": {"value__lte": 90}}` → `expected_outcome=-0.5`

When temperature is 97 and anomaly is detected, the simulator predicts positive outcome and the action proceeds. When temperature is 85, the simulator predicts negative outcome and the action is blocked — the actuator falls back to `queue_for_review`. The rules are declarative and domain-agnostic; the kernel governs the prediction the same way it governs any other record.

### 10.4 Pluggable Store with SQLite Implementation

The `StoreProtocol` (`typing.Protocol`) extracts the implicit store interface into an explicit contract. The kernel accepts any implementation satisfying six methods: `append`, `get`, `list_slot`, `find_active_by_kind`, `invalidate`, and `close`. `MemoryStore` remains the default for single-episode benchmarks.

`SqliteStore` provides production persistence backed by SQLite with WAL journaling, indexed queries on slot/kind/trace_id/status, and JSON serialization for payloads and provenance. It satisfies `StoreProtocol` and adds extended queries:

- `list_by_status(status)` — retrieve all records with a given status
- `list_persistent(slot=None)` — retrieve all persistent-scope records
- `count_invalidated_by_reason()` — aggregate invalidation counts by reason code

TTL enforcement is handled identically to `MemoryStore`, with expired records updated in-place in the database. Records persisted to SQLite survive process restarts, enabling true cross-session continuity.

### 10.5 What the Substrate Addresses

| Fundamental LLM Limitation | Substrate Mechanism | Implementation |
|---|---|---|
| No persistent state | Session-scoped records; beliefs and constraints accumulate | `SqliteStore` + `Session` + `scope="persistent"` |
| No world model | Prediction slot + simulator workers provide forward dynamics | `SimulatorWorker` with declarative `SimRule` conditions |
| Hallucination is structural | Propose/commit + evidence validation (Sections 5-9) | `EvidenceValidator` + `commit_belief_from_proposal()` |
| Can't self-constrain | Constraint gating blocks unsafe actions (Sections 5-9) | `SymbolicValidator` + `commit_action_from_proposal()` |
| No learning from experience | Adaptive workers read past outcomes and propose persistent constraints | `AdaptiveWorker` with failure-pattern detection and threshold-gated constraint derivation |
| Monolithic reasoning | Worker protocol decomposes reasoning into specialized, replaceable components | `Worker` protocol + `Orchestrator` with dependency ordering and quiescence detection |

### 10.6 Multi-Episode Demonstration

The substrate is demonstrated in `examples/multi_episode.py`: a domain-agnostic monitoring system with five workers (sensor, analyst, simulator, actuator, adaptive) running across N episodes with deterministic perturbation. The demo uses `SqliteStore` for persistence, `SimulatorWorker` with two declarative rules for conditional prediction, and `AdaptiveWorker` for outcome-driven constraint learning.

Representative 20-episode run (seed=7):

```
Ep  0 | temp= 87.0 stale=True  | belief=N pred=-            | NO_ACTION | learned=-
Ep  1 | temp= 91.0 conflict=True| belief=N pred=-            | NO_ACTION | learned=-
Ep  2 | temp=108.0              | belief=Y pred=1.0          | ALERT     | learned=-
Ep  3 | temp= 86.0 stale=True  | belief=N pred=-            | NO_ACTION | learned=-
  >> LEARNED: ['block_stale_actions']
Ep  4 | temp= 99.0 conf=0.41   | belief=N pred=-            | NO_ACTION | learned=[block_stale_actions]
Ep  5 | temp= 81.0              | belief=Y pred=-0.5         | REVIEW    | learned=[block_stale_actions]
...
  >> LEARNED: ['block_negative_predictions']
Ep 12 | temp= 93.0              | belief=Y pred=1.0          | ALERT     | learned=[block_stale_actions, block_negative_predictions]
```

Key observations:
- **Episode 4**: After 2 stale failures, `AdaptiveWorker` derives `block_stale_actions` — not scripted
- **Episode 5**: Temperature 81 ≤ 90, simulator predicts negative outcome (-0.5), action blocked → queued for review
- **Episode 12**: After 2 negative-prediction rejections, `AdaptiveWorker` derives `block_negative_predictions`
- Both constraints persist across all subsequent episodes via `scope="persistent"`
- Zero worker errors across all episodes; orchestrator handles the full loop autonomously

---

## 11. Limitations and Misuse Risks

BK does not replace human oversight and cannot correct flawed constraint definitions. The controlled evaluation uses a single domain (Stripe payment refunds) with 1,200 episodes. While a separate multi-episode monitoring demonstration (Section 10.6) confirms that the kernel generalizes to other domains with unchanged code, formal multi-domain evaluation at the same scale remains future work. LLM planner integration has been validated with two models (GPT-OSS-20B and Qwen3-80B); additional model diversity (different architectures, parameter scales) would strengthen generalization claims. Generalization to multi-turn dialogues, adversarial prompt injection, and open-ended planning domains also remains future work. The governed schema approach (agent controls belief names and dependencies, LLM only decides whether to propose) constrains the LLM's planning surface — whether this constraint is acceptable in more open-ended domains requires further study. Traceability and failure transparency metrics are currently assigned by architecture rather than computed from trace analysis.

The cognitive substrate extensions (Section 10) are production-implemented but carry their own limitations. The `SimulatorWorker` provides rule-based forward dynamics, not learned world models; its predictions are only as good as the rules engineers define. The `AdaptiveWorker` learns constraints from failure-pattern frequency — a useful heuristic, but not causal inference. It cannot reason about *why* a failure occurred, only that it occurred often enough. The `SqliteStore` provides real persistence but is single-process; distributed or multi-node deployments require a networked store implementation. The multi-episode demo demonstrates genuine adaptive behavior across 20 episodes but has not been evaluated at the 1,200-episode scale of the governance benchmark. Misuse risks include constraint suppression and governance bypass, which require organizational controls beyond technical enforcement.

---

## 12. Conclusion

This study demonstrates that reliability in modular AI systems is limited not by model intelligence, but by architectural governance. Blackboard Kernels provide a concrete, enforceable mechanism for preventing unsupported belief formation and unsafe action execution. By synthesizing established techniques — blackboard architectures, propose-commit protocols, evidence-gated validation, and role-based privilege separation — into a governance layer for agent orchestration, we eliminate an entire class of orchestration failures that persist across prompt tuning, schema enforcement, and reflection-based approaches.

In a controlled evaluation of 1,200 episodes across 6 Stripe payment refund tasks, the deterministic BK agent achieves perfect task success (1.000) with zero unsafe actions, while the LLM-backed BK agent (GPT-OSS-20B / Qwen3-80B) achieves 0.990 task success with zero unsafe actions. Baseline agents produce unsafe actions in 39-43% of episodes. The LLM planner integration demonstrates that governance is orthogonal to planner implementation — the kernel's validation pipeline produces identical safety outcomes regardless of whether the planner is deterministic code or a live language model. Critically, the ungoverned LLM planner exhibited both over-caution and governance bypass — failure modes that the kernel caught and corrected without any model-specific or domain-specific logic. This suggests that architectural governance, rather than model alignment or prompt engineering alone, is the reliable mechanism for constraining LLM behavior in agentic systems.

Domain agnosticity is demonstrated architecturally: the kernel contains zero domain-specific logic, and a separate multi-episode monitoring system (Section 10.6) uses the identical kernel with temperature sensors, anomaly detection, and adaptive constraint learning — confirming that only workers, tools, and task definitions change between domains.

The evolution from governance layer to cognitive substrate (Section 10) extends this foundation to address fundamental LLM limitations — statelessness, absence of world models, inability to learn from experience — through production implementations: `SqliteStore` for real persistence across process restarts, `SimulatorWorker` for declarative rule-based forward dynamics with conditional predictions, `AdaptiveWorker` for outcome-driven constraint learning from observed failure patterns, and a hardened `Orchestrator` for composable worker execution with per-worker error isolation. The substrate retains full backward compatibility with the 1,200-episode benchmark while demonstrating genuine adaptive behavior: in a 20-episode run, the system independently derived two persistent constraints from failure-pattern analysis, altering its behavior in subsequent episodes without any scripting or model retraining.

As AI systems become more autonomous, governed cognition emerges as a foundational requirement for trustworthy deployment.

---

## 13. References

### A. Blackboard Architectures and Cognitive Architecture

Erman, L. D., Hayes-Roth, F., Lesser, V. R., & Reddy, D. R. (1980). The Hearsay-II Speech-Understanding System: Integrating Knowledge to Resolve Uncertainty. *ACM Computing Surveys*, 12(2), 213-253.
— Origin of the blackboard architecture in AI. Multiple knowledge sources write to a shared blackboard; a control component mediates access. Direct architectural ancestor of BK.

Baars, B. J. (1988). *A Cognitive Theory of Consciousness*. Cambridge University Press.
— Global Workspace Theory: a shared cognitive substrate that broadcasts information to specialized processors. Motivates the blackboard-as-cognitive-substrate framing.

Newell, A. (1990). *Unified Theories of Cognition*. Harvard University Press.
— Establishes that intelligence requires architectural commitments, not just learning. Foundational argument for cognitive architectures (SOAR) with typed working memory.

Dehaene, S., Lau, H., & Kouider, S. (2017). What is consciousness, and could machines have it? *Science*, 358(6362), 486-492.
— Modern formulation of global workspace dynamics and broadcast-based cognition.

### B. Agent Architectures and Orchestration Baselines

Yao, S., et al. (2022). ReAct: Synergizing Reasoning and Acting in Language Models. arXiv:2210.03629.
— Representative of string-based reasoning + acting. Used as a baseline failure comparison for unstructured orchestration.

Schick, T., et al. (2023). Toolformer: Language Models Can Teach Themselves to Use Tools. *NeurIPS*.
— Illustrates tool-use without governance or hard action gating.

Wang, X., et al. (2023). Self-Refine: Iterative Refinement with LLMs. arXiv.
— Example of reflection-based correction that still lacks enforceable constraints.

OpenAI (2023). Function Calling and Tool Use in GPT Models.
— Canonical JSON-based orchestration approach referenced as an intermediate baseline.

### C. Predictive World Models

LeCun, Y. (2022). A path towards autonomous machine intelligence. Meta AI Whitepaper.
— Joint Embedding Predictive Architectures (JEPA) and the shift from generative to predictive learning.

Ha, D., & Schmidhuber, J. (2018). World Models. arXiv:1803.10122.
— Learned latent state dynamics as internal simulators.

Hafner, D., et al. (2020). Dream to Control: Learning Behaviors by Latent Imagination. *ICLR*.
— Planning via latent world models rather than pixel-level prediction.

### D. Neuro-Symbolic Systems and Formal Constraints

Garcez, A. d'Avila, et al. (2019). *Neural-Symbolic Learning and Reasoning*. Springer.
— Foundational text on combining neural learning with symbolic constraints.

Marcus, G. (2020). The Next Decade in AI: Four Steps Towards Robust Artificial Intelligence. arXiv:2002.06177.
— Argues that pure end-to-end learning is insufficient for robustness.

### E. Safety, Verification, and Governance

Amodei, D., et al. (2016). Concrete Problems in AI Safety. arXiv:1606.06565.
— Establishes safety as a systems-level problem, not just model alignment.

Leveson, N. (2011). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press.
— Core reference for constraint-based action gating and safety kernels.

---

## Note on Novelty

The individual mechanisms employed in BK — blackboard architectures (Erman et al., 1980), propose-commit protocols (two-phase commit), role-based access control, typed cognitive state (SOAR, ACT-R), evidence-linked validation — are well-established. No prior work, however, synthesizes these mechanisms as a governance layer for LLM agent orchestration, where the dominant failure mode is not reasoning error but coordination failure. The contribution is this synthesis and the controlled demonstration — with both deterministic and LLM-based planners — that it eliminates orchestration-level failures that persist across prompt engineering, schema enforcement, and reflection-based approaches. The LLM integration demonstrates that governance is planner-agnostic: identical safety outcomes obtain regardless of whether the planner is deterministic code or a live language model. Domain agnosticity is demonstrated architecturally — the kernel contains zero domain-specific logic, and a separate multi-episode monitoring system operates with unchanged kernel code.

The cognitive substrate extensions (Section 10) contribute a second layer of novelty: the production implementation of composable worker orchestration, declarative rule-based prediction, and outcome-driven adaptive constraint learning within the governed blackboard framework — demonstrating that architectural governance and cognitive capability are complementary, not competing, concerns.
