# CMS Medicare Part D — Geographic Drug Surveillance

A geographic disease burden surveillance tool built on Medicare Part D prescribing data. By mapping per-capita drug utilization across U.S. states, the project uses prescribing patterns as a proxy for regional disease prevalence — an approach used in pharmacoepidemiology and environmental health research to generate hypotheses about where and why certain conditions cluster.

## Streamlit App

An interactive web application allows dynamic exploration of any drug in the dataset. Users select a drug by therapeutic category, toggle between claims per 100k enrollees and cost per enrollee, and view a choropleth map alongside state rankings.

To run locally:

```bash
py -m streamlit run app.py
```

## Analytical Approach

Raw claim counts reflect population size and are not analytically meaningful for geographic comparison. All metrics are normalized by state-level Part D enrollment to produce per-capita rates, revealing true variation in prescribing access and disease burden.

Geographic prescribing clusters can reflect:

- Regional variation in disease prevalence driven by environmental, occupational, or demographic exposures
- Access to specialty care and prescribing infrastructure
- Socioeconomic and insurance coverage patterns

This tool surfaces those signals for further investigation. Caution is required when interpreting results — prescribing patterns do not establish causation and are subject to confounding by age distribution, access to care, and coding variation.

## Project Structure

```
app.py                                       # Streamlit web application
notebooks/
├── 00_build_database.ipynb                  # Data ingestion — loads CSVs into SQLite
├── 01_data_exploration.ipynb                # Dataset structure, coverage, suppression
└── 02_case_study/
    ├── 01_drug_selection.ipynb              # Methodology: drug selection and normalization
    └── 02_geographic_map.ipynb             # Methodology: choropleth map construction
```

## Case Study: Lenalidomide (Revlimid)

Lenalidomide is an oral immunomodulatory agent used almost exclusively for multiple myeloma. In 2023 it was the highest-cost drug in Medicare Part D at **$3.86 billion** nationally, with approximately **$104,000 spent per beneficiary per year**. Because it is single-indication, its prescribing geography serves as a reasonable proxy for regional multiple myeloma treatment access.

**Interactive map:** [lenalidomide_map.html](notebooks/02_case_study/lenalidomide_map.html)

## Data Sources

**Medicare Part D Prescribers by Geography and Drug (2023)**
CMS public use file — one row per drug per geographic unit, with total claims, beneficiaries, prescribers, and drug cost. Available at [data.cms.gov](https://data.cms.gov).

**Medicare Monthly Enrollment (2023)**
CMS state-level Part D enrollment counts used for per-capita normalization. Available at [data.cms.gov](https://data.cms.gov).

Raw data files are excluded from this repository via `.gitignore` due to size.

## Tools

Python, pandas, SQLite, Plotly, Streamlit

## Setup

1. Download source CSVs from data.cms.gov and place in `data/`
2. Run `00_build_database.ipynb` to build the local SQLite database
3. Launch the app with `py -m streamlit run app.py`, or run the notebooks in order