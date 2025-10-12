"""Constants for WCAG contrast calculations and related helpers."""

# === sRGB → Linear conversion ===============================================
SRGB_GAMMA = 2.4
SRGB_A = 0.055
SRGB_DIV_LOW = 12.92
SRGB_DIV_HIGH = 1.055

# === Relative luminance coefficients (D65) ==================================
LUMA_R = 0.2126
LUMA_G = 0.7152
LUMA_B = 0.0722

# === Contrast formula constants =============================================
CONTRAST_K = 0.05

# === WCAG thresholds ========================================================
AA_NORMAL = 4.5
AAA_NORMAL = 7.0
AA_LARGE = 3.0
AAA_LARGE = 4.5

# === Brightness adjustment factors =========================================
DARKEN_FACTORS = (0.8, 0.6, 0.4, 0.2)
LIGHTEN_FACTORS = (1.2, 1.4, 1.6, 1.8)
