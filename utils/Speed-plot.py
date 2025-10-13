from qgis.core import QgsProject
import matplotlib.pyplot as plt
from datetime import datetime

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

# Lists to store extracted values
timestamps = []
speeds = []

# Extract data from selected features
for feature in selected_features:
    speed = feature['speed_kmh']
    timestamp = feature['start_time']

    if speed is not None and timestamp is not None:
        try:
            # Convert timestamp to datetime object
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            elif hasattr(timestamp, 'toPyDateTime'):
                timestamp = timestamp.toPyDateTime()
            
            timestamps.append(timestamp)
            speeds.append(speed)
        except Exception as e:
            print(f"Skipping feature due to error: {e}")

# Check if we have valid data to plot
if not timestamps or not speeds:
    raise ValueError("No valid data in selected features to plot.")

# Plot using matplotlib
plt.figure(figsize=(10, 6))
plt.scatter(timestamps, speeds, c='green', alpha=0.7)
plt.xlabel('Start Time')
plt.ylabel('Speed (km/h)')
plt.title('Selected Features: Speed over Time')
plt.grid(True)
plt.tight_layout()
plt.show()
