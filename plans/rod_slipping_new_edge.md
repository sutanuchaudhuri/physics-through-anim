# FALLING ROD AT A TABLE EDGE

## Detailed scene-by-scene physics, graphs, slip condition, energy, kinematics, separation, spins and impact orientation

---

# 0. The physical story

Consider a uniform rod of

$$
\text{mass}=m,\qquad \text{length}=L
$$

standing almost vertically near a rough table edge.

Let:

* \(P\) = lower end/contact point,
* \(G\) = center of mass,
* \(\theta\) = angle measured from vertical,
* \(\omega=\dot\theta\),
* \(\alpha=\ddot\theta\).

The story passes through several phases:

$$
\boxed{
\text{static contact}
\rightarrow
\text{slipping contact}
\rightarrow
\text{edge contact}
\rightarrow
\text{separation}
\rightarrow
\text{free-flight rotation}
\rightarrow
\text{ground impact}
}
$$

The video must make an important point:

> We do NOT use one equation for the entire motion.

Every time the constraint changes, the equations have to be reconsidered.

---

# SCENE 1 — The rod is almost vertical

## Visual

Show table.

Rod almost vertical.

Lower endpoint:

$$
P
$$

Center:

$$
G
$$

Angle:

$$
\theta_0\simeq2^\circ
$$

rather than exactly zero.

Display:

$$
I_G=\frac1{12}mL^2
$$

and

$$
I_P=\frac13mL^2.
$$

---

## Narration

“Consider a uniform rod standing almost vertically on a rough table.”

“We give it a tiny initial tilt.”

“If it were perfectly vertical, perfectly motionless, and perfectly rigid, gravity would produce zero torque about its foot.”

“So an exactly vertical rod would not spontaneously choose a direction in our ideal model.”

“Real disturbances provide the tiny initial displacement. In our simulation, we introduce it explicitly.”

---

# SCENE 2 — Why gravity creates rotation

Freeze at small angle \(\theta\).

Show gravity:

$$
mg
$$

through \(G\).

Show perpendicular lever arm from \(P\) to gravity's line of action:

$$
\frac L2\sin\theta.
$$

Therefore:

$$
\tau_P
=
mg\frac L2\sin\theta.
$$

## Narration

“Once the rod tilts, gravity no longer passes through the foot.”

“So gravity acquires a moment arm.”

“As the angle increases, that moment arm initially increases.”

“And gravity begins angularly accelerating the rod.”

---

# SCENE 3 — First FBD

Freeze the physical rod.

Move a copy beside it and strip away the table.

Show:

$$
mg
$$

at \(G\),

$$
N
$$

at \(P\),

and

$$
f_s
$$

at \(P\).

Now ask:

## WHICH POINT SHOULD WE TAKE TORQUE ABOUT?

Show two candidates:

$$
P
\qquad\text{or}\qquad
G.
$$

---

# SCENE 4 — Why calculate torque about the contact point?

This deserves its own scene.

## About \(G\)

Gravity passes through \(G\).

Therefore gravity contributes no torque about \(G\).

But the unknown forces

$$
N,\qquad f_s
$$

both generally produce torques.

Thus:

$$
I_G\alpha
=
\tau_N+\tau_f.
$$

This is completely correct.

---

## About \(P\)

Now move the torque marker to the contact.

Both contact forces pass through \(P\).

Therefore:

$$
\tau_N=0,
\qquad
\tau_f=0.
$$

Only gravity remains.

Thus:

$$
\sum\tau_P
=
mg\frac L2\sin\theta.
$$

While \(P\) is fixed:

$$
\sum\tau_P=I_P\alpha.
$$

Therefore:

$$
\frac13mL^2\alpha
=
mg\frac L2\sin\theta.
$$

Hence:

$$
\boxed{
\alpha=
\frac{3g}{2L}\sin\theta
}
$$

---

## Narration

“We are not choosing the contact point because torque must always be calculated there.”

“We choose it because it makes this particular calculation dramatically easier.”

“The two unknown contact forces disappear from the torque equation.”

“Torque about the center of mass would give exactly the same physics, but we would have to calculate the normal force and friction simultaneously.”

---

# SCENE 5 — Important warning: this trick has an expiration date

Put a lock symbol on \(P\).

Label:

### FIXED IN AN INERTIAL FRAME

Write:

$$
\sum\tau_P=I_P\alpha.
$$

Then show \(P\) starting to slide.

Break the lock.

Cross out the simple equation.

## Narration

“But this shortcut works in this simple form because the foot is currently fixed.”

“Once the contact point starts accelerating, we cannot blindly keep writing torque equals \(I_P\alpha\) about that moving point.”

“The center-of-mass equation remains safe.”

Show:

$$
\boxed{
\sum\tau_G=I_G\alpha
}
$$

for all planar rigid-body phases.

For an arbitrary point \(P\),

$$
\sum\tau_P
=
I_G\alpha
+
\vec r_{G/P}\times m\vec a_G.
$$

So the missing translational term matters once \(P\) is not a fixed pivot.

---

# SCENE 6 — Use ENERGY before using time

This is where the video should teach an important solution strategy.

Start with:

$$
\alpha(\theta)
$$

known.

But ask:

### HOW FAST IS THE ROD ROTATING AT ANGLE \(\theta\)?

Instead of immediately integrating \(\alpha(t)\), use energy.

While \(P\) is fixed:

* \(N\) does no work,
* static friction does no work,
* gravity is conservative.

Therefore mechanical energy is conserved.

---

## Height of CM

$$
y_G=\frac L2\cos\theta.
$$

For an initial angle \(\theta_0\) released from rest:

$$
mg\frac L2\cos\theta_0
=
mg\frac L2\cos\theta
+
\frac12I_P\omega^2.
$$

Substitute:

$$
I_P=\frac13mL^2.
$$

Then:

$$
\boxed{
\omega^2
=
\frac{3g}{L}
\left(
\cos\theta_0-\cos\theta
\right)
}
$$

For the limiting idealization

$$
\theta_0\rightarrow0,
$$

this becomes

$$
\boxed{
\omega^2
=
\frac{3g}{L}(1-\cos\theta)
}
$$

---

## Narration

“Torque gave us angular acceleration.”

“But energy gives us angular velocity as a function of angle almost immediately.”

“This is exactly the kind of situation where energy is more efficient than trying to solve the time-dependent differential equation first.”

---

# SCENE 7 — Energy visualization

Show three continuously changing bars:

### Gravitational potential energy

$$
U=mg\frac L2\cos\theta
$$

decreasing.

### Rotational kinetic energy

$$
K=\frac12I_P\omega^2
$$

increasing.

### Total

constant.

Narration:

“Before slipping, static friction does no work because the point where it acts is stationary.”

“So gravitational potential energy is converted into rotational kinetic energy.”

---

# SCENE 8 — Now use kinematics to recover time

We know

$$
\omega=\frac{d\theta}{dt}.
$$

Therefore:

$$
dt=\frac{d\theta}{\omega(\theta)}.
$$

So:

$$
\boxed{
t(\theta)
=
\int_{\theta_0}^{\theta}
\frac{d\phi}
{
\sqrt{
\omega_0^2+
\frac{3g}{L}
(\cos\theta_0-\cos\phi)
}
}
}
$$

For release from rest:

$$
\omega_0=0.
$$

---

## Important animation point

Do NOT start numerically at

$$
\theta_0=0,\quad\omega_0=0.
$$

That is an exact unstable equilibrium.

Use something such as

$$
\theta_0=2^\circ.
$$

---

## Narration

“Energy gave us velocity as a function of position.”

“Kinematics now converts position into time.”

“This integral does not need to be forced into an elementary closed form.”

“For the animation, the physics engine evaluates it numerically.”

---

# SCENE 9 — First live graph: angular velocity versus time

Place a graph on the right.

Horizontal:

$$
t
$$

Vertical:

$$
\omega.
$$

Rod runs on left.

A moving vertical cursor follows the animation time.

The plotted curve initially rises.

At every frame:

$$
\omega(t)
=
\sqrt{
\frac{3g}{L}
(\cos\theta_0-\cos\theta(t))
}.
$$

### Narration

“As gravitational potential energy is released, angular velocity continuously increases.”

“Notice that angular velocity itself cannot suddenly jump under ordinary finite forces.”

That statement becomes important at slipping and separation.

---

# SCENE 10 — Second live graph: angular acceleration

Below or in a later dedicated frame show

$$
\alpha(t).
$$

During fixed-pivot motion:

$$
\boxed{
\alpha(t)
=
\frac{3g}{2L}\sin\theta(t)
}
$$

For the angles relevant before slipping, this generally rises as \(\theta\) increases.

### Narration

“Angular acceleration tells a different story.”

“It depends directly on the instantaneous torque.”

“So unlike angular velocity, angular acceleration can change abruptly when the contact forces or constraints change.”

This prepares the viewer for the slip transition.

---

# SCENE 11 — How do we calculate when the foot starts slipping?

This must be a major derivation scene.

The incorrect method should first appear:

$$
F_{\rm friction}=\mu_sN.
$$

Cross it out.

Replace with:

$$
|f_s|\leq\mu_sN.
$$

### Narration

“The rod starts slipping not because some particular angle has been memorized.”

“It slips when the static friction required by the assumed fixed-foot motion becomes larger than the maximum friction the contact can supply.”

Therefore we need:

$$
f_{\rm required}(\theta)
$$

and

$$
N(\theta).
$$

---

# SCENE 12 — Find acceleration of the center of mass

With \(P\) fixed:

$$
x_G=\frac L2\sin\theta,
$$

$$
y_G=\frac L2\cos\theta.
$$

Differentiate once:

$$
v_{Gx}
=
\frac L2\omega\cos\theta,
$$

$$
v_{Gy}
=
-\frac L2\omega\sin\theta.
$$

Differentiate again:

$$
\boxed{
a_{Gx}
=
\frac L2
\left(
\alpha\cos\theta
-
\omega^2\sin\theta
\right)
}
$$

and

$$
\boxed{
a_{Gy}
=
-\frac L2
\left(
\alpha\sin\theta
+
\omega^2\cos\theta
\right)
}
$$

---

## Visual explanation

Do not just show differentiation.

Show the two acceleration components geometrically:

### Tangential

$$
a_t=\alpha\frac L2
$$

perpendicular to rod.

### Radial

$$
a_r=\omega^2\frac L2
$$

toward \(P\).

Then vector-add them.

Narration:

“The center of mass has both tangential acceleration from angular acceleration and centripetal acceleration from the already-existing angular velocity.”

---

# SCENE 13 — Calculate the required static friction

Horizontal Newton equation:

$$
f_s=ma_{Gx}.
$$

Therefore:

$$
f_s
=
m\frac L2
\left(
\alpha\cos\theta
-
\omega^2\sin\theta
\right).
$$

For the limiting start from nearly vertical:

$$
\alpha=
\frac{3g}{2L}\sin\theta,
$$

and

$$
\omega^2=
\frac{3g}{L}(1-\cos\theta).
$$

Substitute.

After simplification:

$$
\boxed{
f_s(\theta)
=
\frac{3mg}{4}
\sin\theta
(3\cos\theta-2)
}
$$

This is the **friction required to keep the foot fixed**.

Not the maximum available friction.

---

# SCENE 14 — Calculate the normal force

Vertical Newton equation:

$$
N-mg=ma_{Gy}.
$$

Substitute the CM acceleration.

For the nearly vertical limiting start:

$$
\boxed{
N(\theta)
=
\frac{mg}{4}
(3\cos\theta-1)^2
}
$$

Now show both functions simultaneously.

---

# SCENE 15 — The friction-demand graph

This should be one of the most important graphical scenes.

Plot:

$$
\frac{|f_{\rm required}|}{N}
$$

against \(\theta\).

Because slipping is possible only if:

$$
\frac{|f_{\rm required}|}{N}
\leq\mu_s.
$$

Using the formulas:

$$
\boxed{
\frac{|f_s|}{N}
=
\frac{
3\sin\theta
|3\cos\theta-2|
}{
(3\cos\theta-1)^2
}
}
$$

Add a horizontal line:

$$
y=\mu_s.
$$

The FIRST intersection encountered as \(\theta\) grows is the slip angle.

---

# SCENE 16 — Exact equation for the slip angle

The condition is:

$$
|f_s|=\mu_sN.
$$

Therefore:

$$
\boxed{
3\sin\theta_s
|3\cos\theta_s-2|
=
\mu_s
(3\cos\theta_s-1)^2
}
$$

This is the equation the physics agent solves numerically.

### Narration

“This equation determines the slip angle.”

“The important word is first.”

“If the mathematical curves cross more than once, only the first crossing reached during the actual motion determines the beginning of slipping.”

---

# SCENE 17 — A surprising friction reversal

Before slip, provided the coefficient is large enough to keep the contact static this long:

$$
f_s=
\frac{3mg}{4}
\sin\theta
(3\cos\theta-2).
$$

So friction becomes zero when:

$$
3\cos\theta-2=0.
$$

Thus:

$$
\boxed{
\cos\theta=\frac23
}
$$

or

$$
\boxed{
\theta\simeq48.19^\circ
}
$$

Then its direction reverses.

### Narration

“This falling rod gives us another striking lesson.”

“Even while the foot remains stationary, the direction of static friction can reverse.”

“At small angles, tangential acceleration dominates.”

“At larger angles, the centripetal component becomes strong enough to change the horizontal acceleration required of the center of mass.”

“So the static-friction direction changes.”

---

# SCENE 18 — Example slip calculation

For animation purposes, choose explicit values.

For example:

$$
\mu_s=0.30.
$$

Solving

$$
3\sin\theta
|3\cos\theta-2|
=
0.30(3\cos\theta-1)^2
$$

gives the first crossing at approximately

$$
\boxed{
\theta_s\approx24.2^\circ
}
$$

for the nearly vertical limiting initial condition.

Label clearly:

### ILLUSTRATIVE EXAMPLE: \(\mu_s=0.30\)

Do not present \(24.2^\circ\) as a universal result.

---

# SCENE 19 — Static friction limit reached

Run the rod animation.

The friction-demand graph's cursor approaches the \(\mu_s\) line.

At:

$$
\theta=\theta_s,
$$

freeze.

Show:

$$
|f_s|=\mu_sN.
$$

Narration:

“This is the last instant for which the fixed-foot solution is physically possible.”

“Beyond it, the mathematical solution would demand more static friction than nature can provide.”

---

# SCENE 20 — The instant after slip begins

The lower endpoint begins moving.

Change:

$$
f_s
$$

to

$$
f_k.
$$

For Coulomb kinetic friction:

$$
|f_k|=\mu_kN.
$$

Now remove:

$$
x_P=\text{constant}.
$$

### Very important

$$
\omega
$$

does NOT jump.

Show the \(\omega(t)\) graph passing smoothly through the transition.

But:

$$
\alpha
$$

can jump.

Show a kink/discontinuity in the \(\alpha(t)\) graph if the calculated dynamics produces one.

### Narration

“The position cannot jump.”

“The orientation cannot jump.”

“The linear velocity cannot jump.”

“And the angular velocity cannot jump merely because static friction became kinetic friction.”

“But acceleration and angular acceleration can change immediately because the forces have changed.”

---

# SCENE 21 — Why energy conservation changes after slipping

Before slip:

$$
E_{\rm mech}=\text{constant}.
$$

After slip:

kinetic friction performs negative work.

The instantaneous power dissipated is:

$$
\boxed{
\dot E_{\rm mech}
=
-\mu_kN|v_{\rm slip}|
}
$$

for simple Coulomb sliding.

### Visual

Energy graph:

Phase I:

flat.

Phase II:

decreasing.

### Narration

“We can no longer equate lost gravitational potential energy entirely to kinetic energy.”

“Some mechanical energy is now converted into thermal energy at the sliding contact.”

So during slipping:

$$
\Delta K+\Delta U=W_{\rm friction}.
$$

---

# SCENE 22 — The correct equations after slip

This is where the animation architecture should switch solvers.

Always use:

$$
\boxed{
m\vec a_G
=
m\vec g+\vec F_{\rm contact}
}
$$

and

$$
\boxed{
I_G\alpha
=
\vec r_{P/G}\times
\vec F_{\rm contact}
}
$$

where

$$
\vec F_{\rm contact}
=
N\hat n+f\hat t.
$$

For kinetic sliding:

$$
\boxed{
\vec f
=
-\mu_kN
\frac{\vec v_{\rm rel,t}}
{|\vec v_{\rm rel,t}|}
}
$$

and while contact persists:

$$
\vec v_P\cdot\hat n=0.
$$

These equations work whether the rod is touching:

* the horizontal top,
* a rounded corner,
* the vertical side.

Only

$$
\hat n,\qquad\hat t
$$

change.

---

# SCENE 23 — Sliding toward and around the table edge

Show the contact magnifier.

As the endpoint approaches the edge:

* contact point moves,
* normal direction changes,
* tangent direction changes,
* friction remains tangent,
* normal remains perpendicular.

This is an ideal place to use a slightly rounded corner in the model.

Narration:

“The surface geometry is now part of the mechanics.”

“The direction of the contact force must follow the local surface.”

---

# SCENE 24 — Sliding down the vertical edge

Freeze after the contact has moved onto the vertical face.

Draw a new FBD from scratch.

Do NOT rotate the old FBD automatically without explanation.

If the endpoint is sliding downward:

* normal is horizontal,
* kinetic friction is upward,
* gravity is downward at \(G\).

Narration:

“This looks like the same rod, but it is a different constrained problem.”

“The normal force has changed direction.”

“So the torque created by the contact force has changed as well.”

---

# SCENE 25 — Live \(\omega(t)\) and \(\alpha(t)\) during edge contact

Run both graphs continuously.

## Angular velocity

The value depends on the integrated contact torque:

$$
\omega(t)
=
\omega_s+
\int_{t_s}^{t}\alpha(t')\,dt'.
$$

It may:

* continue increasing,
* increase more slowly,
* become nearly constant,
* or even decrease,

depending on geometry and friction.

Do NOT pre-script the graph shape.

Use the actual dynamics.

---

## Angular acceleration

Calculate:

$$
\boxed{
\alpha
=
\frac{
\vec r_{P/G}\times\vec F_{\rm contact}
}{
I_G
}
}
$$

every frame.

### Narration

“Once slipping begins, there is no universal statement that the rod must angularly accelerate faster.”

“The contact force can either increase or decrease the angular speed.”

“The equations decide.”

---

# SCENE 26 — When does the rod actually leave the table?

This deserves another conceptual pause.

A contact surface can:

$$
\text{push}
$$

but cannot:

$$
\text{pull}.
$$

Therefore:

$$
N\geq0.
$$

While solving the constrained motion, watch \(N(t)\).

When:

$$
\boxed{N=0},
$$

freeze.

Narration:

“This is the physical separation condition.”

“If continuing the constrained solution would require \(N<0\), the table would have to pull the rod toward itself.”

“It cannot.”

“So the contact constraint disappears.”

---

# SCENE 27 — Exact separation state

At the instant of separation record six quantities:

$$
x_{G0},
$$

$$
y_{G0},
$$

$$
v_{Gx,0},
$$

$$
v_{Gy,0},
$$

$$
\theta_0,
$$

$$
\omega_0.
$$

Better names for the code:

* `x_sep`
* `y_sep`
* `vx_sep`
* `vy_sep`
* `theta_sep`
* `omega_sep`

These completely determine the subsequent free-flight motion.

---

# SCENE 28 — What happens to the graphs at separation?

This should be visually dramatic.

At separation:

$$
N\rightarrow0,
$$

$$
f\rightarrow0.
$$

Only gravity remains.

About \(G\):

$$
\tau_G=0.
$$

Therefore:

$$
\boxed{\alpha=0}.
$$

---

## Angular-acceleration graph

The curve reaches the separation time.

Then becomes exactly:

$$
\boxed{\alpha(t)=0}
$$

for the remainder of free flight.

---

## Angular-velocity graph

Because:

$$
\frac{d\omega}{dt}=0,
$$

the graph becomes horizontal:

$$
\boxed{
\omega(t)=\omega_{\rm sep}
}
$$

The line remains continuous at separation.

---

# SCENE 29 — The combined graph should look conceptually like this

Do not hard-code the middle section before solving it.

### \(\omega(t)\)

Phase A — static contact:

increases smoothly.

Phase B — slipping/contact:

continues according to integrated torque.

Phase C — free flight:

horizontal line.

Mark:

$$
t_s=\text{slip}
$$

and

$$
t_{\rm sep}=\text{separation}.
$$

---

### \(\alpha(t)\)

Phase A:

$$
\frac{3g}{2L}\sin\theta(t).
$$

At slipping:

possible jump.

Phase B:

dynamically varying.

At separation:

drops to

$$
0.
$$

Phase C:

stays

$$
0.
$$

---

# SCENE 30 — Free-flight translation

Once airborne:

$$
x_G(\tau)
=
x_{\rm sep}
+
v_{x,\rm sep}\tau,
$$

$$
\boxed{
y_G(\tau)
=
y_{\rm sep}
+
v_{y,\rm sep}\tau
-
\frac12g\tau^2
}
$$

where

$$
\tau=t-t_{\rm sep}.
$$

The center of mass follows a parabola.

Narration:

“The center of mass has become an ordinary projectile.”

---

# SCENE 31 — Free-flight rotation

At the same time:

$$
\alpha=0.
$$

Therefore:

$$
\boxed{
\theta(\tau)
=
\theta_{\rm sep}
+
\omega_{\rm sep}\tau
}
$$

and

$$
\boxed{
\omega(\tau)=\omega_{\rm sep}
}
$$

Narration:

“The translation is accelerated by gravity.”

“The rotation is not.”

“The rod simply keeps the angular velocity it already had.”

---

# SCENE 32 — Energy in free flight

Now mechanical energy becomes conserved again.

$$
E=
\frac12mv_G^2
+
\frac12I_G\omega^2
+
mgy_G.
$$

Because

$$
\omega=\text{constant},
$$

the rotational kinetic energy

$$
\frac12I_G\omega^2
$$

is separately constant.

The changing gravitational potential energy goes into translational kinetic energy.

This creates a beautiful three-phase energy plot:

### Before slip

$$
E_{\rm mech}=\text{constant}.
$$

### During kinetic sliding

$$
E_{\rm mech}\downarrow.
$$

### After separation

$$
E_{\rm mech}=\text{constant again}.
$$

---

# SCENE 33 — How long is the rod in the air?

A tempting approximation is to track only the CM and solve:

$$
y_G=0.
$$

But that gives the time when the CENTER reaches ground level.

The rod will normally hit with an END before that.

So this is not the correct impact condition.

Cross out:

$$
y_G=0.
$$

---

# SCENE 34 — Coordinates of both endpoints

Let endpoint \(A\) and endpoint \(B\) be separated from \(G\) by \(L/2\).

Then:

$$
y_A(\tau)
=
y_G(\tau)
+
\frac L2\cos\theta(\tau),
$$

$$
y_B(\tau)
=
y_G(\tau)
-
\frac L2\cos\theta(\tau).
$$

Substitute:

$$
\theta(\tau)
=
\theta_{\rm sep}
+
\omega_{\rm sep}\tau.
$$

Therefore:

$$
y_A(\tau)
=
y_{\rm sep}
+
v_{y,\rm sep}\tau
-
\frac12g\tau^2
+
\frac L2
\cos
\left(
\theta_{\rm sep}+\omega_{\rm sep}\tau
\right),
$$

and

$$
y_B(\tau)
=
y_{\rm sep}
+
v_{y,\rm sep}\tau
-
\frac12g\tau^2
-
\frac L2
\cos
\left(
\theta_{\rm sep}+\omega_{\rm sep}\tau
\right).
$$

---

# SCENE 35 — Exact ground-impact condition

The rod first hits the ground when:

$$
\boxed{
\min(y_A,y_B)=0
}
$$

or equivalently:

$$
\boxed{
y_G(\tau)
=
\frac L2
|\cos\theta(\tau)|
}
$$

assuming horizontal ground at \(y=0\).

This is generally a transcendental equation because:

* \(y_G\) contains \(\tau^2\),
* orientation contains \(\cos(\omega\tau)\).

So solve numerically for the smallest positive root.

### Narration

“Impact is not determined only by projectile motion.”

“Translation and rotation must be checked simultaneously.”

---

# SCENE 36 — How many times does the rod spin?

Once the flight time

$$
\tau_{\rm hit}
$$

is known:

$$
\Delta\theta_{\rm flight}
=
\omega_{\rm sep}\tau_{\rm hit}.
$$

Number of complete \(360^\circ\) rotations in flight:

$$
\boxed{
N_{\rm full}
=
\left\lfloor
\frac{
|\omega_{\rm sep}|\tau_{\rm hit}
}{
2\pi
}
\right\rfloor
}
$$

Fractional rotation:

$$
\frac{
|\omega_{\rm sep}|\tau_{\rm hit}
}{
2\pi
}.
$$

For example, a result of

$$
1.37
$$

means:

* one complete spin,
* plus \(0.37\) of another rotation.

---

# SCENE 37 — Important subtlety: a rod repeats its appearance every \(180^\circ\)

If both ends are identical, the geometric orientation of an unmarked rod repeats after:

$$
\pi
$$

rather than

$$
2\pi.
$$

But a **full physical rotation** is still:

$$
2\pi.
$$

Therefore the animation should put a small colored marker on one end.

Call:

$$
A=\text{marked end}.
$$

Then the viewer can see actual \(360^\circ\) rotations rather than mistaking a \(180^\circ\) flip for a complete spin.

---

# SCENE 38 — Orientation at impact

Compute the unwrapped angle:

$$
\boxed{
\theta_{\rm hit}
=
\theta_{\rm sep}
+
\omega_{\rm sep}\tau_{\rm hit}
}
$$

For display orientation:

$$
\theta_{\rm display}
=
\theta_{\rm hit}
\bmod 2\pi.
$$

If the ends are indistinguishable and we only care about the rod's line orientation:

$$
\theta_{\rm line}
=
\theta_{\rm hit}
\bmod\pi.
$$

Show both explicitly.

---

# SCENE 39 — Which endpoint hits first?

Evaluate at \(\tau_{\rm hit}\):

$$
y_A,
\qquad
y_B.
$$

The endpoint satisfying

$$
y=0
$$

is the first impact point.

Highlight that end.

Then freeze BEFORE modeling the collision.

Narration:

“Our current story ends at first impact.”

“The subsequent collision is a new problem involving an impulse, angular impulse, possible bounce, friction, and perhaps a new instantaneous pivot.”

This prevents accidentally mixing continuous-motion dynamics with impact mechanics.

---

# SCENE 40 — Full synchronized telemetry replay

Now replay the entire motion without stopping.

Left:

rod.

Right upper graph:

$$
\omega(t).
$$

Right lower graph:

$$
\alpha(t).
$$

Bottom:

energy.

Three vertical transition markers:

### S — STATIC → SLIP

$$
|f_s|=\mu_sN
$$

### L — LOSS OF CONTACT

$$
N=0
$$

### I — IMPACT

$$
\min(y_A,y_B)=0.
$$

---

# SCENE 41 — Final comparison of mathematical tools

Create four columns.

## TORQUE

Use when asking:

> How is rotation changing?

$$
\sum\tau=I\alpha.
$$

---

## ENERGY

Use when asking:

> What is angular speed at a particular orientation?

Before slip:

$$
\omega^2
=
\frac{3g}{L}
(\cos\theta_0-\cos\theta).
$$

---

## KINEMATICS

Use when asking:

> When does the rod reach that orientation?

$$
\omega=\frac{d\theta}{dt}.
$$

and

$$
dt=\frac{d\theta}{\omega(\theta)}.
$$

---

## NEWTON–EULER

Use when:

* contact slides,
* normal changes,
* friction dissipates energy,
* constraints change.

$$
m\vec a_G=\sum\vec F,
$$

$$
I_G\alpha=\sum\tau_G.
$$

---

# SCENE 42 — Why not solve everything using energy?

Narration:

“Energy is powerful, but it cannot tell us everything.”

Energy gives the speed:

$$
\omega(\theta).
$$

But energy alone does not determine:

* \(N\),
* friction direction,
* friction required,
* when static friction fails,
* the normal-force separation condition.

Those require dynamics.

Highlight:

$$
\boxed{\text{Energy tells speed.}}
$$

$$
\boxed{\text{Forces tell constraint feasibility.}}
$$

---

# SCENE 43 — Why not solve everything using torque?

Torque tells:

$$
\alpha.
$$

But integrating

$$
\ddot\theta
=
\frac{3g}{2L}\sin\theta
$$

directly is less convenient for finding \(\omega\) at a particular angle.

Energy gives that result immediately.

Therefore the lesson should explicitly teach:

$$
\boxed{
\text{Choose the mathematical tool according to the question.}
}
$$

---

# SCENE 44 — Final conceptual map

Show:

$$
\text{Gravity}
$$

↓

$$
\tau_P
$$

↓

$$
\alpha(\theta)
$$

↓

### ENERGY

$$
\omega(\theta)
$$

↓

### KINEMATICS

$$
\theta(t),\omega(t),\alpha(t)
$$

↓

### CM ACCELERATION

$$
f_{\rm required}(\theta),N(\theta)
$$

↓

### STATIC-FRICTION TEST

$$
|f_s|=\mu_sN
$$

↓

$$
\boxed{\theta_{\rm slip}}
$$

↓

### NEWTON–EULER + CONTACT

$$
\text{sliding motion}
$$

↓

### NORMAL-FORCE TEST

$$
N=0
$$

↓

$$
\boxed{\text{separation}}
$$

↓

### PROJECTILE + CONSTANT ROTATION

$$
y_G(t),x_G(t),\theta(t)
$$

↓

### ENDPOINT TEST

$$
\min(y_A,y_B)=0
$$

↓

$$
\boxed{
t_{\rm hit},
\quad
N_{\rm spins},
\quad
\theta_{\rm hit}
}
$$

---

# Agent calculation contract

Before Manim animation is generated, the physics agent should output a numerical event table of this form:

| Event                                 | Time | \(\theta\) | \(\omega\) |         \(\alpha\) | \(N\) | \(f\) | \(x_G\) | \(y_G\) |
| ------------------------------------- | ---: | ---------: | ---------: | -----------------: | ----: | ----: | ------: | ------: |
| Release                               |      |            |            |                    |       |       |         |         |
| Max static-friction demand if reached |      |            |            |                    |       |       |         |         |
| Slip begins                           |      |            |            |                    |       |       |         |         |
| Edge reached                          |      |            |            |                    |       |       |         |         |
| Vertical-edge intermediate state      |      |            |            |                    |       |       |         |         |
| Separation                            |      |            |            | 0 after separation |     0 |     0 |         |         |
| First complete airborne rotation      |      |            |            |                  0 |     0 |     0 |         |         |
| Ground impact                         |      |            |            |                  0 |     0 |     0 |         |         |

No motion should be animated from hand-chosen keyframes if the physics calculation gives different values.

---

# Graph contract for Manim

The three graphs should be derived from the same simulation state used to position the rod.

Never create separate “illustrative” graph functions that are merely synchronized visually.

At every frame the shared state should contain:

$$
t,\theta,\omega,\alpha,
x_G,y_G,v_{Gx},v_{Gy},
N,f,
\text{contact state}.
$$

Then:

### Rod orientation

reads:

$$
\theta(t).
$$

### Angular-velocity graph

reads:

$$
\omega(t).
$$

### Angular-acceleration graph

reads:

$$
\alpha(t).
$$

### FBD

reads:

$$
N(t), f(t).
$$

### Contact visualization

reads:

`STATIC`, `KINETIC`, or `FREE`.

Thus animation, narration, FBDs and graphs can never disagree.

---

# The deepest teaching point

The scene should not feel like “here are many equations for a falling rod.”

It should teach a hierarchy:

## While the foot is fixed

Choose the contact point for torque because it eliminates the unknown contact forces.

$$
\tau_P=I_P\alpha.
$$

Use energy to obtain

$$
\omega(\theta).
$$

Use CM kinematics to determine

$$
f_s(\theta)
$$

and

$$
N(\theta).
$$

Test:

$$
|f_s|\leq\mu_sN.
$$

---

## Once slipping begins

The fixed-pivot simplification is gone.

Switch to

$$
m\vec a_G=\sum\vec F
$$

and

$$
I_G\alpha=\sum\tau_G.
$$

Include kinetic-friction work.

---

## Once contact is lost

Remove both normal and friction.

Then:

$$
\vec a_G=\vec g,
$$

while

$$
\alpha=0,
$$

and therefore

$$
\omega=\text{constant}.
$$

---

## To predict ground impact

Do not track only the CM.

Track both rotating endpoints.

Find the first time:

$$
\boxed{
\min(y_A,y_B)=0.
}
$$

That determines:

* flight duration,
* number of spins,
* which end hits,
* rod orientation at impact.

---

# Final narration

“One falling rod has forced us to use nearly every major idea in rigid-body mechanics.”

“Torque told us why it began rotating.”

“Energy told us how fast it rotated at each angle.”

“Kinematics converted angle into time.”

“Newton's laws told us how much friction was required.”

“The friction inequality told us when sticking became impossible.”

“The normal force told us when contact was lost.”

“Projectile motion carried the center of mass through the air.”

“Conservation of angular momentum preserved the rod's spin.”

“And the combination of translation and rotation finally told us which end struck the ground first.”

Final screen:

$$
\boxed{
\text{Forces determine acceleration.}
}
$$

$$
\boxed{
\text{Constraints determine which motion is possible.}
}
$$

$$
\boxed{
\text{When the constraint changes, change the model.}
}
$$
