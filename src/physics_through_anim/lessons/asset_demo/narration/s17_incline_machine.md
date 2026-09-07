# Scene 17 — One machine, minimal code

TODO narration (draft): Here is a whole machine on an incline: a fixed support,
a spring, a block, a second spring, a rope that wraps a pulley at the top, and a
mass hanging on the other side. Every piece is a library asset, wired only by its
endpoints — the spring knows its two ends, the rope knows where it leaves the
pulley, the block knows its edges. When the hanging mass is released it falls and
hauls the block up the ramp, stretching both springs while the rope stays taut
over the pulley. One tracker couples the whole chain; nothing recomputes anyone
else's geometry. That is the point: rich, correct scenes from very little code.
