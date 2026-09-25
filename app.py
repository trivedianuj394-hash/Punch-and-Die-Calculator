import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(page_title="Punching & Blanking Die Force Calculator", page_icon="🔩", layout="wide")

# ============================================================
# THEME — high-contrast dark theme, custom colours + fonts
# ============================================================
NAVY = "#0f2942"        # deep navy (kept for 3D punch model)
STEEL = "#2e8bd4"        # bright steel blue accent
BG = "#0b0f19"           # page background (near-black navy)
PANEL = "#141b2b"        # card / sidebar background
PANEL_BORDER = "#2a3a52"
TEXT = "#f4f7fb"         # primary text — near white
SUBTEXT = "#b9c4d4"      # secondary text
ACCENT = "#ffb703"       # amber accent for high contrast on dark navy
GOOD = "#3ddc97"
WARN = "#ffb703"
BAD = "#ff6b6b"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Roboto+Mono:wght@500&display=swap');

html, body, [class*="css"]  {{
    font-family: 'Inter', sans-serif;
}}

/* ---- Global page background + default text colour ---- */
.stApp {{
    background: {BG};
    color: {TEXT};
}}
.stApp, .stApp p, .stApp span, .stApp label, .stApp li, .stApp div {{
    color: {TEXT};
}}
h1, h2, h3, h4, h5, h6 {{ color: {TEXT} !important; }}
.stMarkdown, .stCaption, [data-testid="stCaptionContainer"] {{ color: {SUBTEXT}; }}
a, a:visited {{ color: {STEEL} !important; }}

/* ---- Hero banner ---- */
.hero {{
    background: linear-gradient(135deg, {NAVY} 0%, {STEEL} 100%);
    padding: 22px 28px;
    border-radius: 14px;
    color: #ffffff;
    margin-bottom: 18px;
    border: 1px solid {PANEL_BORDER};
}}
.hero h1 {{ margin: 0; font-size: 1.7rem; font-weight: 800; color: #ffffff !important; }}
.hero p {{ margin: 4px 0 0 0; opacity: 0.95; font-size: 0.95rem; color: #eaf2fa !important; }}

/* ---- Team info card ---- */
.team-card {{
    background: {PANEL};
    border-left: 5px solid {ACCENT};
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.92rem;
    margin-bottom: 14px;
    color: {TEXT};
    border-top: 1px solid {PANEL_BORDER};
    border-right: 1px solid {PANEL_BORDER};
    border-bottom: 1px solid {PANEL_BORDER};
}}
.team-card b {{ color: {ACCENT}; }}

/* ---- Metrics ---- */
div[data-testid="stMetric"] {{
    background: {PANEL};
    border-radius: 10px;
    padding: 12px 10px 6px 10px;
    border: 1px solid {PANEL_BORDER};
}}
div[data-testid="stMetricLabel"] {{ color: {SUBTEXT} !important; }}
div[data-testid="stMetricValue"] {{ color: {ACCENT} !important; font-family: 'Roboto Mono', monospace; }}
div[data-testid="stMetricDelta"] {{ color: {GOOD} !important; }}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {{
    background: {PANEL};
    border-right: 1px solid {PANEL_BORDER};
}}
section[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}
section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{
    color: {SUBTEXT} !important;
}}

/* ---- Inputs (text/number/textarea/select) ---- */
.stApp input, .stApp textarea, .stApp select {{
    background-color: #1b2333 !important;
    color: {TEXT} !important;
    border: 1px solid {PANEL_BORDER} !important;
}}
div[data-baseweb="select"] > div {{
    background-color: #1b2333 !important;
    color: {TEXT} !important;
    border-color: {PANEL_BORDER} !important;
}}
div[data-baseweb="popover"] * {{ color: {TEXT} !important; }}
ul[role="listbox"] {{ background-color: #1b2333 !important; }}

/* ---- Radio / checkbox / slider labels ---- */
.stRadio label, .stCheckbox label, .stSlider label {{ color: {TEXT} !important; }}
div[data-testid="stTickBarMin"], div[data-testid="stTickBarMax"] {{ color: {SUBTEXT} !important; }}
.stSlider [data-testid="stThumbValue"] {{ color: {ACCENT} !important; }}

/* ---- Tabs ---- */
button[data-baseweb="tab"] {{ color: {SUBTEXT} !important; }}
button[data-baseweb="tab"][aria-selected="true"] {{ color: {ACCENT} !important; }}
div[data-baseweb="tab-highlight"] {{ background-color: {ACCENT} !important; }}
div[data-baseweb="tab-border"] {{ background-color: {PANEL_BORDER} !important; }}

/* ---- Alerts (info/success/warning/error) ---- */
div[data-testid="stAlert"] {{ background: {PANEL}; border: 1px solid {PANEL_BORDER}; }}
div[data-testid="stAlert"] p {{ color: {TEXT} !important; }}

/* ---- Code / latex ---- */
.katex {{ color: {TEXT} !important; }}
code {{ color: {ACCENT} !important; background: #1b2333 !important; }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR — TEAM DETAILS  (edit these with your actual details)
# ============================================================
st.sidebar.header("👥 Team Details")
group_no = st.sidebar.text_input("Group Name", value="MechSphere")
members = st.sidebar.text_area("Member Names (one per line)", value="Anuj Trivedi")
enroll = st.sidebar.text_area("Enrollment Numbers (one per line)", value="25012250610073")
guide_name = st.sidebar.text_input("Guide / Teacher Name", value="Shaikh Mohammed Azim")

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
    diameter = perimeter / np.pi  # equivalent circular diameter, used only for the 3D schematic

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
    default_width = diameter
    shear_width = st.sidebar.number_input(
        "Face Width across Shear, W (mm)", min_value=0.1, value=float(round(default_width, 1)), step=1.0,
        help="For a circular punch this is the diameter. For other profiles, use the largest straight-line "
             "width across which the shear rise acts."
    )
else:
    shear_angle = 0.0
    shear_width = diameter

st.sidebar.markdown("---")
st.sidebar.header("🧊 3D Model View")
transparent_sheet = st.sidebar.checkbox("Semi-transparent sheet (see punch/die through it)", value=False)

# ============================================================
# MAIN — HEADER
# ============================================================
st.markdown(f"""
<div class="hero">
    <h1>🔩 Punching & Blanking Die Force Calculator</h1>
    <p>Diploma in Mechanical Engineering — Semester 3 Python Mini Project · Topic 24</p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="team-card">
<b>{group_no}</b> &nbsp;|&nbsp; <b>Member(s):</b> {members.replace(chr(10), ', ')}
&nbsp;|&nbsp; <b>Enrollment No.:</b> {enroll.replace(chr(10), ', ')}
&nbsp;|&nbsp; <b>Guide:</b> {guide_name}
</div>
""", unsafe_allow_html=True)

st.markdown(
    "This app estimates the **peak punching/blanking force**, the **required press tonnage** "
    "(with a safety factor), and the **reduction in force** achieved when a shear angle is "
    "ground onto the punch face — with supporting graphs and an interactive 3D view of the punch, "
    "sheet, and die."
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
F_max_N = perimeter * thickness * tau_u          # N
F_max_kN = F_max_N / 1000
F_max_tonf = F_max_N / 9810                       # metric tonnes-force (g = 9.81 m/s^2)

required_tonnage = F_max_tonf * safety_factor

standard_presses = [5, 10, 15, 20, 25, 30, 40, 50, 63, 80, 100, 125, 160, 200, 250]
recommended_press = next((p for p in standard_presses if p >= required_tonnage), None)


def shear_reduced_force(F0, t, angle_deg, width):
    """F_shear = F0 * t / (t + h), h = W*tan(angle). Reduces to the design rule of thumb
    'shear = thickness gives ~50% force reduction' when h = t."""
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
# 3D ASSEMBLY MODEL (Plotly) — punch / sheet / die, schematic, not to scale
# ============================================================

def _cyl_wall(R, theta, z_bottom, z_top, n_z=2):
    fz = np.linspace(0.0, 1.0, n_z)
    F, TH = np.meshgrid(fz, theta, indexing="ij")
    X = R * np.cos(TH)
    Y = R * np.sin(TH)
    Zb = np.broadcast_to(z_bottom, TH.shape)
    Zt = np.broadcast_to(z_top, TH.shape)
    Z = Zb + F * (Zt - Zb)
    return X, Y, Z


def _flat_cap(r_in, r_out, theta, z_of_rtheta, n_r=2):
    r_lin = np.linspace(r_in, r_out, n_r)
    R_, TH_ = np.meshgrid(r_lin, theta, indexing="ij")
    X = R_ * np.cos(TH_)
    Y = R_ * np.sin(TH_)
    Z = z_of_rtheta(R_, TH_)
    return X, Y, Z


def build_assembly_figure(D, t, shear_deg, sheet_opacity=1.0, n=48):
    R = D / 2.0
    shear_rad = np.radians(shear_deg)
    theta = np.linspace(0, 2 * np.pi, n)

    punch_h = max(0.8 * D, 20.0)
    die_h = max(0.35 * D, 10.0)
    gap = max(0.15 * D, 4.0)
    outer_r = 1.7 * R

    sheet_top = _flat_cap(0, outer_r, theta, lambda Rg, Tg: np.full_like(Rg, t))
    sheet_bot = _flat_cap(0, outer_r, theta, lambda Rg, Tg: np.zeros_like(Rg))
    sheet_wall = _cyl_wall(outer_r, theta, 0.0, t)

    die_top_z, die_bot_z = -gap, -gap - die_h
    die_top = _flat_cap(R, outer_r, theta, lambda Rg, Tg: np.full_like(Rg, die_top_z))
    die_bot = _flat_cap(R, outer_r, theta, lambda Rg, Tg: np.full_like(Rg, die_bot_z))
    die_outer = _cyl_wall(outer_r, theta, die_bot_z, die_top_z)
    die_inner = _cyl_wall(R, theta, die_bot_z, die_top_z)

    z_base = t + gap
    z_bottom_theta = z_base + R * np.cos(theta) * np.tan(shear_rad)
    z_top_flat = z_base + punch_h + R * abs(np.tan(shear_rad))
    punch_bot = _flat_cap(0, R, theta, lambda Rg, Tg: z_base + Rg * np.cos(Tg) * np.tan(shear_rad))
    punch_top = _flat_cap(0, R, theta, lambda Rg, Tg: np.full_like(Rg, z_top_flat))
    punch_wall = _cyl_wall(R, theta, z_bottom_theta, z_top_flat)

    fig = go.Figure()

    def add(surf, color, name, opacity=1.0, showlegend=False):
        X, Y, Z = surf
        fig.add_trace(go.Surface(
            x=X, y=Y, z=Z, surfacecolor=np.zeros_like(Z),
            colorscale=[[0, color], [1, color]], showscale=False,
            opacity=opacity, name=name, showlegend=showlegend,
            hoverinfo="name",
        ))

    add(die_top, "#4a4a4a", "Die", showlegend=True)
    add(die_bot, "#3a3a3a", "Die")
    add(die_outer, "#555555", "Die")
    add(die_inner, "#2f2f2f", "Die")

    add(sheet_top, "#b8c4cc", "Sheet / Blank", opacity=sheet_opacity, showlegend=True)
    add(sheet_bot, "#9aa7af", "Sheet / Blank", opacity=sheet_opacity)
    add(sheet_wall, "#a3b0b8", "Sheet / Blank", opacity=sheet_opacity)

    add(punch_bot, NAVY, "Punch", showlegend=True)
    add(punch_top, NAVY, "Punch")
    add(punch_wall, STEEL, "Punch")

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
            aspectmode="data",
            camera=dict(eye=dict(x=1.6, y=1.6, z=1.1)),
        ),
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01),
        height=520,
    )
    return fig


# ============================================================
# TABS
# ============================================================
tab_results, tab_graphs, tab_3d, tab_formulas = st.tabs(
    ["📐 Results", "📊 Graphs", "🧊 3D Model", "📘 Formulas"]
)

# ---------------- RESULTS TAB ----------------
with tab_results:
    st.subheader("Calculated Results")
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
        st.subheader("Effect of Shear on Punch")
        d1, d2, d3 = st.columns(3)
        d1.metric("Reduced Force", f"{F_shear_kN:.2f} kN", f"-{reduction_pct:.1f}%")
        d2.metric("Reduced Press Tonnage", f"{required_tonnage_shear:.2f} T")
        d3.metric("Recommended Press", f"{recommended_press_shear} T" if recommended_press_shear else "N/A")

# ---------------- GRAPHS TAB ----------------
with tab_graphs:
    colA, colB = st.columns(2)

    with colA:
        st.markdown("**Blanking Force vs Shear Angle**")
        angles = np.linspace(0, 5, 100)
        ref_width = shear_width if shear_width else diameter
        forces_kN = [shear_reduced_force(F_max_N, thickness, a, ref_width)[0] / 1000 for a in angles]
        fig1, ax1 = plt.subplots(figsize=(5.2, 4))
        ax1.plot(angles, forces_kN, color=STEEL, linewidth=2, label="Blanking Force")
        ax1.axhline(F_max_kN, color="gray", linestyle="--", linewidth=1, label="No shear (θ=0°)")
        if apply_shear:
            ax1.plot(shear_angle, F_shear_kN, "o", color="#c0392b", markersize=8, label=f"θ = {shear_angle}°")
        ax1.set_xlabel("Shear Angle, θ (degrees)")
        ax1.set_ylabel("Blanking Force (kN)")
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend(fontsize=8)
        st.pyplot(fig1)

    with colB:
        st.markdown("**Blanking Force vs Sheet Thickness**")
        t_range = np.linspace(max(0.2, 0.3 * thickness), 2.5 * thickness, 100)
        forces_t_kN = (perimeter * t_range * tau_u) / 1000
        fig2, ax2 = plt.subplots(figsize=(5.2, 4))
        ax2.plot(t_range, forces_t_kN, color=NAVY, linewidth=2)
        ax2.plot(thickness, F_max_kN, "o", color="#c0392b", markersize=8, label=f"Current t = {thickness} mm")
        ax2.set_xlabel("Sheet Thickness, t (mm)")
        ax2.set_ylabel("Blanking Force (kN)")
        ax2.grid(True, linestyle=":", alpha=0.6)
        ax2.legend(fontsize=8)
        st.pyplot(fig2)

    st.markdown("**Force Comparison: No Shear vs Current Shear Setting**")
    fig3, ax3 = plt.subplots(figsize=(6.5, 3.2))
    bars = ax3.bar(["No Shear", f"With Shear (θ={shear_angle}°)"], [F_max_kN, F_shear_kN],
                    color=[STEEL, NAVY], width=0.5)
    for b in bars:
        ax3.text(b.get_x() + b.get_width() / 2, b.get_height() + 1, f"{b.get_height():.1f} kN",
                  ha="center", fontsize=9)
    ax3.set_ylabel("Blanking Force (kN)")
    ax3.grid(True, axis="y", linestyle=":", alpha=0.6)
    st.pyplot(fig3)

# ---------------- 3D MODEL TAB ----------------
with tab_3d:
    st.markdown(
        "Interactive schematic of the punch, sheet metal (blank), and die — drag to rotate, "
        "scroll to zoom. Proportions are exaggerated for clarity and are **not to scale**; the "
        "punch's cutting face reflects the shear angle set in the sidebar."
    )
    sheet_opacity = 0.35 if transparent_sheet else 1.0
    fig3d = build_assembly_figure(diameter, thickness, shear_angle, sheet_opacity=sheet_opacity)
    st.plotly_chart(fig3d, width="stretch")

# ---------------- FORMULAS TAB ----------------
with tab_formulas:
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

        The shear-reduction formula is a standard press-tool design approximation: a shear height
        equal to the stock thickness (h = t) cuts the force by about half, which is the well-known
        rule of thumb used when specifying shear on a punch. Confirm the exact formula and material
        values given in your textbook when writing up your manual vs. app comparison.
        """
    )
