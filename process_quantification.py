import streamlit as st
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load YAML file
def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Load data from the YAML file
data = load_yaml("green_metallurgy.yaml")

st.title("Process Energy and Conditions")

total_energy = 0
processes = []

# Sidebar for navigation with custom styling
sidebar_background = """
    <style>
        .css-1d391kg {background-color: #f4f4f4; opacity: 0.7;} 
        .css-1d391kg:hover {background-color: #e0e0e0; opacity: 1;}
    </style>
"""
st.markdown(sidebar_background, unsafe_allow_html=True)

# Navigation
st.sidebar.title("Navigation Page")
selected_process = st.sidebar.selectbox("Select a Process", list(data.keys()))

# Map process identifiers (e.g., "(a)", "(b)") to image filenames
process_images = {
    "(a)": "Figa.jpg",
    "(b)": "Figb.jpg",
    "(c)": "Figc.jpg",
    "(d)": "Figd.jpg",
    "(e)": "Fige.jpg",
}

# Sidebar options for plot customization
st.sidebar.title("Plot Customization")
plot_library = st.sidebar.radio("Select Plotting Library", ["Matplotlib", "Plotly"], index=0)
line_thickness = st.sidebar.slider("Line Thickness", min_value=1, max_value=10, value=2)
label_font_size = st.sidebar.slider("Label Font Size", min_value=8, max_value=20, value=12)
curve_color = st.sidebar.color_picker("Select Curve Color", "#1f77b4")  # Default color

for process_name, details in data.items():
    power = details.get("Power_Average", 0)  # kW
    time_steps = details.get("Time", {})
    time_values = list(time_steps.values())
    total_time = sum(time_values)  # hours
    energy = power * total_time  # kWh
    total_energy += energy
    processes.append((process_name, power, energy, time_steps))

    if process_name == selected_process:
        st.subheader(f"{process_name}")
        
        # Create two columns for the image and the T-t curve
        col1, col2 = st.columns([1, 2])  # Adjust column widths (1:2 ratio)

        # Display the process image in the first column
        with col1:
            process_id = details.get("Process", None)  # Get the process identifier (e.g., "(a)")
            image_file = process_images.get(process_id, None)
            if image_file:
                st.image(image_file, caption=f"Process {process_id}", use_container_width=True)

        # Display the Temperature-Time (T-t) curve in the second column
        with col2:
            temp_profile = details.get("Temperature_Profile", {})
            temp_values = []
            time_points = []
            cumulative_time = 0  # Track cumulative time for each step

            for step, temp_info in temp_profile.items():
                interval = time_steps.get(step, 0)  # Get interval for the current step
                midpoint = cumulative_time + interval / 2  # Calculate midpoint time
                time_points.append(midpoint)
                cumulative_time += interval  # Update cumulative time

                if temp_info.get("Type") == "ramp":
                    temp_values.append((temp_info["Tstart"] + temp_info["Tend"]) / 2)  # Average temperature
                elif temp_info.get("Type") == "isothermal":
                    temp_values.append(temp_info["T"])

            if temp_values:
                df = pd.DataFrame({"Time (hours)": time_points, "Temperature (K)": temp_values})

                if plot_library == "Matplotlib":
                    # Plot using Matplotlib
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.plot(df["Time (hours)"], df["Temperature (K)"], linewidth=line_thickness, color=curve_color, label="T-t Curve")
                    ax.set_title(f"Temperature Profile for {process_name}", fontsize=label_font_size)
                    ax.set_xlabel("Time (hours)", fontsize=label_font_size)
                    ax.set_ylabel("Temperature (K)", fontsize=label_font_size)
                    ax.legend(fontsize=label_font_size)
                    ax.grid(True)
                    st.pyplot(fig)
                else:
                    # Plot using Plotly
                    fig = px.line(
                        df,
                        x="Time (hours)",
                        y="Temperature (K)",
                        title=f"Temperature Profile for {process_name}",
                        line_shape="linear",
                    )
                    fig.update_traces(line=dict(width=line_thickness, color=curve_color))
                    fig.update_layout(
                        title_font_size=label_font_size,
                        xaxis_title_font_size=label_font_size,
                        yaxis_title_font_size=label_font_size,
                    )
                    st.plotly_chart(fig, use_column_width=True)

        # Display metrics and energy per step details below the image and T-t curve
        col3, col4 = st.columns(2)

        with col3:
            st.metric(label="Power (kW)", value=power)
            st.metric(label="Total Energy (kWh)", value=f"{energy:.2f}")

        with col4:
            st.write("Energy per Step (Time in hours and Energy in kWh):")
            for step, interval in time_steps.items():
                energy_per_step = power * interval  # Calculate energy for each step
                st.write(f"{step}: {interval} hours, {energy_per_step:.2f} kWh")

# Sidebar metrics
st.sidebar.metric(label="Grand Total Energy Used", value=f"{total_energy:.2f} kWh")
