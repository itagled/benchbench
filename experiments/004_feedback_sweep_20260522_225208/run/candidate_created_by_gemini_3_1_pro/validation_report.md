# Validation Report

## Solvability and Identifiability
This benchmark requires the recovery of exactly 3 mutated bytes in a custom LZ77 compressed stream.
While blind brute-force search is computationally infeasible (approximately $\approx 10^{15}$ states for 3 flips in a 400-byte stream), the uncompressed data has a rigid semantic structure: every 16 bytes, the last 2 bytes are a Modbus CRC16 of the preceding 14 bytes.

Because the CRC16 has only a $1/65536$ chance of matching random data, a backtracking search that interleaves LZ77 decompression with CRC checking will immediately prune any branches where mutations occurred. When a block fails its CRC check, the solver can mathematically infer that one or more mutations must have occurred in the exact compressed tokens that were evaluated since the last valid CRC check. By only branching (testing byte flips) within these small local token windows, the search space collapses, making it highly solvable by a well-written algorithm.

The problem is perfectly externally solvable in principle because:
1. The exact custom compression and CRC source code are provided in `compressor.py`.
2. The rules are closed and deterministic.
3. The dense CRC checks guarantee a unique solution with overwhelming probability ($2^{-16}$ false positive rate per block over 100 blocks).
4. No hidden states, API keys, or private generator seeds are required.

## Evidence Available to the Solver
The solver has access to the corrupted binary, the decompression source code, and the English specification of the payload format (14 bytes payload + 2 bytes CRC16). This is sufficient information to build the necessary backtracking decompressor.
