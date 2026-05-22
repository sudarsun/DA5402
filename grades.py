import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, beta
from scipy.optimize import curve_fit

# Sample data: array of scores (0-100)
np.random.seed(42)
#scores = np.random.normal(loc=70, scale=15, size=500)
#scores = np.clip(scores, 0, 100)

scores = np.array([37.46,77.22,84.98,87.05,20.01,25.73,21.29,75.03,88.23,75.84,82.59,15.13,92.47,74.06,93.36,81.59,33.98,88.93,92.92,79.71,90.24,87.81,89.80,14.44,82.59,79.99,94.41,91.97,91.56,75.07,88.49,0.00,94.67,36.46,82.15,22.97,86.87,88.87,96.71,93.27,89.29,91.94,94.97,89.96,91.15,74.68,90.13,92.63,75.29,78.53,84.76,94.09,80.13,89.69,89.50,82.17,89.55,94.17,93.70,89.93,87.36,90.80,94.65,93.37,93.40,92.82,92.06,92.27,91.33,95.09,96.13,92.36,89.27,89.26,89.77,83.87,78.93,93.51,96.47,86.01,90.60,82.95,92.19,63.42,93.43,42.96,96.40,75.84,83.61,84.32,94.83,92.03,83.31,61.64,27.07,72.33,88.26,88.68,93.93,86.69,81.45,66.95,74.61,91.64,92.24,93.69,26.69,88.43,68.33,70.16,93.46,93.15,85.55,90.51,95.04,93.73,89.34,82.53,60.01,78.80,93.53,73.19,59.88,79.02,74.88,85.45,93.74,47.81,87.63,65.62,92.00,81.06,52.40])

print(f"Score statistics: mean={np.mean(scores):.2f}, std={np.std(scores):.2f}, min={np.min(scores):.2f}, max={np.max(scores):.2f}")

print("\nFiltering scores...")
dropped_scores = scores[scores < 25]  # Filter out scores below 25 for better fitting
scores = scores[scores >= 25]
print(f"Dropped {len(dropped_scores)} scores below 25. Remaining scores: {len(scores)}")

print("\nFitting distributions...")

# Fit Gaussian distribution
mu_gauss, sigma_gauss = norm.fit(scores)
print(f"Gaussian fit: μ={mu_gauss:.2f}, σ={sigma_gauss:.2f}")

# Fit Beta distribution (scale to 0-1, fit, then scale back)
scores_norm = scores / 100
alpha, beta_param, loc, scale = beta.fit(scores_norm)
print(f"Beta fit: α={alpha:.2f}, β={beta_param:.2f}")

# Compute grade cutoffs using Gaussian distribution (equal probability approach)
# Grade distribution: S(20%), A(20%), B(20%), C(20%), D(10%), E(10%)

cutoffs_gauss = [
    norm.ppf(0.10, mu_gauss, sigma_gauss),    # E: 5-15%
    norm.ppf(0.20, mu_gauss, sigma_gauss),    # D: 15-35%
    norm.ppf(0.40, mu_gauss, sigma_gauss),    # C: 35-65%
    norm.ppf(0.60, mu_gauss, sigma_gauss),    # B: 65-85%
    norm.ppf(0.80, mu_gauss, sigma_gauss),    # A: 85-95%
    100                                         # S: 95-100%
]

# Compute grade cutoffs using Beta distribution
cutoffs_beta = [
    beta.ppf(0.10, alpha, beta_param, loc, scale) * 100,
    beta.ppf(0.20, alpha, beta_param, loc, scale) * 100,
    beta.ppf(0.40, alpha, beta_param, loc, scale) * 100,
    beta.ppf(0.60, alpha, beta_param, loc, scale) * 100,
    beta.ppf(0.80, alpha, beta_param, loc, scale) * 100,
    100
]

grade_names = ['E', 'D', 'C', 'B', 'A', 'S'] # U is implicitly below E
print("\nGaussian Cutoffs:")
for i, (name, cutoff) in enumerate(zip(grade_names, cutoffs_gauss)):
    print(f"{name}: {cutoff:.1f}")

print("\nBeta Cutoffs:")
for i, (name, cutoff) in enumerate(zip(grade_names, cutoffs_beta)):
    print(f"{name}: {cutoff:.2f}")

# Assign grades using Gaussian cutoffs
def assign_grades(scores, cutoffs):
    grades = []
    for score in scores:
        for i, cutoff in enumerate(cutoffs[:-1]):
            if score < cutoff:
                grades.append(grade_names[i])
                break
        else:
            grades.append('S')
    return grades

grades_gauss = assign_grades(scores, cutoffs_gauss)
grades_beta = assign_grades(scores, cutoffs_beta)

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 8))
fig.suptitle('DA5402: Score and Grade Distributions', fontsize=16)

# Plot 1: Score distribution with Gaussian fit
ax = axes[0, 0]
ax.hist(scores, bins=30, density=True, alpha=0.7, color='blue', edgecolor='black')
x = np.linspace(0, 100, 1000)
ax.plot(x, norm.pdf(x, mu_gauss, sigma_gauss), 'r-', linewidth=2, label='Gaussian fit')
ax.set_xlabel('Score')
ax.set_ylabel('Density')
ax.set_title('Score Distribution with Gaussian Fit')
ax.legend()
ax.grid(alpha=0.3)

# Plot 2: Score distribution with Beta fit
ax = axes[0, 1]
ax.hist(scores, bins=30, density=True, alpha=0.7, color='green', edgecolor='black')
ax.plot(x, beta.pdf(x/100, alpha, beta_param, loc, scale)/100, 'r-', linewidth=2, label='Beta fit')
ax.set_xlabel('Score')
ax.set_ylabel('Density')
ax.set_title('Score Distribution with Beta Fit')
ax.legend()
ax.grid(alpha=0.3)

# Plot 3: Grade distribution (Gaussian)
ax = axes[1, 0]
grade_counts_gauss = [grades_gauss.count(g) for g in grade_names]
colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(grade_names)))
# also add the count on top of each bar
for i, count in enumerate(grade_counts_gauss):
    ax.text(i, count + 1, str(count), ha='center', va='bottom')
    ax.bar(grade_names, grade_counts_gauss, color=colors, edgecolor='black')
ax.set_xlabel('Grade')
ax.set_ylabel('Count')
ax.set_title('Grade Distribution (Gaussian)')
ax.grid(alpha=0.3, axis='y')

# Plot 4: Grade distribution (Beta)
ax = axes[1, 1]
grade_counts_beta = [grades_beta.count(g) for g in grade_names]
# also add the count on top of each bar
for i, count in enumerate(grade_counts_beta):
    ax.text(i, count + 1, str(count), ha='center', va='bottom')
ax.bar(grade_names, grade_counts_beta, color=colors, edgecolor='black')
ax.set_xlabel('Grade')
ax.set_ylabel('Count')
ax.set_title('Grade Distribution (Beta)')
ax.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.show()
