# Final visual QA: Inko carry

Reviewed all eight 192 × 208 cells in `inko/carry/packed.webp` on a checkerboard and at enlarged size against the original identity reference. The requested direction is southeast: toward the viewer and screen right.

**Verdict: Reject for southeast direction.** In every frame the muzzle and head turn toward screen left, while the large curled tail stays on screen right. The body therefore reads as a southwest/front-left carry, not southeast/front-right. Reorient the head and torso to the right-facing three-quarter view and place the tail consistently on the opposite visible side, keeping the current parcel grip and step timing.

The other requirements pass: navy fur, cream ear curls, closed-eye expression, chest spiral, and cream-edged tail preserve identity. The warm wood parcel stays at chest height and visibly touches both paws in all eight frames, with no size or position jump. Feet alternate in a grounded slow gait and reach y=200 throughout. Apparent scale is stable, frame 8 returns coherently to frame 1, and no opaque pixels clip a cell. Alpha bounds across the strip are x=38–154, y=12–200.

## Direction reclassification

**Verdict: Accept as a southwest carry.** The screen-left muzzle and three-quarter front body angle establish a readable southwest heading in every frame; the large tail stays consistently on screen right. The wood parcel remains in both paws through the grounded eight-frame gait, and the identity, scale, clipping, and loop checks above pass. This strip can be registered as `sw` for a carry feature that needs one consistent direction. The original southeast verdict remains rejected because the artwork does not face screen right.
