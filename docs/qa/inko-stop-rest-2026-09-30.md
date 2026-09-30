# Final visual QA: Inko south stop and seated rest

Reviewed the original four-view identity reference and both packed strips on a checkerboard. Each cell is 192 × 208; `stop-s` has four frames and `rest` has eight.

| Strip | Verdict | Findings |
| --- | --- | --- |
| `stop-s/packed.webp` | **Reject** | All four frames face south and preserve Inko's navy fur, cream ear curls, closed-eye expression, chest spiral, and cream-edged tail. Size, tail side, and the y=200 foot baseline stay consistent, with no opaque clipping. The legs are already close together and planted in frame 1 and remain effectively neutral through frame 4. Small silhouette changes do not show a step decelerating into a stand. The clip would read as a four-frame idle rather than a progressive stop. Start with a clearly advanced/lifted walking foot and ease it down over frames 2–3 before neutral frame 4. |
| `rest/packed.webp` | **Accept** | The character remains seated and front-facing with the same navy, cream-ear, chest-spiral, and curled-tail identity. The closed-eye expression matches the identity reference; a subtle face change near frame 3 and small ear, body, and tail shifts keep the loop gently alive. The seated base stays at y=200, apparent scale is stable, no tail jumps or detached elements appear, and frame 8 returns naturally to frame 1. No opaque clipping. |

Alpha bounds stay within each cell: `stop-s` x=32–159 and y=12–200; `rest` x=32–159 and y=12–200. The stop rejection concerns visible motion progression, not registration or image quality.
