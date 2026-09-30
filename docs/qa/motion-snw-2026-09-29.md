# Final visual QA: Inko south and Bunny northwest

Compared each eight-frame 192 × 208 packed WebP with its original identity reference on a checkerboard. Reviewed facing direction, grounded gait, identity, clipping, scale, tail continuity, and the 8-to-1 loop.

| Strip | Verdict | Findings |
| --- | --- | --- |
| Inko `walk-s/packed.webp` | **Accept** | All eight poses face the viewer and retain the navy fur, cream ear curls, closed eyes, chest spiral, and large cream-edged tail. The tail stays on the left of the image without popping. Feet alternate in small, readable steps while every frame reaches y=200. Apparent scale and placement are stable, the loop closes coherently, and no opaque pixels clip a cell. |
| Bunny `walk-nw/packed.webp` | **Accept** | All eight poses show the bunny from behind, turned toward screen left; the white side cheek is visible, but the front face and belly are not. Blue body, pink inner ear, and round white tail match the character. The tail stays on the right; legs and arms alternate, with feet reaching y=200 throughout. Small ear-pose variations do not create a material scale jump or loop seam. No opaque clipping. |

Alpha bounds stay within each cell: Inko x=39–153, y=12–200; Bunny x=44–147, y=12–200. Visual inspection supports the motion and identity verdicts.
