import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Punching & Blanking Die Force Calculator", page_icon="🔩", layout="wide")

# ============================================================
# SIDEBAR — TEAM DETAILS  (edit these with your actual details)
# ============================================================
st.sidebar.header("👥 Team Details")
group_no = st.sidebar.text_input("Group Number", value="Group 24")
members = st.sidebar.text_area("Member Names (one per line)", value="Member 1\nMember 2\nMember 3")
enroll = st.sidebar.text_area("Enrollment Numbers (one per line)", value="Enrollment No. 1\nEnrollment No. 2\nEnrollment No. 3")

st.sidebar.markdown("---")

# ============================================================
# SIDEBAR — GEOMETRY INPUTS
# ============================================================
st.sidebar.header("⚙️ Blank / Punch Geometry")

profile_shape = st.sidebar.radio("Blank Profile Shape", ["Circular", "Custom Perimeter"])

if profile_shape == "Circular":
    diameter = st.sidebar.number_input("Blank Diameter, D (mm)", min_value=0.0, value=50.0, step=1.0)
    perimeter = np.pi * diameter
else:
    perimeter = st.sidebar.number_input("Profile Perimeter, L (mm)", min_value=0.0, value=150.0, step=1.0)
    diameter = None

thickness = st.sidebar.number_input("Sheet Thickness, t (mm)", min_value=0.0, value=2.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.header("🧱 Material")

material_data = {
    "Mild Steel (Low Carbon)": 350,
    "Medium Carbon Steel": 450,
    "Aluminum": 95,
    "Brass": 260,
    "Copper": 220,
    "Stainless Steel (304)": 550,
    "Zinc": 130,
    "Custom": None,
}
material = st.sidebar.selectbox("Material", list(material_data.keys()))
if material == "Custom":
    tau_u = st.sidebar.number_input("Ultimate Shear Strength, τu (N/mm²)", min_value=0.0, value=300.0, step=10.0)
else:
    tau_u = material_data[material]
    st.sidebar.caption(f"Typical τu for {material} ≈ {tau_u} N/mm² — replace with your textbook's exact value when verifying against your manual calculation.")

st.sidebar.markdown("---")
st.sidebar.header("🏭 Press Selection")
safety_factor = st.sidebar.slider("Safety Factor on Press Capacity", 1.0, 2.0, 1.25, 0.05)

st.sidebar.markdown("---")
st.sidebar.header("✂️ Shear on Punch (Optional)")
apply_shear = st.sidebar.checkbox("Apply shear angle to punch face?")
if apply_shear:
    shear_angle = st.sidebar.slider("Shear Angle, θ (degrees)", 0.0, 5.0, 1.0, 0.1)
    default_width = diameter if diameter else perimeter / np.pi
    shear_width = st.sidebar.number_input(
        "Face Width across Shear, W (mm)", min_value=0.1, value=float(round(default_width, 1)), step=1.0,
        help="For a circular punch this is the diameter. For other profiles, use the largest straight-line "
             "width across which the shear rise acts."
    )
else:
    shear_angle = 0.0
    shear_width = None

# ============================================================
# MAIN — HEADER
# ============================================================
st.title("🔩 Punching & Blanking Die Force Calculator")
st.caption("Diploma in Mechanical Engineering — Semester 3 Python Mini Project | Topic 24")

st.info(
    f"**{group_no}**  \n"
    f"**Members:** {members.replace(chr(10), ', ')}  \n"
    f"**Enrollment No.:** {enroll.replace(chr(10), ', ')}"
)

st.markdown(
    "This app estimates the **peak punching/blanking force**, the **required press tonnage** "
    "(with a safety factor), and the **reduction in force** achieved when a shear angle is "
    "ground onto the punch face."
)

# ============================================================
# VALIDATION
# ============================================================
errors = []
if thickness <= 0:
    errors.append("Sheet thickness must be greater than zero.")
if perimeter <= 0:
    errors.append("Perimeter / diameter must be greater than zero.")
if tau_u is None or tau_u <= 0:
    errors.append("Ultimate shear strength must be greater than zero.")

if errors:
    for e in errors:
        st.error(f"⚠️ {e}")
    st.stop()

if safety_factor < 1.0:
    st.warning("A safety factor below 1.0 is not recommended for press selection.")

if apply_shear and shear_angle > 3.0:
    st.warning("Shear angles above ~3° are uncommon in practice and unnecessarily lengthen the punch stroke.")

# ============================================================
# CALCULATIONS
# ============================================================
F_max_N = perimeter * thickness * tau_u          # N   (L in mm, t in mm, tau_u in N/mm^2)
F_max_kN = F_max_N / 1000
F_max_tonf = F_max_N / 9810                       # metric tonnes-force (g = 9.81 m/s^2)

required_tonnage = F_max_tonf * safety_factor

standard_presses = [5, 10,15,20,25,30,40,50,63,80,100, 125, 160, 200, 250]
recommended_press = next((p for p in standard_presses if p >= required_tonnage), None)


def shear_reduced_force(F0, t, angle_deg, width):
    """Approximate model: F_shear = F0 * t / (t + h), where h = W*tan(angle) is the shear rise.
    This reduces to the well-known design rule 'shear = thickness gives ~50% force reduction'
    when h = t. Always confirm the exact formula given in your textbook."""
    if width is None or angle_deg <= 0:
        return F0, 0.0
    h = width * np.tan(np.radians(angle_deg))
    F1 = F0 * t / (t + h)
    reduction_pct = (F0 - F1) / F0 * 100
    return F1, reduction_pct


F_shear_N, reduction_pct = shear_reduced_force(F_max_N, thickness, shear_angle, shear_width)
F_shear_kN = F_shear_N / 1000
F_shear_tonf = F_shear_N / 9810
required_tonnage_shear = F_shear_tonf * safety_factor
recommended_press_shear = next((p for p in standard_presses if p >= required_tonnage_shear), None)

# ============================================================
# RESULTS
# ============================================================
st.subheader("📐 Calculated Results")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Perimeter, L", f"{perimeter:.1f} mm")
c2.metric("Peak Blanking Force", f"{F_max_kN:.2f} kN")
c3.metric("Force (ton-force)", f"{F_max_tonf:.2f} tf")
c4.metric("Required Press Tonnage", f"{required_tonnage:.2f} T", help=f"With safety factor {safety_factor}")

if recommended_press:
    st.success(f"✅ Recommended standard press capacity: **{recommended_press} Tonnes**")
else:
    st.warning("⚠️ Required tonnage exceeds the standard press range listed — a larger custom press would be needed.")

if apply_shear and shear_angle > 0:
    st.subheader("✂️ Effect of Shear on Punch")
    d1, d2, d3 = st.columns(3)
    d1.metric("Reduced Force", f"{F_shear_kN:.2f} kN", f"-{reduction_pct:.1f}%")
    d2.metric("Reduced Press Tonnage", f"{required_tonnage_shear:.2f} T")
    d3.metric("Recommended Press", f"{recommended_press_shear} T" if recommended_press_shear else "N/A")

# ============================================================
# GRAPH
# ============================================================
st.subheader("📊 Blanking Force vs Shear Angle")

angles = np.linspace(0, 5, 100)
ref_width = shear_width if shear_width else (diameter if diameter else perimeter / np.pi)
forces_kN = [shear_reduced_force(F_max_N, thickness, a, ref_width)[0] / 1000 for a in angles]

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(angles, forces_kN, color="#1f77b4", linewidth=2, label="Blanking Force")
ax.axhline(F_max_kN, color="gray", linestyle="--", linewidth=1, label="Force without shear (θ = 0°)")
if apply_shear:
    ax.plot(shear_angle, F_shear_kN, "ro", markersize=8, label=f"Selected θ = {shear_angle}°")
ax.set_xlabel("Shear Angle, θ (degrees)")
ax.set_ylabel("Blanking Force (kN)")
ax.set_title("Blanking Force / Press Capacity Reduction vs Shear Angle")
ax.grid(True, linestyle=":", alpha=0.6)
ax.legend()
st.pyplot(fig)

st.caption(
    "Note: the force-reduction curve uses the approximation F_shear = F_max × t / (t + h), where "
    "h = W·tan(θ) is the shear rise across face width W. This matches the standard press-tool design "
    "rule of thumb that a shear height equal to the stock thickness cuts the force by about half. "
    "Confirm the exact formula and material values given in your textbook when writing up your manual "
    "vs. app comparison."
)

# ============================================================
# FORMULAS USED
# ============================================================
with st.expander("📘 Formulas Used"):
    st.latex(r"F_{max} = L \times t \times \tau_u")
    st.latex(r"\text{Press Tonnage} = \dfrac{F_{max}}{9810} \times SF")
    st.latex(r"h = W \tan(\theta), \qquad F_{shear} = F_{max} \times \dfrac{t}{t+h}")
    st.markdown(
        """
        - **L** = perimeter of the blanked/punched profile (mm)
        - **t** = sheet thickness (mm)
        - **τu** = ultimate shear strength of the material (N/mm²)
        - **SF** = safety factor
        - **W** = punch face width across which the shear rise acts (mm)
        - **θ** = shear angle ground onto the punch face (degrees)
        """
    )
