# Robotic Arm — 3D Modeling Journey

**Goal:** Design and 3D print all structural parts in Fusion 360, then assemble with servos and electronics.  
**Background:** Some electronics experience, beginner in CAD. Already covered: Sketch basics, Extrude basics, Fillet basics.

---

## 5 Core Basics to Learn (in order)

---

### 1. Fully Constrained Sketches

The most important habit to build. Every sketch element should turn **black** — no blue lines remaining. Use dimensions and constraints (horizontal, vertical, equal, tangent, coincident) to lock every point and edge. Unconstrained sketches cause geometry to shift unexpectedly when you edit later.

**Watch:**
- [HOW and WHY to Fully Constrain Your Sketches — Learn Fusion 360 in 30 Days: Day 17](https://www.youtube.com/watch?v=C11L136U0vQ)
- [Sketch Constraints Made Easy in Autodesk Fusion (Updated)](https://www.youtube.com/watch?v=EnNPCfIxpX8)
- [All 12 Fusion 360 Sketch Constraints — 2023 Edition](https://www.youtube.com/watch?v=ddtjErtTgOo)

---

### 2. Extrude — New Body / Join / Cut

You know the basic push-pull. Next step: use the **Operation** dropdown intentionally.
- **New Body** — creates a separate solid, useful for designing parts side by side
- **Join** — merges into existing body, for adding material
- **Cut** — removes material, how you make holes and slots without the Hole tool

**Watch:**
- [Fusion 360 Extrude Cut & Extrude Basics You Must Know](https://www.youtube.com/watch?v=xb52xlgyTCI)
- [Join, Cut, Intersect — Fusion 360 Tutorial](https://www.youtube.com/watch?v=iLr9d8Gp7Ls)

---

### 3. Fillet & Chamfer — When and Where

You know the tools. Focus now on *when* to use each:
- **Fillet** — smooth rounded edge. Use on corners that take stress or load. Apply **last**, before export.
- **Chamfer** — angled flat bevel. Use on print bed contact edges to avoid elephant foot, and on mating/assembly faces.
- Don't over-fillet everything — pick the corners that matter.

**Watch:**
- [Fillet and Chamfer — Fusion 360 Tutorial for Beginners](https://www.youtube.com/watch?v=KBcgaPMe9d8)
- [Introduction to Fusion 360: Fillet and Chamfer Tool Basics](https://www.youtube.com/watch?v=e__yJYiSOJk)

---

### 4. Hole Tool + Tolerances for 3D Printing

Critical for functional parts. FDM printers over-extrude slightly, so holes always come out smaller than designed.

**Key rules:**
- Design screw/shaft holes **0.2–0.3mm under nominal** (e.g. a 3mm hole → design at 2.8mm)
- **Print a tolerance test bar first** — a strip with holes at nominal, +0.1, +0.2, +0.3mm. Find what fits your printer. Do this once, use the result forever.
- For servo mounting holes, measure your actual servo with calipers before modeling.
- Prefer **captive nut traps** over threading into plastic — plastic threads strip fast under repeated assembly.

**Watch:**
- [The Best Way to Add Tolerances in Fusion 360](https://www.youtube.com/watch?v=cqAx1eUQG3o)
- [Beginner's Guide to Fit and Tolerance in Fusion 360 — Perfect Fit for 3D Printing](https://www.youtube.com/watch?v=Re4tKegVfqs)
- [Fusion 360 — Where to Do 3D Printing Tolerances](https://www.youtube.com/watch?v=Gr0l5J5xQiA)

---

### 5. Components & Assembly

When your design has multiple parts that need to fit together (every joint on the arm), use **Components** — not just Bodies. Each part of the arm is its own Component. Then use **Joints** to define how they connect and move.

**Why this matters:** You can simulate the arm moving in Fusion and catch clearance issues before wasting filament.

**Watch:**
- [Create Assemblies with Joints in Fusion 360 — Learn Fusion 360 in 30 Days: Day 23 (2023)](https://www.youtube.com/watch?v=OsdL0VoaGl0)
- [Fusion 360 Joints and Assemblies — 12 Tips for Beginners](https://www.youtube.com/watch?v=vjft_uppasc)
- [Components and Joints — Fusion 360](https://www.youtube.com/watch?v=CbBm6kn_xj0)

---

## Build Order

### Before anything: Calibrate your printer

Print a **tolerance test bar** — a flat strip with a row of holes at nominal, +0.1, +0.2, +0.3mm over the target size. Find what offset fits your servo screws and M3/M4 bolts. This one print saves hours of failed parts.

---

### Part 1 — Base Plate / Mounting Plate
- Static, no moving parts
- Simple rectangular body with mounting holes
- Focus: get hole placement accurate, practice fully constrained sketches
- Skill practiced: Sketch, Extrude, Hole tool

### Part 2 — Servo Brackets
- Measure your actual servos with calipers first
- Model the bracket around the servo body — don't guess dimensions
- Print one bracket → test fit → adjust offset → print the rest
- Skill practiced: Tolerances, Hole tool, Fillet on stress corners

### Part 3 — Link Arms (upper arm + forearm)
- Long structural pieces connecting joints
- Add 1–2 ribs along the length for rigidity
- **Print orientation matters:** layer lines should run along the length of the arm, not across it
- Skill practiced: Extrude (Join/Cut), Fillet on load-bearing corners

### Part 4 — Wrist Mount
- Combines a servo mount with a pivot point
- More complex geometry — builds on servo bracket experience
- Skill practiced: Components, Assembly, Joint simulation

### Part 5 — Gripper / End Effector
- Most complex part — has moving pieces
- Design last when you have the most experience
- Skill practiced: Full assembly workflow, clearance checking

---

## Good Practices Throughout

| Rule | Why |
|------|-----|
| Measure physical parts with calipers before modeling | Don't trust datasheets — real servos vary |
| 40–60% infill, 3+ perimeter walls for structural parts | Layer separation under load otherwise |
| Avoid overhangs >45° or split the part | Supports leave rough surfaces on functional faces |
| Fillet every corner under stress | Prevents cracking at layer lines |
| Think about assembly while designing | Leave screwdriver clearance, add nut traps |
| Save as v1, v2, v3 — never overwrite | You will reprint and revise parts |
| Test one part before printing multiples | Catch tolerance issues cheap |
