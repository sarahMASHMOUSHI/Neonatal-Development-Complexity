### Script to generate Figures 2C and 2E
# pairwise t-tests: time window vs mean baseline

import os, re
import pandas as pd
from scipy.stats import ttest_rel
from statsmodels.stats.multitest import multipletests

# --- Settings ---
folder = r"D:\results_movingwindow"
age_bins = [(26, 28, "26–28"), (29, 30, "29–30"), (31, 32, "31–32")]
n_windows = 37


def load_mean_curves(prefix, value_col=None, scale=1.0):
    # Load excel files, compute mean curve per subject, return df
    rows = []
    for f in os.listdir(folder):
        if not f.endswith(".xlsx") or not f.startswith(prefix):
            continue
        m = re.match(rf"{prefix}_(.+?)_(\d+(?:\.\d+)?).xlsx", f)
        if not m: 
            continue
        subj, age = m.group(1), float(m.group(2))
        try:
            df = pd.read_excel(os.path.join(folder, f))
            if value_col:
                df["Value"] = (df[value_col[0]] - df[value_col[1]]) * scale
            else:
                df["Value"] = df["PCI Value"] * scale
            valid = [g["Value"].values for _, g in df.groupby("Event Index") if len(g) == n_windows]
            if not valid:
                continue
            mean_curve = pd.DataFrame(valid).mean(axis=0).tolist() # Average across events for each time window
            
            for lo, hi, label in age_bins:
                if lo <= round(age) <= hi:
                    rows.append({"Subject": subj, "Age Group": label,
                                 **{f"Win_{i+1}": v for i, v in enumerate(mean_curve)}})
                    break
        except:
            continue
    df_out = pd.DataFrame(rows)
    if df_out.empty:
        raise ValueError(f"No valid data found for {prefix}")
    return df_out

# Load amplitude and complexity data
df_amp = load_mean_curves("PCI", value_col=("Max Amp Response", "Min Amp Response"), scale=1e6)
df_complex = load_mean_curves("PCI")  # PCI Value already in df

# pairwise: windows vs baseline with FDR 
def pairwise_vs_baseline(df, n_baseline=17, label=""):
    print(f"\n=== {label} windows vs baseline (FDR corrected) ===")
    for group, sub in df.groupby("Age Group"):
        print(f"\n--- {group} ---")
        base = sub[[f"Win_{i+1}" for i in range(n_baseline)]].mean(axis=1)
        p_vals, tests = [], []
        for i in range(n_baseline, n_windows):
            t, p = ttest_rel(sub[f"Win_{i+1}"], base)
            p_vals.append(p)
            tests.append((i+1, t, p))
        reject, p_corr, _, _ = multipletests(p_vals, method='fdr_bh')
        for (w, t, p), pc, r in zip(tests, p_corr, reject):
            sig = "***" if pc < 0.001 else "**" if pc < 0.01 else "*" if pc < 0.05 else ""
            print(f"Window {w}: t={t:.3f}, p={p:.4f}, p_corr={pc:.4f} {sig}")

pairwise_vs_baseline(df_amp, label="Amplitude")
pairwise_vs_baseline(df_complex, label="Complexity")

print("\nDone.")
