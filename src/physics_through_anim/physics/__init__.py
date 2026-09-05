"""Physics modeling + rendering framework.

Scalable, cross-domain namespace. Layered so many physics domains can coexist and
reuse assets without tangling:

- ``core``       -- domain-neutral foundation (geometry, state, loads, palette).
- ``kinematics`` -- generic rigid-body/point kinematics + animation bindings.
- ``shared``     -- cross-domain primitives (waves, fields, oscillations, particles).
- domains        -- ``mechanics``, ``fluids``, ``optics``, ``electromagnetism``,
                    ``acoustics``, ``thermodynamics``, ``modern``.
- ``overlays`` / ``recipes`` / ``problems`` / ``render`` -- cross-domain layers.

Dependency rule (one way): core <- kinematics <- shared <- domains <- recipes <-
problems. No domain imports another domain; cross-domain reuse goes through
``shared`` (or ``core``). See plans/ARCHITECTURE.md.
"""
