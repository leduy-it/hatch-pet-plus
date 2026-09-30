# Final visual QA: Inko northwest and Bunny southwest

Compared each eight-frame 192 × 208 packed WebP with its original identity reference on a checkerboard. Reviewed direction, grounded gait, identity, tail continuity, scale, clipping, and the 8-to-1 loop.

| Strip | Verdict | Findings |
| --- | --- | --- |
| Inko `walk-nw/packed.webp` | **Accept** | All eight frames show the character from behind, turned toward screen left, without front facial or chest features. Navy fur, cream ear curls, and the large cream-edged tail preserve identity. The tail stays on the right of the image and changes smoothly; legs alternate while the feet reach y=198–200. The small baseline variation reads as a normal step, with no airborne pose, scale jump, clipping, or visible loop seam. |
| Bunny `walk-sw/packed.webp` | **Accept** | All eight frames show a front three-quarter view toward screen left. Blue fur, pink ears, orange eyes, white cheeks and belly, and smiling mouth match the identity reference. The small tail stays on the right side, arms and legs alternate, and feet reach y=199–200. Frame size and placement remain stable, with no opaque clipping or visible 8-to-1 discontinuity. |

Alpha bounds remain inside every cell: Inko x=38–154, y=12–200; Bunny x=47–145, y=12–200. Visual pose inspection supports the direction and motion verdicts.
