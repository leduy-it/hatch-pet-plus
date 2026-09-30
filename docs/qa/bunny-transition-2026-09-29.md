# Final visual QA: Bunny south start/stop transition

Reviewed the eight 192 × 208 cells in `bunny/transition-s/packed.webp` on a checkerboard against the original identity reference and the accepted south walk. Frames 1–4 are intended as the start clip; frames 5–8 as the stop clip.

**Verdict: Reject for the intended two-clip transition.**

| Frames | Assessment |
| --- | --- |
| 1–4 start | Acceptable progression: frame 1 is neutral front standing, frame 2 begins arm/body motion, frame 3 advances a foot, and frame 4 reaches a grounded first-step pose. |
| 5–8 stop | Frame 5 is still in the step pose, but frame 6 is already neutral; frames 7 and 8 remain visually near-neutral. The braking action is concentrated in 5→6 instead of easing across the four frames. As a standalone stop clip this reads as a snap followed by a hold. Add intermediate retreating-foot/settling poses in frames 6–7, then let frame 8 reach neutral. |

Identity stays consistent: blue fur, pink ears, orange eyes, white cheeks and belly, and smiling front face. All eight frames are grounded (opaque bottom y=200), similarly scaled, and unclipped. Alpha bounds are x=46–145 and y=12–200 across the strip. The rejection is for stop-motion progression, not image bounds or identity.

## Reassessment: `transition-s/packed-v2.webp`

**Verdict: Accept the repaired two-clip transition.** Frames 1–4 now progress from neutral standing, through arm motion and a lifted foot, to a grounded first step. Frames 5–8 progress from a step through a forward foot and settling pose to neutral standing; the stop no longer snaps to neutral early. The front-facing Bunny identity remains consistent, and both four-frame clips read as continuous motion. All eight cells are grounded (opaque bottom y=199–200), similarly scaled, and unclipped; alpha bounds across the strip are x=42–150, y=12–200. This acceptance applies to `packed-v2.webp`; the original `packed.webp` rejection above remains recorded.
