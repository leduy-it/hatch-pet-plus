# Final visual QA: Inko south start

Reviewed all four 192 × 208 cells in `inko/start-s/packed.webp` on a checkerboard and at 2× size, alongside the original identity reference and the accepted south walk.

**Start verdict: Accept.** Frame 1 is a planted neutral stance; frame 2 shifts weight and separates the feet; frames 3–4 visibly lift and advance one foot into a small first step. The movement is subtle but readable at native size. The front-facing navy character retains cream ear curls, closed-eye expression, chest spiral, and cream-edged tail. The tail stays on the image left, head and torso height remain stable (all frame tops y=12), every frame reaches the y=200 baseline, and no opaque pixels clip a cell. Alpha bounds across the strip are x=32–160, y=12–200.

**Reverse-as-stop verdict: Accept for a gentle stop from this small step.** Playing frames 4→3→2→1 lowers the raised foot, returns weight toward center, and ends on planted neutral. There is no height snap or tail-side change. This judgment concerns the four-frame clip itself; the runtime handoff from a particular walk frame should still use a matching foot phase.
