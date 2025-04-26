# San Francisco Cordon Pricing Study

This repository contains the data analysis and visualization code for the paper "Effective Congestion Management Through Protective Pricing: An Agent-Based Study of Cordon Schemes in San Francisco". The study evaluates three pricing scenarios (baseline, flat-rate, and income-based) and their impacts on travel behavior, air quality, and other transportation-related outcomes.

## Project Structure

The project is organized into three main components:

1. **Primary Outcomes Analysis** - Analysis and visualization of key metrics reported in the paper (e.g. VMT, mode shift).
2. **INEXUS Analysis** - Analysis of accessibility impacts through consumer surplus metrics.
3. **Air Quality Analysis** - Analysis of air quality impacts under different pricing scenarios.

## Datasets

Due to GitHub storage limitations, only partial code for data processing and visualization is available in this repository. The full data from scenario runs is available upon request.

### Available Data Files

Key data files available in the repository include:

- Trip counts by mode, scenario, and geographic area
- Vehicle miles traveled (VMT) by mode and scenario
- Vehicle hours traveled (VHT) by mode and scenario
- Air quality impacts (PM2.5, NOx, SOx, etc.)
- INEXUS (consumer surplus) metrics by income segment

## Notebooks and Their Outputs

### Primary Outcomes Analysis

- **DataProcesing_1.ipynb**: Reads in events and person-to-vehicles files, adds links travelled, time, and passenger data. Adds population characteristics from person and household info, labels scenario, and exports to CSV.

- **DataProcessing_2.ipynb**: Combines data from all scenarios into a unified dataset, calculates income segments, and models revenue generation from cordon pricing schemes.

- **Plots_Cordon.ipynb**: Produces visualizations specific to the cordon area, including:
  - Mode share comparisons across scenarios
  - VMT changes by mode and scenario
  - Trip count differences with respect to baseline
  - Energy use differences with respect to baseline

- **Plots_SF.ipynb**: Similar to the cordon plots, but focused on impacts across the entire San Francisco area.

- **Plots_SFNoCordon.ipynb**: Analyzes impacts on San Francisco areas outside the cordon.

### INEXUS Analysis

- **INEXUS_CordonFilter.ipynb**: Analyzes consumer surplus (INEXUS) metrics for trips into and out of the cordon area. Key outputs include:
  - Welfare impacts by income segment
  - Revenue generation by scenario
  - Mode share comparisons and changes
  - Social INEXUS accounting for carbon costs

- **INEXUS_SFFilter.ipynb**: Similar INEXUS analysis but for trips within the entire San Francisco area.

### Air Quality Analysis

- **AQ_Analysis.ipynb**: Processes air quality metrics for different scenarios, including:
  - Particle levels (PM2.5, SOA, NOx, NH3, etc.)
  - Comparison of air quality changes across scenarios and geographic areas


## Data Access

While the code in this repository can be used to understand the analysis methodology, the full dataset from scenario runs is not included due to size constraints. For access to the complete dataset, please contact the authors.