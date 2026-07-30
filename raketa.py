import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


st.title("Rocket flight simulator")
st.write("A 2D model of a rocket's flight, including thrust, variable mass, "
         "air drag, and atmospheric density that decreases with altitude.")


def simulate(thrust, dry_mass, fuel_mass, burn_time, angle, Cd, area, drag_on=True):
    x = 0
    y = 0
    vx = 0
    vy = 0
    t = 0
    mass = dry_mass + fuel_mass
    fuel_rate = fuel_mass / burn_time
    peak_y = 0
    
    xs, ys, vys, ts, gforces = [], [], [], [], []
    
    max_steps = 500000
    step = 0
    
    while (y > 0 or t < burn_time) and step < max_steps:
        g = g0 * (R_earth / (R_earth + y))**2
        v_total = np.sqrt(vx**2 + vy**2)
        rho = rho0 * np.exp(-y / scale_height)
        
        if drag_on:
            drag_force = 0.5 * rho * v_total**2 * Cd * area
        else:
            drag_force = 0
        
        if t < burn_time:
            thrust_x = thrust * np.sin(angle)
            thrust_y = thrust * np.cos(angle)
            mass = mass - fuel_rate * dt
        else:
            thrust_x = 0
            thrust_y = 0
        
        if v_total > 0:
            drag_x = drag_force * (vx / v_total)
            drag_y = drag_force * (vy / v_total)
        else:
            drag_x = 0
            drag_y = 0
        
        ax = (thrust_x - drag_x) / mass
        ay = (thrust_y - drag_y) / mass - g
        a_total = np.sqrt(ax**2 + ay**2)
        gforce = a_total / g0
        
        vx = vx + ax * dt
        vy = vy + ay * dt
        x = x + vx * dt
        y = y + vy * dt
        t = t + dt
        
        xs.append(x)
        ys.append(y)
        vys.append(vy)
        ts.append(t)
        gforces.append(gforce)
        
        if y > peak_y:
            peak_y = y
        step += 1
    
    return xs, ys, vys, ts, gforces, peak_y, x, t

st.sidebar.header("Rocket parameters")

angle_deg = st.sidebar.slider("Launch angle (degrees)", 0, 70, 5) 
angle = np.radians(angle_deg)
g0 = 9.81            # gravitational acceleration at sea level, m/s²
R_earth = 6371000    # radius of the Earth, m
dt = 0.01
thrust = st.sidebar.slider("Thrust (N)", 1000, 10000, 4000)
dry_mass = st.sidebar.slider("Dry mass (kg)", 10, 100, 50)
fuel_mass = st.sidebar.slider("Fuel mass (kg)", 10, 200, 100)
burn_time = st.sidebar.slider("Burn time (s)", 1, 20, 5)

drag_on = True 

drag_on = st.sidebar.checkbox("Drag Enabled", value=True)
if drag_on:
    Cd = st.sidebar.slider("Coefficient of drag", 0.1, 1.0, 0.5)
    area = st.sidebar.slider("Cross-sectional area (m²)", 0.01, 0.1, 0.03)
else:
    Cd = 0
    area = 0
    st.sidebar.write("Drag is OFF, so Cd and area are set to 0.")


rho0 = 1.2           # air density at sea level, kg/m³
scale_height = 8500  


max_steps = 500000
step = 0

# spuštění s odporem
xs, ys, vys, ts, gforces, peak_y, x, t = simulate(
    thrust, dry_mass, fuel_mass, burn_time, angle, Cd, area, drag_on=True
)

print("Time taken to hit the ground:", t, "seconds")
print("Peak height:", peak_y, "meters")
print("Horizontal distance:", x, "meters")

st.subheader("Results")
col1, col2, col3 = st.columns(3)
col1.metric("Peak height", f"{peak_y:.0f} m")
col2.metric("Horizontal distance", f"{x:.0f} m")
col3.metric("Flight time", f"{t:.1f} s")

fig1, ax1 = plt.subplots()
ax1.plot(xs, ys)
ax1.set_xlabel("Horizontal distance (m)")
ax1.set_ylabel("Altitude (m)")
ax1.set_title("Flight path")
ax1.grid(True)
st.pyplot(fig1)

fig2, ax2 = plt.subplots()
ax2.plot(ts, vys)
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Vertical velocity (m/s)")
ax2.set_title("Vertical velocity over time")
ax2.grid(True)
st.pyplot(fig2)

fig3, ax3 = plt.subplots()
ax3.plot(ts, gforces)
ax3.set_xlabel("Time (s)")
ax3.set_ylabel("G-Force")
ax3.set_title("G-Force over time")
ax3.grid(True)
st.pyplot(fig3)
