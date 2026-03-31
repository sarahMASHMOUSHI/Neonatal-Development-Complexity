### Script to generate Figure 2A and 2C in the manuscript

import os, glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import statsmodels.api as sm
import pingouin as pg

folder = r"D:\response_event" # for figure 2A
#folder = r"D:\response_post" # for figure 2C

data = []

for file in glob.glob(os.path.join(folder, "*.xlsx")):
    try:
        wga = float(file.split("_")[-1].replace(".xlsx", ""))
        df = pd.read_excel(file)

        pci = df["PCI Value"].dropna()
        if not pci.empty:
            data.append((wga, pci.mean()))
    except:
        continue

if not data:
    raise ValueError("No valid data found.")

wga, means = map(np.array, zip(*data))

# Stats
r, p = pearsonr(wga, means)
bf10 = pg.bayesfactor_pearson(r=r, n=len(wga))

print(f"Pearson r = {r:.3f}")
print(f"p-value = {p:.3f}")
print(f"BF10 = {bf10:.3f}")

# Linear regression
X = sm.add_constant(wga)
model = sm.OLS(means, X).fit()

# Plot
plt.figure(figsize=(4, 3))
plt.scatter(wga, means, color='darkorange', alpha=0.7) # for figure 2A
#plt.scatter(wga, means, color='darkgreen', alpha=0.7) # for fgure 2C

x_line = np.linspace(wga.min(), wga.max(), 200)
y_pred = model.predict(sm.add_constant(x_line))
plt.plot(x_line, y_pred, color='black', linewidth=2)

plt.xlabel("Gestational Age (wGA)", fontweight='semibold')
plt.ylabel("Mean Complexity Index", fontweight='semibold')
plt.xticks(fontweight='bold')
plt.yticks(fontweight='bold')

ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(1.5)
ax.spines['left'].set_linewidth(1.5)

plt.tight_layout()
plt.show()
