import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm

# === Step 1: Load specific region from CSV ===
filename = 'D:/scan00.csv'  # your CSV
eye_data = pd.read_csv(filename, skiprows=22, nrows=30, header=None, usecols=range(1, 10))
eye_matrix = eye_data.apply(pd.to_numeric, errors='coerce').dropna(how='any').values

# === Step 2: Replace zeros to avoid log scale crash ===
eye_matrix[eye_matrix == 0] = 1e-12  # Replace 0 with tiny value for log scale

# === Step 3: Plot with vivid color layering and log scale ===
plt.figure(figsize=(10, 6))

img = plt.imshow(
    eye_matrix,
    aspect='auto',
    cmap='jet',
    origin='lower',
    norm=LogNorm(vmin=1e-10, vmax=1e-0)  # Covers BER range from 1e-12 (blue) to 1e-3 (red)
)

# Add colorbar with log ticks
cbar = plt.colorbar(img)
cbar.set_label('Bit Error Rate (log scale)')
cbar.set_ticks([1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e-0])
cbar.ax.set_yticklabels(['1e-10', '1e-9', '1e-8', '1e-7', '1e-6', '1e-5', '1e-4', '1e-3', '1e-2', '1e-1', '1e-0'])

# Add labels and layout
plt.title('Eye Scan for X0Y4 (Log BER Heatmap)')
plt.xlabel('Horizontal Offset (UI)')
plt.ylabel('Vertical Offset (Codes)')
plt.tight_layout()
plt.show()

# === Step 1: Load specific region from CSV ===
filename = 'D:/scan01.csv'  # your CSV
eye_data = pd.read_csv(filename, skiprows=22, nrows=30, header=None, usecols=range(1, 10))
eye_matrix = eye_data.apply(pd.to_numeric, errors='coerce').dropna(how='any').values

# === Step 2: Replace zeros to avoid log scale crash ===
eye_matrix[eye_matrix == 0] = 1e-12  # Replace 0 with tiny value for log scale

# === Step 3: Plot with vivid color layering and log scale ===
plt.figure(figsize=(10, 6))

img = plt.imshow(
    eye_matrix,
    aspect='auto',
    cmap='jet',
    origin='lower',
    norm=LogNorm(vmin=1e-10, vmax=1e-0)  # Covers BER range from 1e-12 (blue) to 1e-3 (red)
)

# Add colorbar with log ticks
cbar = plt.colorbar(img)
cbar.set_label('Bit Error Rate (log scale)')
cbar.set_ticks([1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e-0])
cbar.ax.set_yticklabels(['1e-10', '1e-9', '1e-8', '1e-7', '1e-6', '1e-5', '1e-4', '1e-3', '1e-2', '1e-1', '1e-0'])

# Add labels and layout
plt.title('Eye Scan for X0Y5 (Log BER Heatmap)')
plt.xlabel('Horizontal Offset (UI)')
plt.ylabel('Vertical Offset (Codes)')
plt.tight_layout()
plt.show()

