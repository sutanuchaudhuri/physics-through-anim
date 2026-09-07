# Scene 20 — Counting collisions

TODO narration (draft): A heavy block slides toward a light block that sits
between it and a wall. Every collision is perfectly elastic. The light block gets
knocked into the wall, bounces back, is struck again, and so on. Each impact is a
sudden jump in velocity — the speeds change instantly, but the positions never
teleport. Off to the side we count the impacts and plot each pair of velocities.
Because energy is conserved, those points all lie on a circle, and each collision
is a reflection around it. Remarkably, the total number of collisions, for mass
ratios that are powers of one hundred, spells out the digits of pi. The framework
only renders the schedule; a tiny solver decides what each impact does.
