import streamlit as st
import numpy as np
import altair as alt
import pandas as pd
from scipy import signal
import time

def get_primary_function(time_vals, frequency, amplitude, classification):
    if classification == "Square":
        return amplitude * signal.square(2 * np.pi * frequency * time_vals)
    elif classification == "Sawtooth":
        return amplitude * signal.sawtooth(2 * np.pi * frequency * time_vals)
    elif classification == "Triangle":
        return amplitude * signal.sawtooth(2 * np.pi * frequency * time_vals, 0.5)
    else:
        return amplitude * np.sin(2 * np.pi * frequency * time_vals)

st.set_page_config(layout="wide")
st.title("Signal Convolutor")

# SIDEBAR CONTROLS
st.sidebar.header("Global Settings")
duration = st.sidebar.slider("Duration (s)", 1, 10, 5, 1)
anim_speed = st.sidebar.slider("Anim Speed", 1, 100, 50, help="Frames per second (approx)")
sampling_rate = 100
dt = 1.0 / sampling_rate
time_axis = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# Signal 1
with st.sidebar.expander("Signal 1 (Stationary)", expanded=True):
    type1 = st.selectbox("Type 1", ["Square", "Sine", "Sawtooth", "Triangle"])
    c1, c2 = st.columns(2)
    f1 = c1.slider("Freq 1", 0.1, 5.0, 1.0, 0.1)
    a1 = c2.slider("Amp 1", 0.1, 5.0, 1.0, 0.1)
    c3, c4 = st.columns(2)
    ox1 = c3.slider("X-Off 1", -2.0, 2.0, 0.0, 0.1)
    oy1 = c4.slider("Y-Off 1", -2.0, 2.0, 0.0, 0.1)

# Signal 2
with st.sidebar.expander("Signal 2 (Sliding)", expanded=True):
    type2 = st.selectbox("Type 2", ["Sine", "Square", "Sawtooth", "Triangle"])
    c1, c2 = st.columns(2)
    f2 = c1.slider("Freq 2", 0.1, 5.0, 0.5, 0.1)
    a2 = c2.slider("Amp 2", 0.1, 5.0, 1.0, 0.1)
    c3, c4 = st.columns(2)
    ox2 = c3.slider("X-Off 2", -2.0, 2.0, 0.0, 0.1)
    oy2 = c4.slider("Y-Off 2", -2.0, 2.0, 0.0, 0.1)


# SIGNAL GENERATION

# Apply offsets: Y = Function(t - X_offset) + Y_offset
y1 = get_primary_function(time_axis - ox1, f1, a1, type1) + oy1
y2 = get_primary_function(time_axis - ox2, f2, a2, type2) + oy2

# Convolution
convolved_full = signal.convolve(y1, y2, mode='full') * dt
conv_time_axis = np.arange(len(convolved_full)) * dt

col_btn1, col_btn2 = st.columns([1, 10])
start_anim = col_btn1.button("Start")
stop_anim = col_btn2.button("Stop") 

status_text = st.empty()
chart_placeholder = st.empty()

def render_frame(current_shift_index):
    t_current = current_shift_index * dt
    tau = time_axis
    
    # Calculate Sliding Signal 2: g(t - tau)
    t_local_for_y2 = t_current - tau
    
    # Generate shifting y2
    mask = (t_local_for_y2 >= 0) & (t_local_for_y2 < duration)
    y2_sliding = np.zeros_like(tau)
    # Note: We re-apply the user's base parameters to the sliding window
    # The 'time' passed to the function is the local shifted time
    y2_sliding[mask] = get_primary_function(t_local_for_y2[mask] - ox2, f2, a2, type2) + oy2
    
    # Product
    product = y1 * y2_sliding

    df_interaction = pd.DataFrame({
        'tau': tau,
        'Signal 1': y1,
        'Signal 2': y2_sliding,
        'Product': product
    })

    # Prepare Result Data (slice up to current)
    df_result = pd.DataFrame({'t': conv_time_axis, 'Convolution': convolved_full})
    df_result_visible = df_result.iloc[:current_shift_index+1]
    
    
    # Interaction Chart
    base_int = alt.Chart(df_interaction).encode(x=alt.X('tau', title=None, axis=alt.Axis(labels=False, ticks=False)))
    
    l1 = base_int.mark_line(color='#1f77b4').encode(y=alt.Y('Signal 1', title='Amp'))
    l2 = base_int.mark_line(color='#ff7f0e', strokeWidth=3).encode(y='Signal 2')
    area = base_int.mark_area(opacity=0.3, color='green').encode(y='Product')
    
    top = (area + l1 + l2).properties(
        height=150,
        title="Interaction (Flip & Slide)"
    )

    # Result Chart
    base_res = alt.Chart(df_result).encode(x=alt.X('t', title='Time (s)'))
    
    r_full = base_res.mark_line(color='#eeeeee').encode(y=alt.Y('Convolution', title='Conv'))
    r_prog = alt.Chart(df_result_visible).mark_line(color='green').encode(x='t', y='Convolution')
    r_tip = alt.Chart(df_result_visible.iloc[-1:]).mark_circle(color='red', size=60).encode(x='t', y='Convolution')

    bottom = (r_full + r_prog + r_tip).properties(height=150)

    return alt.vconcat(top, bottom, spacing=0)

# Logic: Streamlit reruns script on interaction. 
# If 'Start' was clicked, we run the loop. 
# If 'Stop' is clicked during the loop, the script reruns and since 'Start' is now False, it stops.

if start_anim and not stop_anim:
    total_steps = len(conv_time_axis)
    # Skip frames based on speed to keep animation responsive
    skip = max(1, int(100 / anim_speed)) 
    
    for i in range(0, total_steps, skip):
        chart = render_frame(i)
        chart_placeholder.altair_chart(chart, width="stretch")
        time.sleep(1/anim_speed) # Control speed
        
    status_text.text("Done!")
else:
    # Static view (show middle of convolution)
    mid = int(len(conv_time_axis) / 2)
    chart_placeholder.altair_chart(render_frame(mid), width="stretch")