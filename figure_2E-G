### Script to generate figures 2E-G

import os, glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import pingouin as pg

folder_post = r"D:\response_post"
folder_pci_event = r"D:\response_event"

columns_amp = {
    "TTA-SW Event": ("Max Amp Event","Min Amp Event","darkorange"),
    "Post-event": ("Max Amp Response","Min Amp Response","darkgreen")
}

# Load amplitude data
data_amp = {}
for label, (cmax, cmin, color) in columns_amp.items():
    pts = []
    for f in glob.glob(os.path.join(folder_post,"*.xlsx")):
        try:
            wga = float(f.split("_")[-1].replace(".xlsx",""))
            df = pd.read_excel(f)
            pts.append((wga, (df[cmax]-df[cmin]).mean()*1e6))
        except: pass
    data_amp[label] = (pts, color)

# Load PCI data
data_pci = {"TTA-SW Event": [], "Post-event": []}
for f in glob.glob(os.path.join(folder_pci_event,"*.xlsx")):
    try:
        wga = float(f.split("_")[-1].replace(".xlsx",""))
        df = pd.read_excel(f)
        data_pci["TTA-SW Event"].append((wga, df["PCI Value"].mean()))
    except: pass

for f in glob.glob(os.path.join(folder_post,"*.xlsx")):
    try:
        wga = float(f.split("_")[-1].replace(".xlsx",""))
        df = pd.read_excel(f)
        data_pci["Post-event"].append((wga, df["PCI Value"].mean()))
    except: pass

def plot_amp_pci_linear(label):
    pts_amp, color = data_amp[label]
    pts_pci = data_pci[label]
    if not pts_amp or not pts_pci: return

    x_amp, y_amp = np.array([x for x,_ in pts_amp]), np.array([y for _,y in pts_amp])
    x_pci, y_pci = np.array([x for x,_ in pts_pci]), np.array([y for _,y in pts_pci])

    fig, ax1 = plt.subplots(figsize=(5,3.5))

    # Amplitude vs Gestational Age
    sc1 = ax1.scatter(x_amp, y_amp, color=color, alpha=0.7, label="Amplitude")
    fit_amp = np.poly1d(np.polyfit(x_amp, y_amp, 1))
    xl = np.linspace(min(x_amp), max(x_amp), 200)
    ax1.plot(xl, fit_amp(xl), color=color, linewidth=1.5)
    r_amp, p_amp = pearsonr(x_amp, y_amp)
    bf_amp = pg.bayesfactor_pearson(r_amp, len(x_amp))

    ax1.set_xlabel("Gestational Age (wGA)", fontweight='semibold')
    ax1.set_ylabel("Mean Amplitude (µV)", fontweight='semibold')

    # Complexity vs Gestational Age
    ax2 = ax1.twinx()
    sc2 = ax2.scatter(x_pci, y_pci, color='black', alpha=0.7, label="Complexity")
    fit_pci = np.poly1d(np.polyfit(x_pci, y_pci, 1))
    xl2 = np.linspace(min(x_pci), max(x_pci), 200)
    ax2.plot(xl2, fit_pci(xl2), color='black', linewidth=1.5)
    r_pci, p_pci = pearsonr(x_pci, y_pci)
    bf_pci = pg.bayesfactor_pearson(r_pci, len(x_pci))

    ax2.set_ylabel("Mean Complexity Index", fontweight='semibold')

    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_linewidth(1.5)
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['right'].set_linewidth(1.5)
        plt.setp(ax.get_xticklabels(), fontweight='bold')
        plt.setp(ax.get_yticklabels(), fontweight='bold')

    fig.tight_layout()
    plt.title(label, fontweight='semibold')
    plt.show()

    # legend (separate plot)
    fig_leg = plt.figure(figsize=(2.5,1))
    leg = fig_leg.legend(handles=[sc1, sc2], loc='center', frameon=True, fontsize=12)
    leg.get_frame().set_linewidth(1.5)
    leg.get_frame().set_edgecolor('black')
    for t in leg.get_texts():
        t.set_fontweight('semibold')
    plt.axis('off')
    plt.show()

    # Amplitude vs Complexity
    r_ap, p_ap = pearsonr(y_amp, y_pci)
    bf_ap = pg.bayesfactor_pearson(r_ap, len(y_amp))

    print(f"\n{label}:")
    print(f"  Amplitude vs Age: Pearson r={r_amp:.3f}, p={p_amp:.4f}, BF10={bf_amp:.3f}")
    print(f"  Complexity vs Age: Pearson r={r_pci:.3f}, p={p_pci:.4f}, BF10={bf_pci:.3f}")
    print(f"  Amplitude vs Complexity: Pearson r={r_ap:.3f}, p={p_ap:.4f}, BF10={bf_ap:.3f}")

# Run for all labels (event and post-event)
for label in columns_amp.keys():
    plot_amp_pci_linear(label)


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
