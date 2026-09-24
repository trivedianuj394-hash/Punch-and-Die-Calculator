Punching & Blanking Die Force Calculator

Diploma in Mechanical Engineering — Semester 3 Python Mini Project (Topic 24)

What it does
Takes sheet thickness, blank perimeter (or diameter, for circular blanks), and material ultimate shear strength as inputs.
Calculates peak blanking force F = L × t × τu, converts it to press tonnage, and recommends the nearest standard press size.
Optionally applies a shear angle to the punch and plots how the force drops as the angle increases.
Validates inputs (rejects zero/negative thickness, perimeter, or strength).

Quantity	Formula
Peak blanking force	F_max = L × t × τu
Press tonnage	(F_max / 9810) × Safety Factor
Shear rise on punch	h = W × tan(θ)
Force with shear	F_shear = F_max × t / (t + h)

Where L = profile perimeter (mm), t = sheet thickness (mm), τu = ultimate shear strength (N/mm²), W = punch face width across the shear (mm), θ = shear angle (°).

The shear-reduction formula is a standard press-tool design approximation (it reproduces the well-known rule that a shear height equal to the stock thickness halves the force). Verify the exact formula and material values against your textbook for the manual calculation required in the report.
