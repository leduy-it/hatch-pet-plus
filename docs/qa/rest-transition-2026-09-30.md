# Final visual QA: Bunny rest and Inko south transition

Reviewed both eight-frame 192 × 208 packed strips on a checkerboard against their original identity references. Inko's `packed-grounded.webp` was judged as delivered after same-scale ground registration.

| Strip | Verdict | Findings |
| --- | --- | --- |
| Bunny `rest/packed.webp` | **Accept** | The bunny remains seated, front-facing, and awake through a gentle idle, with one brief blink in frame 5. Blue fur, pink ears, orange eyes, white cheeks and belly, and small tail details retain identity. The seat/feet stay at y=200. Ear and body changes are modest, frame 8 returns naturally to frame 1, and there is no opaque clipping or material scale jump. |
| Inko `transition-s/packed-grounded.webp` | **Reject** | The front-facing navy character, cream ear curls, chest spiral, and tail are consistent, and all eight frames now reach y=200 without clipping. The motion still has a visible height pop: the top changes from y=20 in frame 3 to y=11 in frame 4, then from y=12 in frame 5 to y=20 in frame 6. This makes the body appear to spring taller and shorter around the start/stop split despite the aligned feet. Frames 6–8 also settle near neutral too early, leaving little progressive deceleration across the four-frame stop clip. Rework the pose progression in frames 3–7; ground registration alone does not resolve this motion issue. |

Alpha bounds across the strips: Bunny x=42–149, y=12–200; Inko x=39–153, y=11–200. Both strips contain eight cells and have safe margins. The Inko rejection concerns visible pose timing and stature change, not clipping or identity.
