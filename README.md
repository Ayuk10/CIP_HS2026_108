# Road Collisions, Traffic Volume and Weather Conditions in Great Britain (2000–2025)

### A Comparative Analysis of Road Fatalities in Great Britain and Switzerland

**Course:** W.MSCDAI_CIP02.H26 
**Group:** 108  
**Author:** Ayuk isaac Asek  
**University:** Lucerne University of Applied Sciences and Arts (HSLU)

## 1. Project Overview

This Python data science project investigates the relationship between road traffic volume, weather conditions and road collisions in Great Britain from 2000 to 2025. It also compares long-term road fatality rates between Great Britain and Switzerland.

The project focuses on collecting, cleaning, transforming, integrating and visualizing publicly available data using Python.

## 2. Research Questions

1. What is the relationship between annual average daily traffic volume and nearby road collisions in Great Britain?
2. How are weather conditions associated with road collision frequency and severity?
3. How have road traffic fatalities per 100,000 inhabitants changed in Great Britain and Switzerland between 2000 and 2025?

## 3. Data Sources and Collection Methods

| Dataset | Source | Collection Method |
|---|---|---|
| Road traffic volume | UK Department for Transport (DfT) | REST API requests |
| Road collisions | DfT STATS19 | Downloadable historical CSV datasets |
| Historical weather | Open-Meteo ERA5 | Automated API requests |
| Road fatalities and population | DfT and Swiss Federal Statistical Office | Web scraping to discover official statistical datasets, followed by data extraction and processing |

The analysis covers 2000–2025.

### Data Acquisition Techniques

- **API integration:** Python HTTP requests were used to retrieve traffic and historical weather data.
- **Web scraping:** `requests` and `BeautifulSoup` were used to identify official statistical dataset links.
- **File processing:** `pandas` was used to load, combine and transform historical datasets.
- **Data integration:** Spatial and temporal matching connected traffic, collision and weather observations.

## 4. Python Notebooks

The `Notebooks/` directory contains six Marimo notebooks:

| Notebook | Description |
|---|---|
| `01_traffic_api.py` | Collects annual road traffic data |
| `02_collision_data.py` | Collects and consolidates collision records |
| `03_weather_data.py` | Retrieves historical weather observations |
| `04_road_fatalities.py` | Collects and prepares GB and Swiss fatality statistics |
| `05_data_cleaning.py` | Validates, cleans and prepares datasets |
| `06_exploratory_analysis.py` | Performs spatial matching, analysis and visualization |

## 5. Technologies and Libraries

- Python
- Marimo
- pandas and NumPy
- requests and BeautifulSoup
- SciPy (`cKDTree`)
- Matplotlib

## 6. Running the Project

Install the required Python libraries:

```bash
pip install marimo pandas numpy requests beautifulsoup4 scipy matplotlib
```

Clone the repository:

```bash
git clone https://github.com/Ayuk10/CIP_HS2026_108.git
cd CIP_HS2026_108
```

Open the notebooks using Marimo:

```bash
marimo edit Notebooks/01_traffic_api.py
```

Execute the notebooks in numerical order, starting with data acquisition and ending with exploratory analysis.

The notebooks use a local `Data/` directory for intermediate and processed CSV files. Some file paths are configured for the original Windows project directory and must be adjusted when running on another computer.

## 7. Key Findings

- Higher traffic volumes were associated with more nearby collisions, although the relationship was relatively weak.
- Weather conditions showed differences in collision frequency and severity, with geographical factors influencing the observed associations.
- Road fatality rates declined by 62.36% in Great Britain and 71.47% in Switzerland between 2000 and 2025.

## 8. Author and Contributions

**Author:** Ayuk Isaac Asek

This project was completed individually. The author was responsible for:

- Research design and identification of data sources.
- Development of Python scripts for API requests and web scraping.
- Data acquisition, validation, cleaning and transformation.
- Spatial and temporal matching of datasets.
- Exploratory analysis, visualization and interpretation.
- Project documentation and preparation of the GitHub repository.

## 9. Data Sources

- [UK Department for Transport — Road Traffic Statistics](https://roadtraffic.dft.gov.uk/)
- [UK Department for Transport — Road Safety Statistics](https://www.gov.uk/government/statistical-data-sets/road-safety-statistics-data-tables)
- [Open-Meteo — Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
- [Swiss Federal Statistical Office](https://www.bfs.admin.ch/)

## 10. Project Documentation

The final project report is submitted separately through HSLU ILIAS. This repository contains the Python implementation and supporting documentation.
