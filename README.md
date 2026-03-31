This repository contains scripts associated with the manuscript:

"Endogenous high-density electroencephalography analysis of functional network complexity during development in premature neonates."

The repository is organized into two main folders:

1. Complexity-calculation: folder contains scripts for computing the Perturbational Complexity Index (PCIst):

    1.1 calc_PCIst.py
        Core implementation of PCIst, adapted from:
        Comolatti et al. (2019), "A fast and general method to empirically estimate the complexity of brain responses to            perturbations."

    1.2 calc_PCIst_event.py
        Computes PCIst for event-related EEG segments.
   
    1.3 calc_PCIst_post.py
        Computes PCIst for post TTA-SW event activity.

    1.4 calc_PCIst_moving.py
        Computes PCIst using a 2-second sliding window (−10s to +10s around event onset, step size = 0.5s).

    Important: calc_PCIst.py must be available and executed/imported before running scripts 1.2 – 1.4.


2. Figures: folder contains scripts used to reproduce the figures from the manuscript:

    2.1 figure_2A_2C.py
        - Scatter plots of complexity vs. gestational age
        - Event-related (Fig. 2A) and post-event (Fig. 2C)
        - Includes linear regression and statistical outputs: p-value, Pearson correlation, BF10
   
    2.2 figure_2B_2D.py
        - Boxplots across three gestational age groups (26–28, 29–30, 31–32 weeks)
        - Event (Fig. 2B) and post-event (Fig. 2D)
        - Pairwise t-tests with: p-value, t-value, Cohen’s d, BF10
        - Multiple comparison correction using FDR
   
    2.3 figure_2E-G.py
        - Fig. 2E: Amplitude vs. gestational age (event, post-event, baseline)
        - Fig. 2F–G: Complexity vs. amplitude relationships
        - Includes statistical outputs: p-value, Pearson correlation, BF10

    2.4 figure_3A-B_3D.py
        - Fig. 3A: Averaged EEG traces across a 20-second window (−10 to +10 s). Averaging pipeline: channels → events →              subjects → age groups
        - Fig. 3B & 3D: Peak-to-peak amplitude and complexity index. Computed using a 2-second moving window (step = 0.5s).           Shaded regions represent ±1 SEM. Analysis uses isolated events (minimum inter-event interval: 10 s).
   
    2.5 figure_3C_3E.py
        - Pairwise t-tests comparing post-event windows (0.5–10 s) to pre-event baseline (−8 to 0 s)
        - Statistical significance after FDR correction: *p < 0.05, **p < 0.01, **p < 0.001

----------------------------------------------------------------------------------------------------------------------------
Notes:
- Ensure EEG data is preprocessed before running PCIst computations.
- Input formats (e.g., .fif, .xlsx) must match those expected by the scripts.
- All analyses are performed on a per-event and per-subject basis.

Requirements: 
- Python (≥ 3.8)
- Required packages: mne, numpy, pandas, matplotlib, scipy, pingouin (for statistical analysis). 










