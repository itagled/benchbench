# Failure Modes

## Known potential failure modes and mitigations

1. **Stem/suffix segmentation collisions.** If a random stem happens to end
   in the same letters as another language's suffix, a solver doing naive
   substring matching could mis-segment. *Mitigation:* the lexicon gives
   each stem explicitly, so the solver does not need to *guess* where the
   stem ends — only to compare lexicon stem with surface form. Generator
   draws stems and suffixes from disjoint syllable pools where reasonable
   and rejects pairs where the chosen plural/accusative/past suffixes
   collide with each other within a single language.

2. **Ambiguous word order.** If both example transitive sentences used the
   same noun as subject and object, word order would be undetermined.
   *Mitigation:* `pick_sentence_spec` constrains subject ≠ object per
   sentence, and the lexicon labels each stem so a solver can always
   identify which token is which.

3. **Under-demonstrated rule.** If a rule needed by the test were not
   shown in any example, the answer would not be uniquely derivable.
   *Mitigation:* `build_examples` forces a fixed coverage set (plural
   subject, plural object, past, present, adjective on subj+obj,
   negation) so every rule is exercised before the test combines them.

4. **English natural-language ambiguity.** Solver might be confused by
   English tense/article variation. *Mitigation:* the task uses
   interlinear gloss notation with explicit tags (.SG, .PL, .ACC, .PAST,
   .PRES, NEG). No natural English sentences are presented.

5. **Tokenization/normalization mismatch on scoring.** A solver might
   output uppercase or extra punctuation. *Mitigation:* scorer normalizes
   both sides (lowercase, strip punctuation, collapse whitespace).

6. **Trivially low scores for solvers that misread format.** A solver that
   does not understand it must produce a single string of conlang tokens
   could output English. *Mitigation:* solver packet explicitly states
   the required output format and gives a literal example.

## Open weaknesses

- The grammar space is moderate but not enormous; a sufficiently careful
  tool-using solver could in principle iterate over hypotheses. If
  multiple solvers score above ~25/30, future versions should expand the
  grammar feature set (case agreement, dual number, verb-subject agreement,
  fused portmanteau morphemes) to enlarge the hypothesis space.
- Adjective+plural interactions are not exercised in the current generator
  (adjectives never modify a plural noun). This is a deliberate
  simplification to keep gold uniqueness easy to argue, but it caps
  difficulty.
- The suffix syllable pool is shared across items; sufficient memorization
  across items could in principle let a solver guess. Each item's
  *combination* is unique though, so this risk is low.
