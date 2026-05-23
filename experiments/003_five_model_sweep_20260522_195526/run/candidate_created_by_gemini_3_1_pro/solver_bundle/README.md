# Polyhedral Surface Traversal Benchmark

In this benchmark, you are tracing the path of a turtle moving on the surface of a folded 3x3x3 cube.

## The Net
The cube is formed by folding a 2D net consisting of 6 faces: A, B, C, D, E, F.
In the flattened 2D net, they are arranged in a cross:
```
      [Face A]
[Face C][Face B][Face D]
      [Face E]
      [Face F]
```

- Face B is the central Front face.
- Face A connects to Face B's top edge.
- Face E connects to Face B's bottom edge.
- Face C connects to Face B's left edge.
- Face D connects to Face B's right edge.
- Face F connects to Face E's bottom edge.

Each face is a 3x3 grid of cells. Within each face:
- Cell (0, 0) is the top-left corner.
- Row indices (0, 1, 2) increase from top to bottom.
- Column indices (0, 1, 2) increase from left to right.

## Folding Rules
The net is folded into a solid cube such that the printed text is on the OUTSIDE of the cube.
All folds between adjacent faces in the net are exactly 90 degrees away from the viewer.

## Turtle Movement
You are given an initial state: the starting Face, row, col, and the local direction the turtle is facing (Up, Down, Left, or Right).
- "Up" means facing towards decreasing row index.
- "Down" means facing towards increasing row index.
- "Left" means facing towards decreasing column index.
- "Right" means facing towards increasing column index.

You are given a sequence of commands:
- `M`: Move forward 1 cell in the current facing direction.
- `L`: Turn left 90 degrees in place.
- `R`: Turn right 90 degrees in place.

When moving off the edge of a face, the turtle seamlessly crosses onto the adjacent face on the 3D cube. Its new local position and local facing direction must be correctly determined by the 3D geometry of the folded cube.

## Your Task
For each item, you are given the contents of each cell on each face, the initial state, and a list of commands.
You must find the contents of the final 4 cells the turtle lands on after executing the `M` commands.
Your answer should be formatted as the 4 cell contents joined by hyphens.
For example, if the last 4 cells you moved into contain "XX", "YY", "ZZ", and "WW", your answer is "XX-YY-ZZ-WW".
Note: The final sequence strictly records the contents of the cells landed on for the last 4 `M` commands, in chronological order. Turns do not change the cell you are on and do not add to the visited sequence.

Solve the items and output your predictions in a JSONL file with `id` and `answer`.
