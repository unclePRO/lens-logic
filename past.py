import cv2
import numpy as np

# -----------------------------
# 1. Load image
# -----------------------------
img = cv2.imread("img2.jpeg").astype(np.float32) / 255.0
img = cv2.resize(img, (1000, 700))

# -----------------------------
# 2. Desaturation (vintage base)
# -----------------------------
hsv = cv2.cvtColor((img*255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
h, s, v = cv2.split(hsv)
s *= 0.5
hsv = cv2.merge([h, s, v])
desat = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255.0

# -----------------------------
# 3. Soft sepia blend
# -----------------------------
sepia_filter = np.array([[0.272, 0.534, 0.131],
                         [0.349, 0.686, 0.168],
                         [0.393, 0.769, 0.189]], dtype=np.float32)

sepia = cv2.transform(desat, sepia_filter)
sepia = np.clip(sepia, 0, 1)

vintage = desat * 0.6 + sepia * 0.4

# -----------------------------
# 4. Matte fade (film look)
# -----------------------------
matte = vintage * 0.85 + 0.15

# -----------------------------
# 5. Soft blur (film softness)
# -----------------------------
soft = cv2.GaussianBlur(matte, (5, 5), 0.8)

# -----------------------------
# 6. Vignette
# -----------------------------
rows, cols = soft.shape[:2]
kernel_x = cv2.getGaussianKernel(cols, 400)
kernel_y = cv2.getGaussianKernel(rows, 400)
kernel = kernel_y * kernel_x.T
mask = kernel / kernel.max()

for i in range(3):
    soft[:, :, i] *= mask

# -----------------------------
# 7. Slight brown tone (BACKGROUND FEEL)
# -----------------------------
# Add warm tone subtly
soft[:,:,2] += 0.06   # red
soft[:,:,1] += 0.03   # green
soft = np.clip(soft, 0, 1)

# -----------------------------
# 8. SUN RAYS (God rays)
# -----------------------------
center_x = int(cols * 0.7)
center_y = int(rows * 0.2)

X = np.linspace(0, cols-1, cols)
Y = np.linspace(0, rows-1, rows)
X, Y = np.meshgrid(X, Y)

dist = np.sqrt((X - center_x)*2 + (Y - center_y)*2)
dist = dist / dist.max()

rays = 1 - dist

# Smooth rays
for _ in range(3):
    rays = cv2.GaussianBlur(rays, (0,0), 15)

rays = np.repeat(rays[:, :, np.newaxis], 3, axis=2)

# Warm sunlight color
sun_color = np.zeros_like(soft)
sun_color[:,:,2] = 1.0
sun_color[:,:,1] = 0.8

sun_rays = rays * sun_color

# Blend rays
final = soft + sun_rays * 0.35
final = np.clip(final, 0, 1)

# -----------------------------
# 9. Convert to uint8
# -----------------------------
final = (final * 255).astype(np.uint8)

# -----------------------------
# 10. CLEAN UPSCALE (no pixelation)
# -----------------------------
smooth = cv2.bilateralFilter(final, 9, 50, 50)
output = cv2.resize(smooth, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

# -----------------------------
# Save & Show
# -----------------------------
cv2.imwrite("FINAL_PAST_THEME.jpg", output)
cv2.imshow("Final Output", output)
cv2.waitKey(0)
cv2.destroyAllWindows()