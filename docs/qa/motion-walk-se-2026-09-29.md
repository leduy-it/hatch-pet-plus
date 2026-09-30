# Final visual QA: `walk-se` packed strips

Reviewed the original four-view identity references and all eight 192 × 208 cells in each 1536 × 208 packed WebP. I composited the alpha onto a checkerboard and compared the poses as two full strips. The long colored lines visible in an opaque raw-RGB preview are in fully transparent pixels and disappear under normal alpha compositing.

| Strip | Verdict | Findings |
| --- | --- | --- |
| Inko | **Reject for `walk-se`** | Navy body, curled tail, cream ear marks, and chest spiral remain recognizable across eight frames. The head and torso face southeast consistently, and no opaque pixels clip a cell edge. Scale is stable. However, frames 4 and 8 raise both feet well above the common ground line (opaque bottom at y=184 and y=189 versus y=199–200 in grounded poses). The repeated full-body lift reads as a hop/skip, not a grounded southeast walk. The 8→1 transition also drops the character back to the baseline. Revise those airborne poses and their adjacent transitions into alternating planted steps, then recheck the loop. |
| Bunny | **Accept** | Blue fur, pink ears, face, white belly, and small tail match the identity reference across all eight frames. Three-quarter right-facing body and alternating leg/arm placements read as a southeast walk. All opaque frame bounds stay within the 192 × 208 cell; no clipping or material scale jump is visible. The feet return to the same y=200 baseline, and frame 8 flows naturally back to frame 1. |

Bounds check from WebP alpha: Inko's eight cells occupy x=35–156 and y=12–200 at most; bunny's occupy x=40–152 and y=12–200 at most. These measurements support the visual no-clipping assessment. They do not replace the motion judgment above.

## Inko `packed-v2.webp` reassessment

**Accept.** Compared all eight revised cells with the original identity reference on a checkerboard. The same navy body, curled tail, cream ear markings, face, and chest spiral persist; the three-quarter right-facing body reads southeast. Legs alternate through planted and passing poses, with no full-body airborne phase. Each frame reaches the same y=200 ground line, including frames 4 and 8 that caused the original rejection. The 8→1 transition returns to the opposing step without a vertical snap. Opaque bounds remain inside each cell (x=33–158, y=12–200 across the strip), and apparent size stays consistent. No visible clipping or alpha-composited artifact remains. This acceptance applies to `packed-v2.webp`; the original `packed.webp` verdict above is unchanged.
