### Script to generate Figure 2B and 2D

import os, glob
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import pingouin as pg
from statsmodels.stats.multitest import multipletests

folder = r"D:\response_event" # for figure 2B
#folder = r"D:\response_post" # for figure 2D

# Load data and assign age groups
subject_data = []

for file in glob.glob(os.path.join(folder, "*.xlsx")):
    try:
        filename = os.path.basename(file)
        wga = round(float(filename.split("_")[-1].replace(".xlsx", "")))
        subject = filename.split("_")[-2]
        df = pd.read_excel(file)

        pci = df["PCI Value"].dropna()
        if pci.empty:
            continue

        age_dict = {
            range(26, 29): "26–28",
            range(29, 31): "29–30",
            range(31, 33): "31–32"
        }
        
        age_group = next((label for r, label in age_dict.items() if wga in r), None)
        if age_group is None:
            continue

        subject_data.append({
            "Subject": subject,
            "wGA": wga,
            "Age Group": age_group,
            "Mean PCI": pci.mean()
        })

    except Exception as e:
        print(f"Error with file {file}: {e}")

df = pd.DataFrame(subject_data)

# === Boxplot ===
fig, ax = plt.subplots(figsize=(4, 3))
df.boxplot(
    column="Mean PCI", by="Age Group", 
    grid=False, patch_artist=True, ax=ax
    showfliers=False, 
    boxprops=dict(facecolor='lightgray', color='black'),       
    medianprops=dict(color='black', linewidth=1.5),              
    whiskerprops=dict(color='black', linewidth=1.5),           
    capprops=dict(color='black', linewidth=1.5)               
)

ax.set_xlabel("Age Group (wGA)", fontweight='semibold')
ax.set_ylabel("Mean Complexity Index", fontweight='semibold')
plt.suptitle("")
plt.title("")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(1.5)
ax.spines['left'].set_linewidth(1.5)
plt.setp(ax.get_xticklabels(), fontweight='bold')
plt.setp(ax.get_yticklabels(), fontweight='bold')
plt.tight_layout()
plt.show()

# === Pairwise Welch’s t-tests + Cohen’s d + BF10 + FDR correction ===
group_names = ["26–28", "29–30", "31–32"]
p_vals = []
results = []

for i in range(len(group_names)):
    for j in range(i + 1, len(group_names)):
        g1 = df[df["Age Group"] == group_names[i]]["Mean PCI"]
        g2 = df[df["Age Group"] == group_names[j]]["Mean PCI"]

        t_stat, p_val = ttest_ind(g1, g2, equal_var=False)
        d = pg.compute_effsize(g1, g2, eftype='cohen')
        bf = pg.bayesfactor_ttest(t=t_stat, nx=len(g1), ny=len(g2), paired=False)

        p_vals.append(p_val)
        results.append((group_names[i], group_names[j], t_stat, p_val, d, bf))

reject, pvals_corrected, _, _ = multipletests(p_vals, method='fdr_bh')

print("\nPairwise comparisons with FDR correction (Mean PCI):")
for i, (g1, g2, t_stat, p_val, d, bf) in enumerate(results):
    print(f"{g1} vs {g2}: t = {t_stat:.3f}, p = {p_val:.4f}, p_corrected = {pvals_corrected[i]:.4f}, d = {d:.3f}, BF10 = {bf:.3f}")
