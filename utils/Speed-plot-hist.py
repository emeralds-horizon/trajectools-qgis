from qgis.core import QgsProject
import matplotlib.pyplot as plt
from datetime import datetime, time

# Get the active layer
layer = iface.activeLayer()

if not layer:
    raise ValueError("No active layer selected.")

# Check for selected features
selected_features = layer.selectedFeatures()
if not selected_features:
    raise ValueError("No features are selected in the active layer.")

# Check if the required fields exist
field_names = [field.name() for field in layer.fields()]
if 'speed_kmh' not in field_names or 'start_time' not in field_names:
    raise ValueError("Required fields 'speed_kmh' and/or 'start_time' not found in the layer.")

# Define time windows
time_window_1_start = time(12, 0)
time_window_1_end = time(14, 0)
time_window_2_start = time(16, 0)
time_window_2_end = time(18, 0)

# Lists to store speed values per time window
speeds_window_1 = []
speeds_window_2 = []

# Extract and classify data
for feature in selected_features:
    speed = feature['speed_kmh']
    timestamp = feature['start_time']

    if speed is not None and timestamp is not None:
        try:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            elif hasattr(timestamp, 'toPyDateTime'):
                timestamp = timestamp.toPyDateTime()

            t = timestamp.time()

            if time_window_1_start <= t < time_window_1_end:
                speeds_window_1.append(speed)
            elif time_window_2_start <= t < time_window_2_end:
                speeds_window_2.append(speed)

        except Exception as e:
            print(f"Skipping feature due to error: {e}")

# Check data
if not speeds_window_1 and not speeds_window_2:
    raise ValueError("No speed data found in the specified time windows.")

# Plot normalized histograms (density=True)
plt.figure(figsize=(12, 6))

plt.hist(speeds_window_1, bins=20, alpha=0.7, label='12:00–14:00', color='skyblue', density=True)
plt.hist(speeds_window_2, bins=20, alpha=0.7, label='16:00–18:00', color='salmon', density=True)

plt.xlabel('Speed (km/h)')
plt.ylabel('Probability Density')
plt.title('Normalized Speed Distribution: 12:00–14:00 vs 16:00–18:00')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
