import cv2
import numpy as np

# 1. Load your daytime bike image
image_path = 'img1.jpeg'
img = cv2.imread(image_path)

if img is None:
    print("Error: Could not load the image!")
    exit()

# --- PART 1: CYBERPUNK DAY-TO-NIGHT SHIFT ---
# Step A: Darken the image using Gamma Correction (fakes nighttime)
gamma = 0.4  # Lower number = darker image (0.4 is a good night setting)
inv_gamma = 1.0 / gamma
table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
night_img = cv2.LUT(img, table)

# Step B: The Neon Wash (Boost Blue & Red, Crush Green)
# Convert to float32 so the math doesn't max out at 255 prematurely
float_img = night_img.astype(np.float32)

float_img[:, :, 0] = float_img[:, :, 0] * 1.8  # Massively boost Blue
float_img[:, :, 1] = float_img[:, :, 1] * 0.6  # Kill the Green (removes sunlight feel)
float_img[:, :, 2] = float_img[:, :, 2] * 1.5  # Boost Red for the Magenta vibe

# Lock the colors back into standard image format
cyberpunk_img = np.clip(float_img, 0, 255).astype(np.uint8)


# --- PART 2: THE DIGITAL GLITCH ---
# Split the new neon colors
b, g, r = cv2.split(cyberpunk_img)

# Shift amount (how hard the colors tear apart)
shift_amount = 20 

r_shifted = np.zeros_like(r)
b_shifted = np.zeros_like(b)

# Slice and shift
r_shifted[:, :-shift_amount] = r[:, shift_amount:]
b_shifted[:, shift_amount:]  = b[:, :-shift_amount]

# Recombine with the original green
glitched_colors = cv2.merge([b_shifted, g, r_shifted])


# --- PART 3: CRT SCANLINES ---
# Darken every 4th row by 50% to look like a hacked monitor
glitched_colors[::4, :] = glitched_colors[::4, :] * 0.5

# Final safety clip
final_result = np.clip(glitched_colors, 0, 255).astype(np.uint8)

# Save it!
cv2.imwrite('cyberpunk_glitch_bike.jpg', final_result)
print("Night City Glitch complete! Check your folder.")