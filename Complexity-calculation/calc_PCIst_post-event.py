### Script to compute PCIst for post TTA-SW events on a per-subject basis.
### Ensure that calc_PCIst.py is executed beforehand.

import mne
import numpy as np
import pandas as pd
import os
import re  

input_folder_excel = r"D:\markers_ttasw_isolated"
input_folder_fif = r"D:\clean_fif"
output_base_folder = r"D:\response_post"

subject_names = [] # "subject's-last-name_gestational-age" for example "MASHMOUSHI_25.5"

for subject in subject_names:
    excel_file = os.path.join(input_folder_excel, f"markers_{subject}_isolated.xlsx")
    fif_file = os.path.join(input_folder_fif, f"{subject}.fif")

    if not os.path.exists(excel_file) or not os.path.exists(fif_file):
        print(f"Skipping {subject}: Missing Excel or FIF file.")
        continue

    raw = mne.io.read_raw_fif(fif_file, preload=True)
    event_data = pd.read_excel(excel_file)

    results = []
    for index in range(len(event_data)):
        ttasw_start = event_data.iloc[index]['ttasw_start']
        ttasw_end = event_data.iloc[index]['ttasw_end']

        if ttasw_start - 10 < 0:
            continue

        # Selection of baseline window: 2-second window with lowest power window in the last 10s preceding the event
        raw_base = raw.copy().crop(tmin=ttasw_start - 10, tmax=ttasw_start)
        base_data = raw_base.get_data()
        sampling_rate = raw_base.info['sfreq']
        window_size = int(2 * sampling_rate)

        min_power = float('inf')
        baseline_start = None
        for start_idx in range(0, base_data.shape[1] - window_size + 1):
            end_idx = start_idx + window_size
            window_data = base_data[:, start_idx:end_idx]
            window_power = (window_data ** 2).sum()

            if window_power < min_power:
                min_power = window_power
                baseline_start = start_idx / sampling_rate

        if baseline_start is not None:
            baseline_window = (baseline_start, baseline_start + 2)
        else:
            raise ValueError("Could not determine baseline window.")

        baseline_start_idx = int(baseline_start * sampling_rate)
        baseline_end_idx = baseline_start_idx + window_size
        selected_baseline_data = base_data[:, baseline_start_idx:baseline_end_idx]
        min_amp_baseline = selected_baseline_data.min()
        max_amp_baseline = selected_baseline_data.max()

        raw_baseline = raw_base.copy().crop(
            tmin=baseline_start, 
            tmax=min(baseline_start + 2, raw_base.times[-1])
        )

        # Selection of response window, in this case, 2-second window after 0.5s delay following event's offset 
        raw_response = raw.copy().crop(tmin=ttasw_end + 0.5, tmax=ttasw_end + 2.5)
        raw_response_data = raw_response.get_data()
        min_amp_response = raw_response_data.min()
        max_amp_response = raw_response_data.max()

        raw_event = raw.copy().crop(tmin=ttasw_start, tmax=ttasw_end)
        raw_event_data = raw_event.get_data()
        min_amp_event = raw_event_data.min()
        max_amp_event = raw_event_data.max()

        raw_input = mne.concatenate_raws([raw_baseline, raw_response])

        par = {
            'baseline_window': (raw_input.times[0], raw_input.times[0] + 2),
            'response_window': (raw_input.times[0] + 2, raw_input.times[-1]),
            'k': 1.2, 'min_snr': 1, 'max_var': 99, 'embed': False, 'n_steps': 100
        }

        pci_result = calc_PCIst(raw_input.get_data(), raw_input.times, **par, full_return=True)
        pci_value = pci_result['PCI']
        svd_components = pci_result['pre_signal_svd']
        principal_components = pci_result['signal_svd']

        results.append({
            'Event Index': index + 1,
            'Start Time': ttasw_start,
            'End Time': ttasw_end,
            'Event Duration': ttasw_end - ttasw_start,
            'Baseline Window Start': baseline_window[0],
            'Baseline Window End': baseline_window[1],
            'PCI Value': pci_value,
            'Min Amp Baseline': min_amp_baseline,
            'Max Amp Baseline': max_amp_baseline,
            'Min Amp Event': min_amp_event,
            'Max Amp Event': max_amp_event,
            'Min Amp Response': min_amp_response,
            'Max Amp Response': max_amp_response,
            'Number of Principal Components': len(principal_components),
            'Optimal Threshold Pair': pci_result.get('max_thresholds', None) if pci_value != 0 else None
        })

    results_df = pd.DataFrame(results)
    results_df.to_excel(os.path.join(output_base_folder, f"PCI_{subject}.xlsx"), index=False)
    print(f"\nPCI calculation completed for {subject} and results saved.")
