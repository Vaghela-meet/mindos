# MindOS Milestone 3 (M3) — Deterministic Daily Planning Engine Specification

> **Status:** Architecture Specification (Revised Design Phase)  
> **Role:** Deterministic Planning Foundation  
> **Scope:** Milestone 3 (M3)  
> **Principle:** AI proposes → application validates → database changes. *(M3 is strictly deterministic; zero AI dependencies).*

---

## Executive Overview & Architectural Framing

MindOS is an Adaptive Personal Productivity Operating System.

> *"MindOS doesn't just manage tasks. It manages the user's available attention over time."*

Technically, MindOS is defined as:

> *"MindOS is a constraint-aware adaptive planning system that continuously converts goals, tasks, deadlines, available capacity, and observed execution into a feasible daily schedule, then replans when reality diverges from the plan."*

### The M3 Core Principle

> **"M3 does not attempt to predict the user. It creates the best deterministic plan possible from the information currently available, while preserving enough execution data for future adaptation."**

### Evolution Roadmap

MindOS is engineered in deliberate, strictly separated milestones:

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│  M3: PLAN   │ ──> │ M4: OBSERVE │ ──> │  M5: ADAPT  │ ──> │ M6: AI INTERPRETATION  │ ──> │ M7+: PERSONALIZATION   │
│             │     │             │     │             │     │                        │     │      & LEARNING        │
│Deterministi-│     │FocusSession │     │Replanning on│     │LLM explains reasons,   │     │Learned velocity, energy│
│ca-lly build │     │telemetry,   │     │divergence,  │     │proposes task breakdown,│     │curves, dynamic buffers,│
│feasible plan│     │actual vs est│     │slippage     │     │natural language chat   │     │behavioral habits       │
└─────────────┘     └─────────────┘     └─────────────┘     └────────────────────────┘     └────────────────────────┘
```

M3 focuses exclusively on the **PLAN** stage. It contains zero machine learning, zero artificial intelligence, and zero probabilistic heuristics.

---

## Architectural Principles

The planning engine is governed by five foundational architectural principles:

### 1. Plan vs. Recommendation
The planning engine generates a concrete, chronological `DailyPlan` consisting of bounded `ScheduleBlocks`, not merely a ranked or sorted list of suggested tasks. Users do not need another backlog view; they need an actionable commitment of attention against time. Any eligible task that cannot be scheduled must be explicitly accounted for with a structured reason code.

### 2. Reason-Coded Decisions
Every allocation or exclusion decision made by the planning engine must be accompanied by structured, machine-readable reason categories (e.g., `DEADLINE_PRESSURE`, `CAPACITY_CONSTRAINT`). The deterministic engine does not generate natural language; it generates data contracts that an advisory AI layer can interpret and explain in later milestones without altering scheduling decisions.

### 3. Preserve Plan History
A newly generated or regenerated plan must never destroy past planning records. When a schedule is regenerated or adapted, the previous plan transitions to `SUPERSEDED` status. This guarantees an immutable audit trail of what was planned versus what actually occurred, creating the foundational dataset required for M4 observation and M5 adaptation.

### 4. Preserve Estimate vs. Observation
The system strictly distinguishes between three related but distinct temporal concepts:
- **`estimated_effort_minutes`:** The user's original, unrounded effort estimate on the `Task`.
- **`scheduled_block_minutes`:** The calendar duration allocated on the discrete scheduling grid for a `ScheduleBlock`.
- **`observed_actual_seconds`:** The real-world execution time recorded during a `FocusSession` (M4).

The planning engine must never overwrite, mutate, or blur user-provided estimates with calendar occupancy or execution telemetry. This boundary preserves the ability to compute estimation drift and learning curves.

### 5. Design for Measurement
Every component of the planning engine must be measurable. We cannot improve what we cannot quantify. The schema and execution outputs preserve timestamps, planned slot coordinates, shortfall minutes, and allocation ratios so future milestones can quantitatively benchmark planning accuracy, schedule adherence, and replanning frequency.

---

## 1. Planning Objective

The planning engine's optimization objective is defined as:

> **"Maximize meaningful progress toward important goals while respecting time constraints, deadlines, availability, and realistic working limits."**

### Explicit Non-Objectives
To maintain architectural integrity, the planner explicitly does NOT optimize for:
1. **Maximizing total task count:** Completing 15 trivial administrative checkboxes while ignoring a strategic high-priority milestone is a planning failure.
2. **Filling every available minute (100% packing):** Humans are not industrial machines. A schedule packed to 100% capacity collapses upon the first minor interruption.
3. **Blind deadline satisfaction at all costs:** Scheduling an overdue low-value chore ahead of vital deep work for a critical goal distorts user attention.
4. **Producing the busiest possible calendar:** The objective is cognitive clarity and goal advancement, not artificial schedule density.

---

## 2. Inputs

The planning engine is a pure, side-effect-free function:
$$\text{generate\_daily\_plan}(\text{Inputs}) \longrightarrow (\text{DailyPlan}, [\text{ScheduleBlock}], \text{ShortfallReport})$$

```text
┌────────────────────────────────────────────────────────────────────────┐
│                             ENGINE INPUTS                              │
├──────────────────────────────┬───────────────────────────┬─────────────┤
│ Required Inputs              │ Optional Inputs           │ Future      │
├──────────────────────────────┼───────────────────────────┼─────────────┤
│ • planning_date (Date)       │ • existing_plan_id (int)  │ • Learned   │
│ • user_id (int)              │ • planner_policy (config) │   velocity  │
│ • user_timezone (str)        │ • is_recurring (filter)   │ • Energy    │
│ • candidate_tasks (list)     │                           │   curves    │
│ • active_goals (list)        │                           │ • Calendar  │
│ • availability_windows (list)│                           │   events    │
└──────────────────────────────┴───────────────────────────┴─────────────┘
```

### Detailed Breakdown

#### Required Inputs
- **`planning_date` (`datetime.date`):** The target calendar date being planned (e.g., `2026-09-25`).
- **`user_id` (`int`):** The tenant boundary for data isolation.
- **`user_timezone` (`str`):** IANA timezone identifier (e.g., `UTC`, `America/New_York`, `Asia/Kolkata`) from `User.timezone`.
- **`candidate_tasks` (`List[Task]`):** Actionable tasks (`status IN ('TODO', 'IN_PROGRESS')`) belonging to active goals.
- **`active_goals` (`List[Goal]`):** Goals with `status = 'ACTIVE'`, providing strategic context and priority.
- **`availability_windows` (`List[Availability]`):** Discrete recurring availability windows for the weekday of `planning_date`, preserving start and end boundaries (not flattened into an unstructured total).

#### Optional Inputs
- **`existing_plan_id` (`Optional[int]`):** If regenerating or replanning, the identifier of the plan to supersede.
- **`planner_policy` (`Optional[PlannerPolicy]`):** Configurable policy parameters for block limits and minimum slot sizes.

#### Future Inputs (Deliberately Deferred Beyond M3)
- Historical actual duration averages or velocity multipliers (M4/M5).
- Real-time physiological energy or chronotype curves (M7+).
- Third-party external calendar appointments via Google/Outlook (Future integration).
- Real-time location or environmental context (Future integration).

---

## 3. Task Types

To manage cognitive load and schedule structure without conflating duration with cognitive nature, MindOS defines seven conceptual task types:

| Task Type | Cognitive Profile | Scheduling Bias | Policy Default Minimum Block |
| :--- | :--- | :--- | :--- |
| `ROUTINE` | Low cognitive overhead, recurring | Preferred start/end of day anchoring | 30 minutes |
| `DEEP_WORK` | High cognitive focus, high fatigue | Earliest available contiguous slot runs; protected from splitting | 60 minutes |
| `SHALLOW_WORK`| Low-to-moderate focus, execution | Residual gap filler, afternoon placement | 30 minutes |
| `HABIT` | High automaticity, short duration | Fixed anchor slot or contiguous with routines | 30 minutes |
| `DEADLINE_DRIVEN` | Urgent output requirement | Highest priority candidate placement regardless of slot length | 30 minutes |
| `CREATIVE` | Unstructured, exploratory | Contiguous mid-day or morning blocks; avoids interleaving | 60 minutes |
| `ADMINISTRATIVE` | Low focus, transactional | End of day batching; fills small residual gaps | 30 minutes |

### Domain Correction: Duration $\ne$ Cognitive Nature
**Task type MUST NOT be inferred from estimated duration.**
- A 15-minute creative brainstorm or reflection session is `CREATIVE` or `DEEP_WORK`, not shallow work.
- A 90-minute administrative receipt filing or inbox cleanup chore is `ADMINISTRATIVE`, not deep work.
Duration measures *effort volume*; task type measures *cognitive modality*. Inferring one from the other corrupts both scheduling bias and future telemetry.

### Required M3 Domain Extension & Proposed Representation
The current `Task` model (from M1) contains: `id`, `goal_id`, `title`, `description`, `status`, `priority`, `estimated_minutes`, `deadline`, `completed_at`. It does not contain `task_type`.

**Proposed Cleanest Representation for M3:**
When M3 schema extensions are introduced, add an explicit enum column to `tasks`:
```python
class TaskType(str, enum.Enum):
    ROUTINE = "ROUTINE"
    DEEP_WORK = "DEEP_WORK"
    SHALLOW_WORK = "SHALLOW_WORK"
    HABIT = "HABIT"
    DEADLINE_DRIVEN = "DEADLINE_DRIVEN"
    CREATIVE = "CREATIVE"
    ADMINISTRATIVE = "ADMINISTRATIVE"

# In Task model:
task_type = Column(
    Enum(TaskType, name="task_type"),
    nullable=False,
    server_default="SHALLOW_WORK",
    index=True,
)
```
- **Fallback during M3:** If a task does not yet have an explicit `task_type`, the system assigns the safe default `SHALLOW_WORK` (or `STANDARD`), but **never** infers it from `estimated_minutes`.

---

## 3.1 Recurring / Routine Work Gap

### Documented Domain Gap
The current MindOS domain contains recurring weekly `Availability` (M2), but **tasks have no recurrence concept**. Every `Task` is currently a one-time execution entity. Discussing `ROUTINE` or `HABIT` scheduling without a recurrence mechanism creates an architectural disconnect.

### Proposed Minimal Representation for MindOS
To avoid building an over-engineered iCalendar RFC-5545 recurrence engine prematurely, MindOS proposes the smallest clean representation that distinguishes recurring work from one-off tasks:

```python
class RecurrenceCadence(str, enum.Enum):
    DAILY = "DAILY"
    WEEKDAYS = "WEEKDAYS"
    WEEKLY = "WEEKLY"

# Minimal extension on Task:
is_recurring = Column(Boolean, nullable=False, default=False, server_default="false")
recurrence_cadence = Column(Enum(RecurrenceCadence, name="recurrence_cadence"), nullable=True)
```

- **Planning Engine Behavior:**
  - When planning for date $D$, one-time tasks (`is_recurring = False`) are scheduled and transition to `COMPLETED` upon finish.
  - Recurring tasks (`is_recurring = True`) serve as templates that can generate a candidate instance for date $D$ matching its cadence (`DAILY`, `WEEKDAYS`, or `WEEKLY` on the target weekday), without destroying the template upon completion.
- *Note:* This domain extension is documented here as an M3 dependency and will be formally added during M3 implementation.

---

## 4. Priority Model

The priority model balances the strategic importance of the parent Goal with the urgency of the specific Task.

Existing domain priority enums: `LOW`, `MEDIUM`, `HIGH`.

### Deterministic Importance Matrix
Instead of arbitrary, floating-point magic numbers, MindOS uses a tiered lexicographic ordering matrix that guarantees explainable placement:

```text
               ┌────────────────────────────────────────────────────────┐
               │                     GOAL PRIORITY                      │
               │         HIGH              MEDIUM             LOW       │
┌──────────────┼──────────────────┬──────────────────┬──────────────────┤
│   T   HIGH   │ Tier 1: Critical │ Tier 2: Major    │ Tier 3: Focused  │
│   A          │ (Highest Weight) │ (Strategic)      │ (Tactical High)  │
│   S   ───────┼──────────────────┼──────────────────┼──────────────────┤
│   K   MEDIUM │ Tier 2: Major    │ Tier 4: Standard │ Tier 5: Routine  │
│       ───────┼──────────────────┼──────────────────┼──────────────────┤
│   P   LOW    │ Tier 3: Focused  │ Tier 5: Routine  │ Tier 6: Backlog  │
│   R          │ (Low Task/Hi Goal│ (Standard Low)   │ (Lowest Weight)  │
└──────────────┴──────────────────┴──────────────────┴──────────────────┘
```

### Evaluation Hierarchy
1. **Urgency (Deadline Pressure Tier):** Imminent deadlines override general importance.
2. **Combined Importance Tier:** Tier 1 through Tier 6 from the Goal $\times$ Task matrix.
3. **Execution Momentum:** Tasks already `IN_PROGRESS` take precedence over unstarted `TODO` tasks within the same tier to promote completion over WIP accumulation.

---

## 5. Deadline Pressure

Deadline pressure is computed deterministically relative to the `planning_date`.

Let $\Delta_{\text{days}} = \text{task.deadline.date} - \text{planning\_date}$.

```text
   Overdue          Imminent           Approaching           Distant          No Deadline
(Δdays < 0)       (0 ≤ Δdays ≤ 1)    (2 ≤ Δdays ≤ 7)      (Δdays > 7)       (deadline is None)
───────┬─────────────────┬───────────────────┬───────────────────┬─────────────────>
       │                 │                   │                   │
   CRITICAL          URGENT              ELEVATED            NORMAL            BASELINE
  Must flag        Must schedule       Schedule if         Regular           Prioritize by
  overdue;         today if            capacity            priority          Goal & Task
  schedule first   capacity fits       permits             matrix            tier
```

### Deterministic Rules
1. **Overdue ($\Delta_{\text{days}} < 0$):**
   - Classified as `OVERDUE`.
   - Placed in the highest candidate pool.
   - Assigned reason code `DEADLINE_PRESSURE_OVERDUE`.
2. **Imminent ($0 \le \Delta_{\text{days}} \le 1$):**
   - Due today or tomorrow.
   - Promoted to Tier 1 candidate status.
   - Assigned reason code `DEADLINE_PRESSURE_IMMINENT`.
3. **Approaching ($2 \le \Delta_{\text{days}} \le 7$):**
   - Due within the planning horizon.
   - Given a secondary priority boost; eligible for multi-day task split allocation.
   - Assigned reason code `DEADLINE_PRESSURE_APPROACHING`.
4. **Distant ($\Delta_{\text{days}} > 7$):**
   - Normal prioritization. Scheduled only if higher-priority or more urgent items leave available capacity.
5. **No Deadline:**
   - Evaluated strictly on Goal $\times$ Task importance and contextual continuity.

*Rule:* Deadline pressure elevates candidate ordering, but will not force a task into an availability slot smaller than the policy's minimum block size.

---

## 6. Capacity Calculation & Buffer Semantics

Available planning capacity derives strictly from the user's recurring `Availability` for the target weekday.

### Buffer as a Capacity Ceiling
> **Crucial Architectural Definition:** The 15% buffer is a **capacity ceiling**, not a literal scheduled block placed on the calendar.

MindOS schedules work into no more than **85%** of raw availability. The remaining 15% of capacity remains **completely unallocated** as free space to absorb real-world disruptions (spillover, interruptions, transitions).

```text
Raw Availability Windows (Total = 360m across all windows)
┌─────────────────────────────────────────────────────────────┬──────────────┐
│                  Usable Capacity (85% = 300m)               │ Buffer (15%) │
│              [Allocated into Discrete 30m Slots]            │    (60m)     │
│                                                             │[Unallocated] │
└─────────────────────────────────────────────────────────────┴──────────────┘
```

### Deterministic Formulation
1. **Raw Available Minutes ($C_{\text{raw}}$):**
   Sum of durations across all discrete availability windows on the target weekday:
   $$C_{\text{raw}} = \sum_{w \in W} (\text{end\_time}_w - \text{start\_time}_w) \text{ in minutes}$$

2. **Usable Planning Capacity ($C_{\text{usable}}$):**
   The maximum capacity available for scheduled blocks, rounded down to the nearest 30-minute grid boundary:
   $$C_{\text{usable}} = \left\lfloor \frac{C_{\text{raw}} \times 0.85}{30} \right\rfloor \times 30$$

3. **Protected Buffer ($B_{\text{protected}}$):**
   $$B_{\text{protected}} = C_{\text{raw}} - C_{\text{usable}}$$
   *Invariant:* The sum of all `scheduled_block_minutes` in a plan can never exceed $C_{\text{usable}}$.

---

## 7. 30-Minute Scheduling Grid: Effort vs. Schedule Occupancy

MindOS locks all schedule allocation to a discrete **30-minute resolution**.

```text
09:00       09:30       10:00       10:30       11:00       11:30       12:00
  ├─── Slot 1 ───┼─── Slot 2 ───┼─── Slot 3 ───┼─── Slot 4 ───┼─── Slot 5 ───┤
```

### The Effort vs. Occupancy Triad
MindOS strictly distinguishes between three measurements:

```text
┌──────────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│   estimated_effort_minutes   │   scheduled_block_minutes    │  unscheduled_effort_minutes  │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ The user's unrounded belief  │ The physical calendar block  │ Effort that could not be     │
│ about how much focused time  │ allocated on the 30m grid.   │ scheduled in this daily plan │
│ the task requires.           │ (Always a multiple of 30m).  │ due to capacity limits.      │
│ Example: 45 minutes          │ Example: 60 minutes          │ Example: 0 (or remaining)    │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

### Rules
1. **Never Mutate User Estimates:** `Task.estimated_minutes` is immutable during planning.
2. **Grid Quantization:** Because the grid resolution is 30 minutes, tasks occupy $\lceil \text{effort} / 30 \rceil \times 30$ minutes of calendar time.
3. **Internal Transition Slack:** When a 45-minute task is scheduled into a 60-minute block, the 15-minute difference is recognized as *intra-block transition slack*. It accounts for setup, context switching, and minor overrun without perturbing the rest of the schedule.
4. **Shortfall Precision:** Shortfall is calculated against `estimated_effort_minutes`, not quantized block minutes, ensuring that capacity reporting accurately reflects real human workload.

---

## 8. Task Splitting & Policy Parameters

Large tasks exceeding a single grid slot can be split into multiple `ScheduleBlocks`.

```text
Task: "Write Specification Document" (Estimated Effort: 120 minutes)
Window A (09:00 - 10:30, 90m Contiguous Run):  [ Block 1: 90m (3 slots) ]
                                              ─── Inter-window gap (Lunch) ───
Window B (13:00 - 15:00, 120m Contiguous Run): [ Block 2: 30m (1 slot) ] -> Task Complete
```

### Configurable Splitting Policy Defaults
The splitting rules are defined as **explicit, configurable policy parameters**, rather than hard-coded universal truths:

```python
class PlannerPolicy:
    minimum_deep_work_block: int = 60    # Deep/Creative tasks need at least 60m
    minimum_standard_block: int = 30     # Routine/Shallow tasks need at least 30m
    max_daily_task_blocks: int = 2       # Max fragmentation per task per day
    usable_capacity_ratio: float = 0.85  # 85% usable, 15% buffer
```

### Policy Rules
1. **Initial Deterministic Defaults:** The values above are the initial baseline. Future adaptive milestones (M5+) can calibrate them per user based on observed focus telemetry.
2. **Splitting Across Availability Windows:** When a task's duration exceeds the remaining capacity of the current availability window, it may be split into the next availability window **only if** the remaining time in both windows meets or exceeds the task's `minimum_block_size`.
3. **Anti-Fragmentation Invariant:** A single task must never be split into more than `max_daily_task_blocks` (default 2) in a single day. Fragmenting work into 4 or 5 thirty-minute pieces across a day destroys deep focus.
4. **Multi-Day Spillover:** If a task's effort exceeds what can be accommodated today under these policy limits, only the allowed blocks are scheduled today; the residual effort remains as `unscheduled_effort_minutes` on the backlog for tomorrow's plan.

---

## 9. Context-Switch Penalty

Cognitive switching between unrelated goals introduces friction. MindOS models this with a deterministic context-continuity preference.

```text
Fragmented (High Context Switching):
[ Goal 1 (30m) ] ──> [ Goal 2 (30m) ] ──> [ Goal 1 (30m) ] ──> [ Goal 3 (30m) ]

Batched (Low Context Switching - PREFERRED):
[ Goal 1 (60m) ] ───────────────────────> [ Goal 2 (30m) ] ──> [ Goal 3 (30m) ]
```

### Deterministic Rules
1. **Goal Continuity Bias:** When choosing among candidates within the same importance tier for the next slot in a contiguous run, the engine selects the candidate sharing the `goal_id` of the immediately preceding block.
2. **Type Continuity Bias:** Tasks of identical cognitive modality (e.g., grouping `ADMINISTRATIVE` tasks at the end of the day) are co-located.
3. **Hard Boundary:** Continuity bias is an intra-tier tie-breaker. It **never** allows a low-priority task to leapfrog an imminent deadline task from a higher tier.

---

## 10. Shortfall Handling

MindOS operates under physical reality: **it never hallucinates time.**

```text
Example Shortfall Accounting:
┌──────────────────────────────────────────────┐
│ Usable Capacity: 300 minutes                 │
├────────────────────────────────┬─────────────┴─────────────────┐
│ Scheduled Work: 300 minutes    │ Unscheduled Shortfall: 90m    │
│ (5 Tasks Scheduled)            │ (2 Tasks Excluded)            │
└────────────────────────────────┴───────────────────────────────┘
```

### Protocol
When candidate workload exceeds $C_{\text{usable}}$:
1. **Schedule What Fits:** Fill usable slots in deterministic priority order until capacity or policy constraints prevent further allocation.
2. **Respect the Buffer:** Stop scheduling when $C_{\text{usable}}$ is reached. Do not encroach upon $B_{\text{protected}}$.
3. **Compute Explicit Shortfall:**
   $$\text{shortfall\_effort\_minutes} = \sum_{\text{excluded}} \text{task.unscheduled\_effort\_minutes}$$
4. **Emit Structured Diagnostic Records:** Every unscheduled task is recorded in the plan output with a machine-readable reason code:
   - `INSUFFICIENT_CAPACITY`: Task was eligible and high priority, but daily usable capacity was exhausted.
   - `LOWER_PRIORITY`: Excluded because available slots were allocated to higher-priority work.
   - `WINDOW_TOO_SMALL`: Remaining unallocated slot in a window was smaller than the task's `minimum_block_size`.
   - `DEADLINE_OUTSIDE_HORIZON`: Candidate has a distant deadline and was deferred in favor of urgent work.

---

## 11. Determinism

### Formal Deterministic Guarantee
> **"The same logical planning inputs produce the same logical task ordering, slot allocation, schedule boundaries, shortfall results, and reason codes."**

### Scope of Deterministic Equality
- **Included in Determinism:**
  - The ordered sequence of scheduled `task_id`s.
  - The exact `start_time` and `end_time` boundaries of every `ScheduleBlock`.
  - The exact `unscheduled_task_ids` and their assigned reason codes.
  - Total `scheduled_block_minutes` and `shortfall_effort_minutes`.
- **Excluded from Determinism:**
  - Database primary keys (`id`) generated by PostgreSQL sequences.
  - Audit timestamps (`created_at`, `updated_at`, `generated_at`).
  - JSON serialization whitespace or dictionary key ordering.

There is zero randomness, no system clock dependencies during candidate ordering, and zero external AI/network calls.

### Stable Tie-Breaking Hierarchy
When two tasks have identical urgency, importance, and duration fit, the tie is broken strictly down this chain:
```text
1. Deadline Proximity (Earlier deadline wins; task with deadline beats task without)
      │
      ▼ (if tied)
2. Task Priority (HIGH > MEDIUM > LOW)
      │
      ▼ (if tied)
3. Goal Priority (HIGH > MEDIUM > LOW)
      │
      ▼ (if tied)
4. Context Continuity (Matches goal/type of immediately preceding block)
      │
      ▼ (if tied)
5. Task State (IN_PROGRESS beats TODO)
      │
      ▼ (if tied)
6. Task Creation Timestamp (created_at ascending - older tasks first)
      │
      ▼ (if tied)
7. Entity ID (Task.id ascending - definitive mechanical tie-breaker)
```

---

## 12. Plan Generation Algorithm (Availability-Window-Aware)

The planner does **NOT** flatten separate availability windows into a continuous timeline. It preserves the discrete structure of availability windows to prevent scheduling tasks across non-working gaps.

```text
Availability Windows (e.g., Morning 09:00-12:00, Afternoon 14:00-17:00)
       │
       ▼
Contiguous Slot Runs:
  Run 1 [09:00, 09:30, 10:00, 10:30, 11:00, 11:30] (6 slots = 180m)
  ─── Gap: 12:00 - 14:00 (Lunch/Unavailable) ───
  Run 2 [14:00, 14:30, 15:00, 15:30, 16:00, 16:30] (6 slots = 180m)
       │
       ▼
Allocate into Runs without crossing boundaries (Split across runs only if policy permits)
```

### Algorithmic Pipeline

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        PLAN GENERATION PIPELINE                        │
├────────────────────────────────────────────────────────────────────────┤
│ 1. INGEST & FILTER        Validate inputs; drop COMPLETED/CANCELLED    │
│         │                                                              │
│         ▼                                                              │
│ 2. BUILD WINDOW RUNS      Map Availability into Contiguous Slot Runs   │
│         │                                                              │
│         ▼                                                              │
│ 3. COMPUTE CAPACITY       Apply 85% capacity ceiling; cap total slots  │
│         │                                                              │
│         ▼                                                              │
│ 4. TIER & SORT CANDIDATES Deterministic lexicographic sort             │
│         │                                                              │
│         ▼                                                              │
│ 5. ALLOCATE RUN-BY-RUN    Fill slots within runs; respect window gaps  │
│         │                                                              │
│         ▼                                                              │
│ 6. VALIDATE INVARIANTS    Assert zero overlaps, containment, grid rules│
│         │                                                              │
│         ▼                                                              │
│ 7. EMIT PLAN ARTIFACTS    Assemble DailyPlan, Blocks & ShortfallReport │
└────────────────────────────────────────────────────────────────────────┘
```

### Algorithmic Specification (Implementation-Neutral Pseudocode)

```python
function generate_daily_plan(user_id, planning_date, user_timezone, policy):
    # Phase 1: Ingest & Filter
    raw_windows = get_user_availability(user_id, weekday_of(planning_date))
    if not raw_windows:
        return empty_plan(user_id, planning_date, reason="NO_AVAILABILITY")

    active_goals = get_active_goals(user_id)
    candidate_tasks = get_actionable_tasks(user_id, active_goals)
    if not candidate_tasks:
        return empty_plan(user_id, planning_date, reason="NO_ELIGIBLE_TASKS")

    # Phase 2: Build Contiguous Slot Runs per Availability Window
    # Crucial: Windows are NOT flattened. Gaps between windows are preserved.
    slot_runs = []
    total_raw_minutes = 0
    for window in raw_windows:
        run = generate_30m_slots_in_window(window.start_time, window.end_time)
        if run:
            slot_runs.append(run)
            total_raw_minutes += len(run) * 30

    # Phase 3: Capacity Calculation & Ceiling Cap
    usable_capacity_minutes = floor((total_raw_minutes * policy.usable_capacity_ratio) / 30) * 30
    max_slots_to_allocate = usable_capacity_minutes // 30

    # Phase 4: Deterministic Candidate Ordering
    ordered_candidates = sort_candidates_deterministic(
        candidate_tasks,
        active_goals,
        planning_date
    )

    # Phase 5: Window-Aware Slot Allocation
    schedule_blocks = []
    unscheduled_records = []
    allocated_slot_count = 0
    task_split_tracker = defaultdict(int)

    for task in ordered_candidates:
        if allocated_slot_count >= max_slots_to_allocate:
            unscheduled_records.append(ShortfallRecord(task, "INSUFFICIENT_CAPACITY"))
            continue

        needed_slots = ceil(task.estimated_minutes / 30)
        task_allocated = False

        # Attempt to place task within an availability window run
        for run in slot_runs:
            available_slots_in_run = run.get_unallocated_slots()
            slots_remaining_today = max_slots_to_allocate - allocated_slot_count
            effective_available = min(len(available_slots_in_run), slots_remaining_today)

            if effective_available <= 0:
                continue

            # Case A: Fits completely within the contiguous run
            if needed_slots <= effective_available:
                slots = run.consume_slots(needed_slots)
                block = create_schedule_block(task, slots, reason="PRIMARY_FIT")
                schedule_blocks.append(block)
                allocated_slot_count += needed_slots
                task_allocated = True
                break

            # Case B: Cannot fit completely, evaluate task splitting across windows
            min_block_slots = policy.minimum_deep_work_block // 30 if task.task_type in (DEEP_WORK, CREATIVE) else policy.minimum_standard_block // 30
            can_split = (
                task_split_tracker[task.id] < policy.max_daily_task_blocks
                and effective_available >= min_block_slots
            )

            if can_split:
                # Allocate what fits in this run without crossing the window gap
                slots = run.consume_slots(effective_available)
                block = create_schedule_block(task, slots, reason="PARTIAL_WINDOW_SPLIT")
                schedule_blocks.append(block)
                allocated_slot_count += effective_available
                task_split_tracker[task.id] += 1
                needed_slots -= effective_available
                # Task continues in next iteration or next run if capacity permits

        if not task_allocated and task.id not in [b.task_id for b in schedule_blocks]:
            unscheduled_records.append(ShortfallRecord(task, "INSUFFICIENT_CAPACITY"))

    # Phase 6: Invariant Validation
    plan = build_daily_plan(user_id, planning_date, schedule_blocks)
    validate_plan_invariants(plan, schedule_blocks, raw_windows, usable_capacity_minutes)

    # Phase 7: Emit Plan Result
    return PlanResult(
        daily_plan=plan,
        schedule_blocks=schedule_blocks,
        shortfall_report=ShortfallReport(unscheduled_records, usable_capacity_minutes)
    )
```

---

## 13. Plan Validation

Before any plan is committed or returned, it must pass a strict suite of invariant assertions:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        PLAN INVARIANT CHECKLIST                        │
├────────────────────────────────────────────────────────────────────────┤
│ [✓] 1. Zero Overlap: No two ScheduleBlocks overlap in time             │
│ [✓] 2. Window Containment: Every block is strictly inside one window   │
│ [✓] 3. No Gap Crossing: No block spans across inter-window gaps        │
│ [✓] 4. Grid Alignment: All blocks start and end on :00 or :30          │
│ [✓] 5. Capacity Ceiling: Total block minutes <= usable capacity ceiling│
│ [✓] 6. Temporal Validity: start_time < end_time for every block        │
│ [✓] 7. Task Status: No COMPLETED or CANCELLED tasks scheduled          │
│ [✓] 8. Strict Ownership: Plan, blocks, and tasks belong to same user_id│
│ [✓] 9. Single Plan per Date: Only one ACTIVE plan per user per date    │
└────────────────────────────────────────────────────────────────────────┘
```

### Failure Behavior
If any invariant is violated during generation:
1. The transaction is aborted immediately.
2. The erroneous plan is **never** written to PostgreSQL.
3. A structured `PlanInvariantViolationException` is raised with full diagnostic details (slot coordinates, conflicting IDs, and violated rule).

---

## 14. Explainability & Reason Codes

Every decision to schedule or exclude work is tagged with a structured enum reason code:

### Scheduling Reason Codes (`ScheduleReasonCode`)
- `DEADLINE_PRESSURE_IMMINENT`: Scheduled because deadline is $\le 24$ hours away.
- `DEADLINE_PRESSURE_APPROACHING`: Scheduled to maintain pace for an upcoming deadline.
- `DEADLINE_PRESSURE_OVERDUE`: Scheduled because task has lapsed deadline.
- `GOAL_ALIGNMENT_HIGH`: Scheduled because parent goal is high priority.
- `TASK_PRIORITY_HIGH`: Scheduled because task itself is marked high priority.
- `CONTEXT_CONTINUITY`: Scheduled adjacent to similar work to prevent cognitive thrashing.
- `TASK_IN_PROGRESS`: Scheduled because work is already active.
- `GAP_FILL_ROUTINE`: Scheduled to utilize a residual 30-minute capacity block.

### Exclusion Reason Codes (`ExclusionReasonCode`)
- `INSUFFICIENT_CAPACITY`: Valid and actionable, but usable daily capacity was exhausted.
- `LOWER_PRIORITY`: Displaced by higher-ranking goals or imminent deadlines.
- `WINDOW_TOO_SMALL`: Remaining unallocated slot in a window was smaller than the task's `minimum_block_size`.
- `DEADLINE_OUTSIDE_HORIZON`: Deadline is distant; urgent work prioritized.
- `MAX_DAILY_SPLITS_REACHED`: Task was already scheduled up to `max_daily_task_blocks` today and cannot be fragmented further.

---

## 15. Edge Cases

| Edge Case | Exact Engine Behavior |
| :--- | :--- |
| **No availability set for day** | Generates `DailyPlan` with status `ACTIVE`, zero `ScheduleBlocks`, and shortfall report stating `NO_AVAILABILITY_CONFIGURED`. |
| **No eligible tasks** | Generates `DailyPlan` with zero blocks and reason `NO_ACTIONABLE_TASKS`. |
| **Task with no deadlines** | Scheduled purely based on Goal $\times$ Task importance and capacity fit. |
| **Task with no goal** | Rejected by M1 domain integrity (`Task.goal_id` is non-nullable). |
| **Task with huge estimate ($> C_{\text{usable}}$)** | Schedules maximum allowed splits (`max_daily_task_blocks`) today; remaining duration remains as `unscheduled_effort_minutes` on backlog. |
| **Task smaller than 30m (e.g., 10m)** | Allocated one 30m grid slot. 20m treated as intra-block slack. Original estimate untouched. |
| **Invalid estimate ($\le 0$ or null)** | If null, assigns 30m default slot with `DEFAULT_ESTIMATE_APPLIED`. $\le 0$ is rejected by database check constraint. |
| **Overdue tasks** | Flagged as `OVERDUE`, elevated to top candidate tier, assigned `DEADLINE_PRESSURE_OVERDUE`. |
| **Identical deadlines** | Resolved using deterministic tie-breaking (Task Priority $\rightarrow$ Goal Priority $\rightarrow$ Context $\rightarrow$ ID). |
| **Overlapping availability** | Prevented by M2 constraints. Engine asserts non-overlap. |
| **Adjacent availability** | Boundary touching windows (e.g., 09:00–12:00 and 12:00–15:00) merge into a single continuous slot run. |
| **Disjoint availability windows** | Windows separated by a gap (e.g., lunch 12:00–14:00) form distinct slot runs. Blocks cannot span across the gap. |
| **Completed / Cancelled tasks** | Filtered out during candidate ingestion. Never scheduled. |
| **Availability slot too small ($< 30$m)** | Ignored during grid slot generation; classified as unavailable buffer. |
| **Mid-day replanning** | Slots prior to `current_time` are marked `ELAPSED`; only remaining future slots are scheduled. |
| **Timezone boundary crossing** | All daily plans scoped to the user's localized midnight-to-midnight boundary in `User.timezone`. |

---

## 16. Future Extension Points for Adaptation

While M3 is strictly deterministic, it embeds the architectural hooks required for future milestones:

```text
M3 Output                 M4 Telemetry                M5 Adaptive Engine
─────────                 ────────────                ──────────────────
ScheduleBlock    ───>    FocusSession         ───>    Replanning Trigger
(Planned: 60m)           (Actual: 85m)                (Slippage detected: +25m)
                                                              │
                                                              ▼
                                                      Personalized Policy Adjust
                                                      (M7+: Learned 1.4x velocity,
                                                            custom min block size)
```

### Specific Integration Touchpoints
1. **Planned vs. Actual Delta (M4):** `ScheduleBlock.id` connects directly to `FocusSession.schedule_block_id`. M4 records the exact elapsed duration without altering the planned block.
2. **Velocity Multipliers (M5/M7):** Future engines can pass a computed velocity factor (e.g., $\text{actual} = 1.25 \times \text{estimated}$) into the candidate scoring phase before grid slot allocation.
3. **Dynamic Buffer Sizing (M5):** The 15% protected buffer constant (`usable_capacity_ratio = 0.85`) can be dynamically tuned per user based on trailing schedule adherence rates.
4. **Energy Level Curves (M7):** Future chronotype inputs can adjust intra-tier candidate sorting to bias `DEEP_WORK` toward morning slots.

---

## 17. Non-Goals

To keep M3 bounded, testable, and robust, the following are explicit **NON-GOALS**:

- ❌ **No AI or LLM Planning:** No prompts, completions, or generative models in the scheduling loop.
- ❌ **No Probabilistic Scheduling:** No Monte Carlo simulations or probabilistic distributions.
- ❌ **No External Calendar Sync:** No bi-directional sync with Google Calendar, Outlook, or Apple Calendar.
- ❌ **No Push Notifications:** No reminders, SMS, or email alerts in this milestone.
- ❌ **No Voice Interaction:** No audio input/output parsing.
- ❌ **No Autonomous AI Mutations:** The database is updated solely by verified deterministic application services.
- ❌ **No Microservices:** The engine lives inside `backend/app/services/planning/` within the modular monolith.
- ❌ **No Heavy Solvers:** No external commercial linear programming or integer programming solvers (e.g., CPLEX, Gurobi, Z3) unless justified by future scale.

---

## 18. Evaluation and Testability

The engine's correctness will be verified through deterministic test assertions across nine specific dimensions:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        TEST VERIFICATION MATRIX                        │
├──────────────────────────┬─────────────────────────────────────────────┤
│ Evaluation Dimension     │ Verifiable Assertion                        │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 1. Logical Determinism   │ Identical inputs produce identical task     │
│                          │ orderings, slot boundaries, and reasons.    │
│ 2. Capacity Adherence    │ Sum of block durations <= usable capacity.  │
│ 3. Window Containment    │ Blocks never cross inter-window gaps.       │
│ 4. Grid Alignment        │ minute % 30 == 0 for all start/end times.   │
│ 5. Deadline Preservation │ Imminent deadline tasks precede non-urgent. │
│ 6. Shortfall Accuracy    │ Shortfall accurately computes unmet effort. │
│ 7. Reason Completeness   │ 100% of blocks and excluded tasks have code.│
│ 8. Policy Conformance    │ No task exceeds max_daily_task_blocks.      │
│ 9. Invariant Purity      │ 0% overlap; 0% completed tasks scheduled.   │
└──────────────────────────┴─────────────────────────────────────────────┘
```

### Conceptual Test Scenarios
1. **The Balanced Day (Happy Path):** 5 tasks totaling 240 minutes, 360 minutes raw capacity (300m usable). All 5 tasks scheduled with zero shortfall and preserved buffer.
2. **The Disjoint Availability Test (Window Awareness):** Two availability windows: Morning (09:00–12:00) and Afternoon (14:00–17:00). A 120-minute task is placed completely in the morning; a 90-minute task is placed in the afternoon. Zero blocks are scheduled across the 12:00–14:00 gap.
3. **The Overloaded Backlog (Shortfall Test):** 10 tasks totaling 600 minutes, 300 minutes usable capacity. Highest priority tasks scheduled up to 300m; remaining tasks reported as `INSUFFICIENT_CAPACITY` with unallocated effort tracked accurately.
4. **The Imminent Deadline (Urgency Override):** Low-priority task due in 2 hours vs. High-priority task with no deadline. The imminent deadline task is scheduled first.
5. **The Indivisible Deep Work (Splitting Floor):** 90-minute deep work task with a 30-minute residual slot in an availability run. Task is not fragmented into an unusable 30m sliver; cleanly deferred to a window with sufficient capacity or flagged with `WINDOW_TOO_SMALL`.
6. **Zero Availability Day:** Target day has no availability windows. Returns clean empty plan with `NO_AVAILABILITY` status without raising runtime errors.
