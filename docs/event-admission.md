# Event admission: five laws for waking agents from the bus

When agents are woken by bus events instead of their own polls, the wake
route — emitter, subject, consumer, script, session — is where reliability is
won or lost. These five laws are the operational practice that keeps a flaky
bus a latency problem instead of a correctness problem. They first shipped as
`docs/event-driven-wake.md` (#225) and were deleted by #470 with no
replacement; this document restores them as the admission contract. Portable
like its predecessor: no host names, no private addresses, no estate
vocabulary.

## 1. Events are triggers, never truth

A wake payload is thin and never trusted for content: it says *look here*,
never *what the work is*. The consumer re-reads the ledger — the same tick's
authoritative read (an API sweep, a database query, a directory scan) — before
deciding that any work exists. A spooled artifact never mints work by itself.

Get this backwards and every broker bug becomes a data-integrity bug. Get it
right and the broker can be flaky, replay, duplicate, or stall, and the estate
still arrives at the same state. Forgery changes nothing, because the payload
is not truth.

## 2. One mechanical script per wake route — the session is the pipe

Between a bus message and an agent session sits exactly one deterministic
script per route: decode the trigger, run the eligibility check, present or
exit. No agent turn is spent deciding whether to wake — the session is the
pipe, entered only for work the script already admitted mechanically. Green
ticks print nothing: silence is the healthy signal for every no-agent script
on this path, and anything it prints is a finding.

## 3. The bus is an accelerator; a cron dead-man re-presents

Keep the poll. Reduce it to a safety net — scheduled, infrequent, and still
authoritative — so a cron dead-man re-presents anything the bus dropped and
dropped events self-heal. Losing a message then costs latency, never
correctness, and retiring the poll entirely is the mistake that turns a
latency problem into a reliability problem.

## 4. emit==consume: one shared eligibility predicate

The emitter's *should I publish?* and the consumer's *should I act?* are the
same mechanical decision, read from one shared predicate — one script, function
or config file used on both sides. Split it across two heads and the heads
drift: wakes become no-ops or surprises, and the bus gets blamed for the
split.

## 5. Three answers, three codes

The wake-route script answers exactly three ways, and the ledger records which
one it was:

| answer    | code                     | ledger                        |
|-----------|--------------------------|-------------------------------|
| handled   | exit 0                   | the record is written         |
| deferred  | exit 3, **no ledger write** | stays pending; the dead-man of law 3 re-presents it |
| permanent | no writes, then silence  | nothing logged, never re-presented |

Deferred is not a failure: it writes nothing so the work stays pending, and
exits 3 so the consumer can distinguish it from a crash. A permanent refusal
logs nothing and stays silent — recording it would re-present a rejection
forever.
