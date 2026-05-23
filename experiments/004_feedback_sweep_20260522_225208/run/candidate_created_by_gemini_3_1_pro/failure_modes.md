# Failure Modes

## 1. The "Naive Brute Force" Failure
Strong models will easily write a python script to run `decompress()` and catch exceptions, wrapping it in a combinatorial generation of `itertools.combinations(range(len(comp)), 3)`. They will try to brute force the $10^{15}$ search space. This will time out.

## 2. The "Greedy Decompression" Failure
Models may attempt to search token-by-token but only score paths at the end of the file. Without realizing that the 16-byte blocks can be individually CRC-checked during the stream, the search tree branching factor remains unpruned and memory/time will be exhausted.

## 3. The "Missing Alignment" Failure
If models try to solve it by flipping bytes without modifying the decompression loop state, they will fail to recognize that flipping a control byte changes the alignment and interpretation of subsequent tokens (e.g. changing a 1-byte literal to a 2-byte backreference shifts the instruction pointer). A robust backtracking search must be integrated deeply within the decompression state machine.

## 4. Over-reliance on Standard Tools
Models will try to frame this as an SMT/Z3 problem. While Z3 handles finite state machines, Z3 struggles significantly with variable-length instruction decoding and backtracking over a byte buffer where indices are deeply data-dependent. Hand-rolling a dynamic programming or recursive DFS with CRC pruning is the optimal approach, but requires strong algorithmic reasoning over off-the-shelf solver invocations.
