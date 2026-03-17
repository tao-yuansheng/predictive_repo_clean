# Bug Report

## Bug 1
Location : line 15, load data block
Type      : other
Severity  : Major
What it does wrong : Reads `../../data/raw/dataset.csv` relative to the caller's working directory instead of the script location.
Why it matters     : The script can fail immediately with `FileNotFoundError` when launched from a different directory.

## Bug 2
Location : line 22, clean missing values block
Type      : data bug
Severity  : Critical
What it does wrong : Drops rows only when `workclass` is `?`, leaving `occupation` and `native.country` sentinel-missing values in the data.
Why it matters     : The pipeline silently trains on partially uncleaned data and uses more rows than intended (`(30725, 15)` vs `(30162, 15)` after the fix).

## Bug 3
Location : lines 29-30 and plot save calls on lines 39, 50, and 58
Type      : silent error
Severity  : Major
What it does wrong : Creates and writes to `output/` relative to the caller's working directory rather than the script directory.
Why it matters     : The script can appear to succeed while saving files into the wrong folder, which breaks reproducibility.

## Bug 4
Location : lines 71-73, categorical encoding block
Type      : logic bug
Severity  : Minor
What it does wrong : Reuses one `LabelEncoder` object across all categorical columns, overwriting its mapping on every iteration.
Why it matters     : Any later inverse transform or saved preprocessing metadata would be wrong because only the final column mapping survives.

## Bug 5
Location : line 94, scaling block
Type      : leakage
Severity  : Critical
What it does wrong : Calls `fit_transform` on the test set instead of applying the scaler fitted on the training data.
Why it matters     : Test-set statistics leak into evaluation, so the reported accuracy is based on an invalid preprocessing pipeline.

## Bug 6
Location : import block, lines 7-8
Type      : other
Severity  : Minor
What it does wrong : Imports Matplotlib without forcing a non-interactive backend or a writable config directory.
Why it matters     : The script can hang or fail in a fresh headless environment before any plots or metrics are produced.

## Severity Notes
- Critical bugs silently produce incorrect data or invalid evaluation.
- Major bugs break portability or save outputs to the wrong place.
- Minor bugs damage preprocessing correctness even if the current script does not crash.

## Before / After Metrics
- Buggy-equivalent accuracy: `0.8202`
- Fixed-equivalent accuracy: `0.8168`
- Accuracy change: `-0.0033`
- Interpretation: the fixed pipeline is slightly less accurate because it removes all sentinel-missing rows and stops re-fitting the scaler on the test set.

## Silent Bug Detection
- Bug 4 was detected by static inspection: one `LabelEncoder` instance is created once and overwritten in the loop.
- Bug 5 was detected by static inspection: `fit_transform` on `X_test` proves the scaler is being re-fit on evaluation data.
- Bugs 1 and 3 were detected by checking that plain relative paths depend on the process working directory, not the script path.
- Bug 6 was confirmed during verification when the plotting import stalled until a writable headless Matplotlib configuration was supplied.
