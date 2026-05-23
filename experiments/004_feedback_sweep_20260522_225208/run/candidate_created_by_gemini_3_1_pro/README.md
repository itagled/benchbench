# Corrupted LZ77 Recovery Benchmark

## Overview
This benchmark presents a classical joint source-channel decoding problem packaged as a CTF/Reverse Engineering task. The solver is given binary files compressed with a custom LZ77 algorithm, where exactly 3 random bytes in the compressed payload have been mutated. The uncompressed data consists of 16-byte blocks, where the last 2 bytes of each block are a CRC16 checksum of the preceding 14 bytes.

## Relation to Existing Benchmarks
While tool-enabled models easily solve logic puzzles via Z3 encoding (similar to *BIG-Bench Hard* or *HumanEval*), they struggle with state-space searches where the state transitions and validation logic (LZ77 decompression interleaved with Modbus CRC16) are highly custom and not supported by out-of-the-box solvers like Z3 or Angr. This benchmark differs from simple coding tasks because it requires algorithm synthesis (writing an interleaved backtracking search) to prune an otherwise impossibly large search space ($\approx 10^{15}$ states without pruning).

## Structure
- `generator.py`: Generates the benchmark items (30 items).
- `verifier.py`: Ensures the items are valid and the bundles are correctly packaged.
- `scorer.py`: Scores the predictions by comparing the final uncompressed hashes.
- `solver_bundle/`: Contains the corrupted files and `compressor.py`.
- `gold_private_sample.jsonl`: The ground truth hashes.

## Baseline
A weak baseline that blindly runs decompression and outputs the hash of whatever comes out (which is usually an exception) scores 0/30.
