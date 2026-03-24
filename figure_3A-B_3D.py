### Script to generate Figure 3A, 3B, and 3D

import os, re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mne

# Paths
fif_folder = r"D:\clean_fif"
event_folder = r"D:\markers_ttasw_isolated_10s"
input_folder = r"D:\movingwindow_results"

# Age groups
colors = {"26–28": "blue", "29-30": "green", "31–32": "red"}
labels = {"26–28": "26–28 wGA", "29-30": "29–30 wGA", "31–32": "31–32 wGA"}

def age_group(a):
    a = round(a)
    return "26–28" if 26 <= a <= 28 else "29-30" if 29 <= a <= 30 else "31–32" if 31 <= a <= 32 else None

time_axis = np.arange(2, 20.5, 0.5)

# -------------------------------------------------------------------------
# EEG (event-locked)
groups = {"26–28": {}, "29-30": {}, "31–32": {}}

for f in os.listdir(fif_folder):
    if not f.endswith(".fif"): continue

    m = re.match(r"(.+?)_(\d+(?:\.\d+)?)\.fif", f)
    if not m: continue

    subj, age = m.groups()
    ag = age_group(float(age))
    if not ag: continue

    raw = mne.io.read_raw_fif(os.path.join(fif_folder, f), preload=True)
    df = pd.read_excel(os.path.join(event_folder, f"markers_ttasw_{subj}_{age}_isolated_10s.xlsx"))
    events = []
    
    for s in df["ttasw_start"]:
        start, end = s - 10, s + 10
        if start < 0 or end > raw.times[-1]: continue

        seg = raw.copy().get_data(
            start=int(start * raw.info["sfreq"]),
            stop=int(end * raw.info["sfreq"])
        )
        events.append(seg)

    if events:
        groups[ag][f] = events

avg_eeg, sem_eeg = {}, {}

for ag, subj_dict in groups.items():
    subj_means = []

    for ev in subj_dict.values():
        ev_mean = [np.mean(e, axis=0) for e in ev]
        minlen = min(map(len, ev_mean))
        subj_means.append(np.mean([e[:minlen] for e in ev_mean], axis=0))

    if subj_means:
        minlen = min(map(len, subj_means))
        subj_means = np.array([s[:minlen] for s in subj_means])

        avg_eeg[ag] = np.mean(subj_means, axis=0) * 1e6
        sem_eeg[ag] = np.std(subj_means, axis=0) / np.sqrt(len(subj_means)) * 1e6

times_eeg = np.arange(minlen) / raw.info["sfreq"]

# -------------------------------------------------------------------------
# Moving window (PCI + amplitude)
age_complex = {"26–28": [], "29-30": [], "31–32": []}
age_amp = {"26–28": [], "29-30": [], "31–32": []}

for f in os.listdir(input_folder):
    m = re.match(r"PCI_(.+?)_(\d+(?:\.\d+)?).xlsx", f)
    if not m: continue

    subj, wga = m.groups()
    grp = age_group(float(wga))
    if not grp: continue

    df = pd.read_excel(os.path.join(input_folder, f))

    df["Amp"] = (df["Max Amp Response"] - df["Min Amp Response"]) * 1e6

    pci_vals = [g["PCI Value"].values for _, g in df.groupby("Event Index") if len(g) == 37]
    amp_vals = [g["Amp"].values for _, g in df.groupby("Event Index") if len(g) == 37]

    if pci_vals:
        age_complex[grp].append(pd.DataFrame(pci_vals).mean(axis=0).values)
    if amp_vals:
        age_amp[grp].append(pd.DataFrame(amp_vals).mean(axis=0).values)

avg_complex = {g: np.mean(v, axis=0) for g, v in age_complex.items() if v}
sem_complex = {g: np.std(v, axis=0)/np.sqrt(len(v)) for g, v in age_complex.items() if v}

avg_amp = {g: np.mean(v, axis=0) for g, v in age_amp.items() if v}
sem_amp = {g: np.std(v, axis=0)/np.sqrt(len(v)) for g, v in age_amp.items() if v}

# -------------------------------------------------------------------------
# All on one figure 
fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

# EEG, Figure 3A
for ag, col in colors.items():
    if ag in avg_eeg:
        m, s = avg_eeg[ag], sem_eeg[ag]
        axes[0].plot(times_eeg, m, color=col, linewidth=1.5, label=labels[ag])
        axes[0].fill_between(times_eeg, m-s, m+s, color=col, alpha=0.25)

axes[0].set_ylabel("Amplitude (µV ± SEM)", fontweight='semibold')
axes[0].grid(True, alpha=0.4)

# Amplitude, Figure 3B
for ag, col in colors.items():
    if ag in avg_amp:
        m, s = avg_amp[ag], sem_amp[ag]
        axes[1].plot(time_axis, m, '-o', color=col, linewidth=1.5)
        axes[1].fill_between(time_axis, m-s, m+s, color=col, alpha=0.25)

axes[1].set_ylabel("Mean Amplitude (µV ± SEM)", fontweight='semibold')
axes[1].grid(True, alpha=0.4)

# Complexity, Figure 3D
for ag, col in colors.items():
    if ag in avg_complex:
        m, s = avg_complex[ag], sem_complex[ag]
        axes[2].plot(time_axis, m, '-o', color=col, linewidth=1.5)
        axes[2].fill_between(time_axis, m-s, m+s, color=col, alpha=0.25)

axes[2].set_ylabel("Complexity Index (± SEM)", fontweight='semibold')
axes[2].set_xlabel("Time (s)", fontweight='semibold')
axes[2].grid(True, alpha=0.4)

axes[2].set_xlabel("Time (s)", fontweight='semibold') 
axes[2].set_xlim(-0.3, 20.3) 
axes[2].set_xticks(np.arange(0, 20.5, 0.5)) 
axes[2].set_xticklabels( [f"{int(x - 10)}" if (x % 1 == 0) 
                          else "" for x in np.arange(0, 20.5, 0.5)], 
                        fontweight='bold' )

axes[0].legend(loc="upper right", frameon=True)

plt.tight_layout()
plt.show()
