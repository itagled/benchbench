# Failure Modes

1. **Incorrect Edge Connections:** Models writing scripts may incorrectly identify which face connects to which across the cut edges of the net. For example, connecting the Top face to the Back face incorrectly.
2. **Coordinate Reflection Errors:** When crossing an edge like Left to Back, the row coordinates map in an inverted manner (e.g., row 0 on the Left face meets row 2 on the Back face). Models often fail to account for this and write naive `r_new = r_old` mappings.
3. **Orientation Errors:** Models may fail to track the new local direction after crossing an edge. For instance, moving "Left" off the Left face enters the Back face moving "Right".
4. **Instruction Misinterpretation:** Models might get confused between turning left/right and moving left/right on the grid.
5. **Context Window Limitations:** The raw grid data and long sequence of 40 commands might cause simpler models to lose track of the state if they try to perform it purely in-context without code execution.
