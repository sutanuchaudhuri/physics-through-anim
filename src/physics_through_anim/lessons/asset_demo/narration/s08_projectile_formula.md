# Scene 08 — Projectile from a formula (assets consume, never integrate)

TODO narration (draft): The ball does not solve any physics. A trajectory — here
a simple parabola formula — is asked for the complete state at each moment in
time, and the framework just places the ball there. The same mechanism accepts a
formula, a NumPy or SciPy solution, a CSV of samples, or values checked by a
model. At the top of the arc we freeze the frame: the velocity is purely
horizontal, because the vertical velocity has dropped to zero. The solver
supplies the numbers; the animation only carries and shows them.
