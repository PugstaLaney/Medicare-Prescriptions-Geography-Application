# CMS Medicare Part D Analysis

Geographic analysis of high-cost oncology drug prescribing in Medicare Part D, with state-level per-capita mapping using Python, SQLite, and Plotly.

## Data Sources

**Medicare Part D Prescribers by Geography and Drug (2023)**
CMS public use file containing prescription drug claims aggregated by drug and geographic unit. Each row represents one drug-state combination with total claims, beneficiaries, prescribers, and drug cost.

**Medicare Monthly Enrollment (2023)**
CMS state-level Medicare enrollment counts used to normalize prescribing metrics by Part D enrollment population.

Both files are publicly available at [data.cms.gov](https://data.cms.gov). Raw data files are excluded from this repository via `.gitignore` due to size.

## Project Structure

```
notebooks/
├── 00_build_database.ipynb        # Loads CSVs into local SQLite database
├── 01_explore/
│   └── 01_explore.ipynb           # Dataset overview and oncology drug survey
└── 02_lenalidomide/
    ├── 01_lenalidomide_explore.ipynb   # National summary and state coverage
    └── 02_lenalidomide_map.ipynb       # Per-capita choropleth map
```

## Module 2: Lenalidomide Geographic Analysis

Lenalidomide (Revlimid) is an oral immunomodulatory drug used primarily for multiple myeloma. In 2023 it was the highest-cost drug in Medicare Part D at **$3.86 billion** nationally, with approximately **$104,000 spent per beneficiary per year**.

Raw claim counts reflect state population size and are not analytically meaningful for geographic comparison. This module normalizes by Part D enrollment to produce claims per 100,000 Medicare Part D enrollees, revealing true variation in prescribing access across states.

**Interactive map:** [lenalidomide_map.html](notebooks/02_lenalidomide/lenalidomide_map.html)

## Tools

- Python, pandas, SQLite, Plotly
- Data source: CMS Medicare Part D (2023)

## Setup

1. Download source CSVs from data.cms.gov and place in `data/`
2. Run `00_build_database.ipynb` to build the local database
3. Run module notebooks in order