
import math

# Parameter Tc-99m dan timbal (Pb) dari Final.py
alpha = 2.558
beta = 1.010
gamma = 4.344

LOWER_BOUND = 1e-10

def calculate_raw_K(x):
    """Menghitung transmisi tanpa clamping."""
    exp_term = math.exp(x * alpha * gamma)
    ratio = beta / alpha
    numerator = exp_term * (1 + ratio) - ratio
    return numerator ** (-1.0 / gamma)

print("x\tK sebelum clamp\tK setelah clamp")
for x in [2.5, 3, 8, 9, 10]:
    raw_K = calculate_raw_K(x)
    clamped_K = max(LOWER_BOUND, min(raw_K, 100.0))
    print(f"{x}\t{raw_K:.6e}\t{clamped_K:.6e}")
