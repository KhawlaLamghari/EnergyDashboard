import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import numpy as np

st.set_page_config(layout="centered")

# --- Labels ---
x_labels = [i / 10 for i in range(5)]  # [0.0, 0.1, ..., 0.4]
y_labels = [f"{i:.1f}" for i in reversed(range(5))]  # ["4.0", ..., "0.0"]

# --- Sidebar Controls ---
with st.sidebar:
    st.title("⚙️ Controls")
    option = st.selectbox("Select a Dataset", ["Energy Consumption", "Financial Cost", "CO₂ Emissions"])

    # Defaults per dataset
    if option == "Energy Consumption":
        unit = "TJ"
        colorscale = "Blues"
        slider_key = "threshold_energy"
        default = 328.21
        min_val, max_val = 200.0, 450.0
    elif option == "Financial Cost":
        unit = "MMAD"
        colorscale = "Greens"
        slider_key = "threshold_cost"
        default = 87.46
        min_val, max_val = 50.0, 500.0
    else:
        unit = "t CO₂ eq"
        colorscale = [[0, "#FADBD8"], [1, "#922B21"]]
        slider_key = "threshold_emissions"
        default = 20419.83
        min_val, max_val = 6000.0, 25000.0

    # Reset button
    if st.button("🔁 Reset Threshold"):
        st.session_state[slider_key] = default

    threshold = st.slider(
        f"Highlight values above ({unit})",
        min_value=min_val,
        max_value=max_val,
        value=default,
        key=slider_key
    )

    show_dots = st.checkbox("Show red dots for values above threshold", value=True)

# --- Load data per option
if option == "Energy Consumption":
    data = np.array([
        [369083703.17, 349700042.30, 239180549.65, 239180549.65, 402487371.22],
        [329553061.70, 308310693.62, 217931963.98, 217931963.98, 358255629.69],
        [329372439.58, 308130071.50, 217751341.85, 217751341.85, 358075007.56],
        [366564325.30, 347180664.43, 236661171.77, 236661171.77, 399967993.35],
        [328203061.70, 306960693.62, 216581963.98, 216581963.98, 356905629.69]
    ]) / 1_000_000
elif option == "Financial Cost":
    data = np.array([
        [98672635.15, 93273286.72, 59520765.48, 53747291.99, 483164111.06],
        [87717648.90, 81800554.73, 54075858.44, 49114920.77, 373448876.83],
        [87682527.93, 81765433.76, 54040737.48, 49079799.80, 373413755.86],
        [98182756.12, 92783407.69, 59030886.45, 53257412.96, 430712970.62],
        [87455148.90, 81538054.73, 53813358.44, 48852420.77, 373186376.83]
    ]) / 1_000_000
else:
    data = np.array([
        [23228.34, 21830.82, 20243.64, 6716.04, 9710.35],
        [20424.32, 18892.79, 17859.67, 6235.90, 8808.80],
        [20423.72, 18892.19, 17859.07, 6235.30, 8808.19],
        [23219.95, 21822.43, 20235.25, 6707.65, 9701.96],
        [20419.83, 18888.30, 17855.18, 6231.40, 8804.30]
    ])

# --- Title ---
st.title("🔍 Energy, Cost, and Emissions Dashboard")


# --- Explanations ---
with st.expander("ℹ️ About this chart"):
    if option == "Energy Consumption":
        st.markdown("""
        - **Dataset**: Energy consumption in **terajoules (TJ)**.
        - **X-axis**: Energy scenarios from 0.0 to 0.4.
        - **Y-axis**: Phosphate scenarios from 0.0 (bottom) to 4.0 (top).
        The heatmap is structured as a matrix of scenarios: the X-axis represents variations in the energy scenario, while the Y-axis captures changes in the phosphate scenario. Each cell reflects the outcome at a specific (energy, phosphate) combination.
        - **Cell values**: Energy used per scenario.
        - 🔴 Red dots show values above your threshold.
        """)
    elif option == "Financial Cost":
        st.markdown("""
        - **Dataset**: Costs in **millions of MAD (MMAD)**.
        - **X-axis**: Energy scenarios from 0.0 to 0.4.
        - **Y-axis**: Phosphate scenarios from 0.0 (bottom) to 4.0 (top).
        The heatmap is structured as a matrix of scenarios: the X-axis represents variations in the energy scenario, while the Y-axis captures changes in the phosphate scenario. Each cell reflects the outcome at a specific (energy, phosphate) combination.
        - **Cell values**: Projected or actual financial costs.
        - 🔴 Red dots mark high-cost areas above threshold.
        """)
    else:
        st.markdown("""
        - **Dataset**: CO₂ emissions in **t CO₂ eq**.
        - **X-axis**: Energy scenarios from 0.0 to 0.4.
        - **Y-axis**: Phosphate scenarios from 0.0 (bottom) to 4.0 (top).
        - The heatmap is structured as a matrix of scenarios: the X-axis represents variations in the energy scenario, while the Y-axis captures changes in the phosphate scenario. Each cell reflects the outcome at a specific (energy, phosphate) combination.
        - **Cell values**: Emissions per scenario setup.
        - 🔴 Red dots highlight excessive emissions.
        """)

with st.expander("📌 Assumptions & Notes"):
    st.markdown("""
    - All data assumed pre-validated and reliable.
    - Thresholds are user-defined and illustrative.
    - Emissions data based on standard conversion.
    - Costs shown are not inflation-adjusted.
    - Energy converted from MJ to TJ for comparability.
    """)

# --- Annotations ---
annotations = [[f"{val:,.2f}" for val in row] for row in data]

# --- Create heatmap ---
fig = go.Figure(data=go.Heatmap(
    z=data,
    x=x_labels,
    y=[float(y) for y in y_labels],
    text=annotations,
    texttemplate="%{text}",
    hoverinfo="text",
    colorscale=colorscale,
    colorbar=dict(title=f"{option} ({unit})"),
    showscale=True
))

# --- Dummy trace for legend
if show_dots:
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(size=6, color="red", line=dict(color="black", width=1)),
        name="Above Threshold",
        showlegend=True
    ))

# --- Red dots under values
if show_dots:
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if data[i, j] > threshold:
                fig.add_trace(go.Scatter(
                    x=[x_labels[j]],
                    y=[float(y_labels[i]) - 0.3],
                    mode="markers",
                    marker=dict(size=6, color="red", line=dict(color="black", width=1)),
                    showlegend=False,
                    hoverinfo="skip"
                ))

# --- Layout adjustments
fig.update_layout(
    title=f"{option} Heatmap ({unit})",
    font=dict(family="Comic Sans MS", size=12),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5
    ),
    margin=dict(b=100)
)
fig.update_yaxes(
    tickmode="array",
    tickvals=[0, 1, 2, 3, 4],
    ticktext=["0.0", "1.0", "2.0", "3.0", "4.0"]
)
fig.update_xaxes(
    tickmode="array",
    tickvals=[0.0, 0.1, 0.2, 0.3, 0.4],
    ticktext=["0.0", "0.1", "0.2", "0.3", "0.4"],
    tickangle=0,
    tickfont=dict(size=12)
)

# --- Show chart
with st.container():
    st.plotly_chart(fig, use_container_width=True)

with st.expander("📘 Energy scenario"):
    st.markdown("""
    | Scenario | Description                         |
    |------|-------------------------------------|
    | X.0  | Business-as-usual scenario           |
    | X.1  | Regenerative breaking system installation in mine haul trucks (MHTs)     |
    | X.2  | MHTs, loaders and D11 bulldozers electrification using the Moroccan grid         |
    | X.3  | MHTs, loaders and D11 bulldozers electrification using the wind electricity               |
    | X.4  | MHTs, loaders and D11 bulldozers running using green hydrogen                  |
    """)


with st.expander("🧪 Phosphate Scenario Legend"):
    st.markdown("""
    | Scenario | Description                         |
    |------|-------------------------------------|
    | 0.Y  | Baseline phosphate production       |
    | 1.Y  | Extracting the deposit non-extracted seams           |
    | 2.Y  | Preventing phosphate from dissipation in DPWR and SPWR      |
    | 3.Y  | Extracting phosphate from old spoil piles (Fr.: cavaliers)               |
    | 4.Y  | Integrated scenario |
    """)


# --- Download as PNG
st.download_button(
    label="📅 Download Chart as PNG",
    data=pio.to_image(fig, format="png"),
    file_name=f"{option.replace(' ', '_').lower()}_heatmap.png",
    mime="image/png"
)

# --- Download as CSV
csv_data = pd.DataFrame(data, index=[f"{y}" for y in y_labels], columns=[f"{x:.1f}" for x in x_labels])
csv = csv_data.to_csv(index=True).encode("utf-8")
st.download_button(
    label="📄 Download Data as CSV",
    data=csv,
    file_name=f"{option.replace(' ', '_').lower()}_data.csv",
    mime="text/csv"
)

# --- Footer spacer
st.markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)
st.markdown("""
---
<div style='text-align: center; font-size: 14px; color: gray;'>
    Made by <strong> Khawla</strong> ✅ <br>
    Khawla.Lamghari@um6p.ma
</div>
""", unsafe_allow_html=True)
