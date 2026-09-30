# Final visual QA: Bunny sleep

Reviewed all eight 192 × 208 frames in `bunny/sleep/packed.webp` on a checkerboard against the original identity reference.

**Verdict: Accept the animation asset.** The bunny stays curled on the ground with eyes closed, head resting near its paws, folded pink ears, blue fur, white cheek/belly, and white tail. The body and ears change slightly through the eight poses, giving a quiet breathing loop; frame 8 returns coherently to frame 1. No detached decorations or stray opaque elements are visible. All frames reach the same y=200 baseline, remain similarly sized, and stay inside their cells (alpha bounds x=8–184, y=77–200 across the strip).

**Display-size note:** At a shared sprite scale, the sleeping pose will occupy about 172–176 px of its 192 px cell horizontally, compared with about 85–90 px for the standing identity silhouette and 132 px for the side-view reference. The wider footprint is partly natural for a lying pose, but it may look oversized beside idle in the app. Preview at the registered shared scale; a sleep-specific display scale around 0.8–0.85, anchored to the same ground line, is likely needed if the visual size feels inconsistent. This is a presentation adjustment, not a rejection of the packed frames.
