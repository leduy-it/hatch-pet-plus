# Final visual QA: Inko southwest repair and sleep

Reviewed both eight-frame 192 × 208 packed strips on a checkerboard against the original Inko identity sheet.

| Strip | Verdict | Findings |
| --- | --- | --- |
| `walk-sw/packed-v2.webp` | **Accept** | The repaired head and muzzle clearly point screen left while the visible chest and near arm keep the body turned toward the viewer. The navy fur, cream ear curl, chest spiral, closed eye, and large cream-edged tail preserve identity. Legs alternate through grounded steps (opaque bottoms y=198–200); the tail stays on the image right without popping. Apparent scale is stable, frame 8 loops cleanly to 1, and no opaque pixels clip a cell. This resolves the original strip's directional rejection. |
| `sleep/packed.webp` | **Reject** | The curled body, closed eyes, chest spiral, navy fur, cream ear curls, and wrapped tail preserve identity; the body stays grounded at y=200 without clipping. The ear pose changes are too large for subtle breathing: upright in frame 1, partly folded in 2, nearly flattened in 3, upright again in 4–5, folded again in 6–7, and upright in 8. The opaque top swings from y=12 to y=45–47, making two abrupt ear-flop cycles and a visible 8-to-1 discontinuity. Keep the ears mostly stable and put the breathing motion into a small torso/head rise and fall, then recheck the loop. |

Alpha bounds remain inside each cell: southwest x=30–161, y=12–200; sleep x=8–184, y=12–200. The sleep rejection concerns animation amplitude and continuity, not identity or clipping.

## Sleep repair: `sleep/packed-v2.webp`

**Verdict: Accept.** Rechecked all eight repaired frames against the original identity and prior sleep strip. The ears hold one relaxed angle throughout instead of repeatedly folding flat and springing upright. Closed eyes, cream ear curls, chest spiral, navy body, and wrapped cream-edged tail remain recognizable. Small body and tail changes now read as gentle breathing, with a smooth 8-to-1 return. The curled body stays grounded at y=200, apparent scale remains consistent, and no opaque clipping or detached decoration is visible. Alpha bounds across the strip are x=8–184, y=25–200. This acceptance applies to `packed-v2.webp`; the original `packed.webp` verdict above remains rejected.
