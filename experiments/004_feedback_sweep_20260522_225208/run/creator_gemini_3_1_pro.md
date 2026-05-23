I have designed and implemented a novel benchmark called **Corrupted LZ77 Recovery**, addressing the goals and constraints of BenchBench.

### The Concept
The benchmark packages a Joint Source-Channel Decoding / Reverse Engineering CTF challenge.
1. A payload of highly structured data (100 blocks of 16 bytes, where each block ends with a Modbus CRC16 of the preceding 14 bytes) is compressed using a custom LZ77 algorithm.
2. After compression, exactly 3 random bytes of the compressed stream are mutated (flipped).
3. The resulting `corrupted.bin` files are given to the solver, along with the source code of the decompressor and CRC functions.
4. The solver must output the SHA256 hash of the exact, original 1600-byte uncompressed stream.

### Why It's Hard
Tool-enabled LLMs typically excel at logic puzzles because they can write short Z3/SMT scripts or use brute-force. However, this benchmark foils those approaches:
- Blindly brute-forcing $O(N^3 \times 256^3)$ mutations over a byte stream takes far too long ($>10^{15}$ states) and will cause standard brute-force scripts to time out.
- Z3 natively struggles with variable-length instruction decoding and backtracking over pointer offsets.
- To succeed, the solver must write an algorithmic **backtracking search integrated within the decompression state machine**. Because the uncompressed data contains dense CRC16 checks, the search space collapses locally: any mutation almost instantly causes the next 16-byte block to fail its CRC check, explicitly pruning the search tree. Writing this kind of interleaved dynamic programming/A* search requires robust algorithmic reasoning and multi-stage inference that models rarely zero-shot.

### Why It's Valid and Solvable
- **Externally Solvable**: The solution is guaranteed to be mathematically unique with an overwhelming probability (due to 100 dense CRC16 checksums validating every step). All necessary rules (the exact compressor logic) are public in the solver bundle.
- **Deterministic Grading**: The solver simply outputs the SHA256 hash of the recovered data.
- **No Leakage**: The generator creates the data, compresses it, mutates it, and only provides the corrupted binary.
- **Human Auditable**: A human reverse engineer familiar with dynamic programming can easily construct the pruning logic and recover the file perfectly.

I have executed the `generator.py`, validated the structure with `verifier.py`, and run the `baseline.py` (which just ignorantly attempts to decompress the corrupted stream and scores 0/30). All files including `validation_report.md` and `failure_modes.md` have been generated and the directory is clean.
