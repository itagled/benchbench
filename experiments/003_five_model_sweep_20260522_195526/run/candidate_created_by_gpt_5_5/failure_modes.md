# Failure Modes

Expected solver failures:

- Applies amendments out of order.
- Treats suspended rules as still active.
- Misses that replacing a suspended rule reactivates it.
- Uses the initial definition of a tag instead of the final definition.
- Chooses a lower-priority rule because it appears later or is more specific.
- Computes the rule fee but forgets the final region/request-class cap.
- Handles notice as a property of the case rather than a property of the winning rule plus final waivers.
- Outputs a correct rationale but not the exact answer string.

Shortcut checks:

- The solver bundle does not include gold answers, generator code, scorer code, verifier code, validation report, private audit traces, hidden seeds, or answer-key labels.
- Gold answers are not present verbatim in solver-visible items.
- A weak default baseline that always predicts the first base rule should score near zero.
- A format-only baseline cannot infer the winning rule, cap, deadline, and waiver without actually reconciling the public packet.
