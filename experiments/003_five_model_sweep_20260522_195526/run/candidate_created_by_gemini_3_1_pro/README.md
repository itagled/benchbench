# Polyhedral Surface Traversal Benchmark

Tests spatial reasoning and coordinate tracking over a 3D folded cube.

Closest existing benchmarks: SpatialSense, Dynabench.

This benchmark is distinct because it requires exact simulation of 2D to 3D mapping with complex orientation inversions across net edges. Tool-using LLMs that rely on quickly written Python scripts frequently fail due to the subtle coordinate reflections required at folded edges.
