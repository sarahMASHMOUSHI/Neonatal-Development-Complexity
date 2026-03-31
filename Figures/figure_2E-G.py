### Script to generate figures 2E-G

import os, glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import pingouin as pg

folder_post = r"D:\response_post"
folder_event = r"D:\response_event"

# Load amplitude data
data_amp = {"TTA-SW Event": [], "Post-event": []}
for f in glob.glob(os.path.join(folder_post, "*.xlsx")):
    try:
        subject = os.path.basename(f).split("_")[-2]
        df = pd.read_excel(f)

        # TTA-SW amplitude
        amp_event = (df["Max Amp Event"] - df["Min Amp Event"]).mean() * 1e6
        data_amp["TTA-SW Event"].append((subject, amp_event))

        # Post-event amplitude
        amp_post = (df["Max Amp Response"] - df["Min Amp Response"]).mean() * 1e6
        data_amp["Post-event"].append((subject, amp_post))

    except: pass

# Load PCI data
data_pci = {"TTA-SW Event": [], "Post-event": []}

for f in glob.glob(os.path.join(folder_event,"*.xlsx")): # Event PCI
    try:
        subject = os.path.basename(f).split("_")[-2]
        df = pd.read_excel(f)

        data_pci["TTA-SW Event"].append((subject, df["PCI Value"].mean()))
    except: pass

for f in glob.glob(os.path.join(folder_post,"*.xlsx")): # Post PCI
    try:
        subject = os.path.basename(f).split("_")[-2]
        df = pd.read_excel(f)
        
        data_pci["Post-event"].append((subject, df["PCI Value"].mean()))
    except: pass

# Complexity vs Amplitude, Figures 2F and 2G
def plot_amp_pci_linear(label, color_dot, color_line):
    pts_amp = data_amp[label]
    pts_pci = data_pci[label]
    
    if not pts_amp or not pts_pci: return

    # Match by subject
    amp_dict = {x: y for x, y in pts_amp}
    pci_dict = {x: y for x, y in pts_pci}

    common_x = sorted(set(amp_dict.keys()) & set(pci_dict.keys()))

    x_amp = np.array([amp_dict[x] for x in common_x])   # Amplitude
    y_pci = np.array([pci_dict[x] for x in common_x])   # Complexity

    fig, ax = plt.subplots(figsize=(5,3.5))

    ax.scatter(x_amp, y_pci, color=color_dot, alpha=0.7)
    fit = np.poly1d(np.polyfit(x_amp, y_pci, 1))
    xl = np.linspace(min(x_amp), max(x_amp), 200)
    ax.plot(xl, fit(xl), color=color_line, linewidth=1.5)

    ax.set_xlabel("Mean Amplitude (µV)", fontweight='semibold')
    ax.set_ylabel("Mean Complexity Index", fontweight='semibold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    plt.setp(ax.get_xticklabels(), fontweight='bold')
    plt.setp(ax.get_yticklabels(), fontweight='bold')
    plt.title(label, fontweight='semibold')
    plt.tight_layout()
    plt.show()

    # Stats
    r, p = pearsonr(x_amp, y_pci)
    bf = pg.bayesfactor_pearson(r, len(x_amp))

    print(f"\n{label}:")
    print(f"  n = {len(x_amp)}")
    print(f"  Pearson r = {r:.3f}, p = {p:.4f}")
    print(f"  BF10 = {bf:.3f}")

plot_amp_pci_linear("TTA-SW Event", color_dot='darkorange', color_line='black') # figure 2F
plot_amp_pci_linear("Post-event", color_dot='darkgreen', color_line='black') # figure 2G

# Amplitude vs Age (TTA-SW, Post-event, Baseline), Figure 2E
def plot_amp_only():
    columns = {
        "TTA-SW Event": ("Max Amp Event", "Min Amp Event", "darkorange"),
        "Baseline": ("Max Amp Baseline", "Min Amp Baseline", "steelblue"),
        "Post-event": ("Max Amp Response", "Min Amp Response", "darkgreen")
    }

    data = {}
    for label, (cmax, cmin, color) in columns.items():
        pts = []
        for f in glob.glob(os.path.join(folder_post, "*.xlsx")):
            try:
                wga = float(f.split("_")[-1].replace(".xlsx", ""))
                df = pd.read_excel(f)
                pts.append((wga, (df[cmax] - df[cmin]).mean() * 1e6))
            except: pass
        data[label] = (pts, color)

    fig, ax = plt.subplots(figsize=(5,3.5))

    for label in ["TTA-SW Event", "Post-event", "Baseline"]:
        pts, color = data[label]
        if not pts: continue

        x = np.array([p[0] for p in pts])
        y = np.array([p[1] for p in pts])

        sc = ax.scatter(x, y, color=color, alpha=0.7, label=label)
        fit = np.poly1d(np.polyfit(x, y, 1))
        xl = np.linspace(min(x), max(x), 200)
        ax.plot(xl, fit(xl), color=color, linewidth=1.5)

        r, p = pearsonr(x, y)
        bf = pg.bayesfactor_pearson(r, len(x))

        print(f"{label}:")
        print(f"  Pearson r={r:.3f}, p={p:.4f}, BF10={bf:.3f}\n")

    ax.set_xlabel("Gestational Age (wGA)", fontweight='semibold')
    ax.set_ylabel("Mean Amplitude (µV)", fontweight='semibold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    plt.setp(ax.get_xticklabels(), fontweight='bold')
    plt.setp(ax.get_yticklabels(), fontweight='bold')
    fig.tight_layout()
    plt.show()

    # Separate legend
    fig_leg = plt.figure(figsize=(2.5,1))
    handles, labels = ax.get_legend_handles_labels()
    leg = fig_leg.legend(handles=handles, labels=labels, loc='center', frameon=True, fontsize=12)
    leg.get_frame().set_linewidth(1.5)
    leg.get_frame().set_edgecolor('black')
    for t in leg.get_texts():
        t.set_fontweight('semibold')
    plt.axis('off')
    plt.show()

plot_amp_only()
