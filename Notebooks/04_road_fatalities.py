import marimo

__generated_with = "0.25.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 04 – Road Traffic Fatality Data Acquisition

    **Sources:** UK Department for Transport (DfT) and Swiss Federal Statistical Office (FSO)
    **Period:** 2000–2025

    Acquire and inspect annual road traffic fatalities and population data for Great Britain and Switzerland.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.1 Data Source Exploration

    Identify official road fatality statistics and their download links for Great Britain and Switzerland.
    """)
    return


@app.cell
def _():
    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin

    source_url = (
        "https://www.gov.uk/government/statistical-data-sets/"
        "road-safety-statistics-data-tables"
    )

    response = requests.get(source_url, timeout=60)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Find links mentioning RAS0101
    for link in soup.find_all("a", href=True):
        title = link.get_text(" ", strip=True)
        url = urljoin(source_url, link["href"])

        if "RAS0101" in title.upper() or "RAS0101" in url.upper():
            print("Title:", title)
            print("URL:", url)
            print("-" * 60)
    return BeautifulSoup, requests, urljoin


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.2 Great Britain Fatality Data Download

    Download and inspect historical road traffic fatality statistics from the UK Department for Transport (DfT).
    """)
    return


@app.cell
def _(requests):
    from pathlib import Path
    from io import BytesIO
    import pandas as pd
    import zipfile

    # Local project folder
    gb_output_dir = (
        Path.home()
        / "Documents"
        / "CIP_HS2026_Group_108"
        / "Data"
        / "Fatalities"
    )
    gb_output_dir.mkdir(parents=True, exist_ok=True)

    # Official Department for Transport dataset
    gb_fatalities_url = (
        "https://assets.publishing.service.gov.uk/media/"
        "6a6398df9a419980593b2bdf/ras0101.ods"
    )

    # Download the dataset
    gb_fatalities_response = requests.get(
        gb_fatalities_url,
        timeout=120
    )
    gb_fatalities_response.raise_for_status()

    # Verify the downloaded spreadsheet
    if not zipfile.is_zipfile(BytesIO(gb_fatalities_response.content)):
        raise ValueError(
            "The downloaded content is not a valid ODS spreadsheet."
        )

    # Save locally
    gb_file_path = gb_output_dir / "RAS0101_GB.ods"
    gb_file_path.write_bytes(gb_fatalities_response.content)

    print("Downloaded successfully:", gb_file_path)
    print(
        "File size:",
        round(gb_file_path.stat().st_size / 1024, 2),
        "KB"
    )

    # Inspect spreadsheet sheets
    gb_sheets = pd.read_excel(
        gb_file_path,
        engine="odf",
        sheet_name=None,
        header=None
    )

    for gb_sheet_name, gb_df in gb_sheets.items():
        print(f"\nSheet: {gb_sheet_name}")
        print(gb_df.head(12).to_string(index=False, header=False))
    return Path, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.3 Great Britain Fatality Data Extraction

    Extract annual road traffic deaths and population figures for Great Britain from 2000 to 2025.
    """)
    return


@app.cell
def _(Path, pd):


    gb_source_file = (
        Path.home()
        / "Documents"
        / "CIP_HS2026_Group_108"
        / "Data"
        / "Fatalities"
        / "RAS0101_GB.ods"
    )

    # Read the casualties worksheet
    gb_casualties_raw = pd.read_excel(
        gb_source_file,
        sheet_name="Casualties",
        engine="odf",
        header=None
    )

    # Select year, all road users killed, and population
    gb_fatalities = gb_casualties_raw.iloc[:, [0, 6, 10]].copy()

    gb_fatalities.columns = [
        "year",
        "road_deaths",
        "population_millions"
    ]

    # Convert to numeric values
    for gb_column in gb_fatalities.columns:
        gb_fatalities[gb_column] = pd.to_numeric(
            gb_fatalities[gb_column],
            errors="coerce"
        )

    # Keep the research period
    gb_fatalities = gb_fatalities[
        gb_fatalities["year"].between(2000, 2025)
    ].copy()

    gb_fatalities["year"] = gb_fatalities["year"].astype(int)

    # Calculate fatalities per 100,000 inhabitants
    gb_fatalities["fatalities_per_100k"] = (
        gb_fatalities["road_deaths"]
        / (gb_fatalities["population_millions"] * 1_000_000)
        * 100_000
    )

    gb_fatalities.insert(0, "country", "Great Britain")

    # Save cleaned data
    gb_clean_file = gb_source_file.parent / "great_britain_fatalities_2000_2025.csv"

    gb_fatalities.to_csv(gb_clean_file, index=False)

    print("Records:", len(gb_fatalities))
    print("Period:", gb_fatalities["year"].min(), "-", gb_fatalities["year"].max())
    print("\nFirst five years:")
    print(gb_fatalities.head().to_string(index=False))
    print("\nLast five years:")
    print(gb_fatalities.tail().to_string(index=False))
    print("\nSaved:", gb_clean_file)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.4 Switzerland Fatality Data Acquisition

    Identify official Swiss road traffic fatality statistics for the period 2000–2025.
    """)
    return


@app.cell
def _():
    swiss_fatalities_source = (
        "https://www.pxweb.bfs.admin.ch/pxweb/de/"
        "px-x-1106010100_104/px-x-1106010100_104/"
        "px-x-1106010100_104.px/"
    )

    print("Source: Swiss Federal Statistical Office (FSO)")
    print("Dataset: Road traffic casualties")
    print("Coverage: 1992–2025")
    print("Dataset URL:", swiss_fatalities_source)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.5 Switzerland Data Source Exploration

    Identify the official Swiss Federal Statistical Office (FSO) dataset and its API endpoint for retrieving road traffic fatality statistics.
    """)
    return


@app.cell
def _(BeautifulSoup, requests, urljoin):


    swiss_source_page = "https://statistik.admin.ch/de/asset/36507076"

    swiss_page_response = requests.get(
        swiss_source_page,
        timeout=60
    )
    swiss_page_response.raise_for_status()

    swiss_soup = BeautifulSoup(
        swiss_page_response.text,
        "html.parser"
    )

    print("Available Swiss dataset links:\n")

    for swiss_link in swiss_soup.find_all("a", href=True):
        swiss_title = swiss_link.get_text(" ", strip=True)
        swiss_url = urljoin(
            swiss_source_page,
            swiss_link["href"]
        )

        if (
            ".px" in swiss_url.lower()
            or ".csv" in swiss_url.lower()
            or ".xlsx" in swiss_url.lower()
            or "download" in swiss_title.lower()
        ):
            print("Title:", swiss_title)
            print("URL:", swiss_url)
            print("-" * 50)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.6 Switzerland API Data Exploration

    Inspect the available API variables to identify annual road traffic fatality records for 2000–2025.
    """)
    return


@app.cell
def _(requests):


    swiss_api_url = (
        "https://www.pxweb.bfs.admin.ch/api/v1/de/"
        "px-x-1106010100_104/px-x-1106010100_104.px"
    )

    swiss_metadata_response = requests.get(
        swiss_api_url,
        timeout=60
    )
    swiss_metadata_response.raise_for_status()

    swiss_metadata = swiss_metadata_response.json()

    print("Dataset:", swiss_metadata.get("title", "Swiss road traffic statistics"))
    print("\nAvailable variables:\n")

    for variable in swiss_metadata["variables"]:
        print("Variable:", variable["text"])
        print("Code:", variable["code"])
        print("Values:", variable["values"][:15])
        print("Labels:", variable["valueTexts"][:15])
        print("-" * 60)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.7 Switzerland Fatality Data Download

    Retrieve annual road traffic deaths from the Swiss Federal Statistical Office (FSO) API for 2000–2025.
    """)
    return


@app.cell
def _(Path, requests):
    import time

    ch_api = (
        "https://www.pxweb.bfs.admin.ch/api/v1/de/"
        "px-x-1106010100_104/px-x-1106010100_104.px"
    )

    ch_folder = (
        Path.home()
        / "Documents"
        / "CIP_HS2026_Group_108"
        / "Data"
        / "Fatalities"
    )
    ch_folder.mkdir(parents=True, exist_ok=True)

    # Read metadata
    ch_meta_response = requests.get(ch_api, timeout=60)
    ch_meta_response.raise_for_status()
    ch_variables = ch_meta_response.json()["variables"]

    # Map calendar years to API codes
    ch_year_variable = next(
        v for v in ch_variables if v["code"] == "Jahr"
    )

    ch_year_codes = {
        int(label): code
        for code, label in zip(
            ch_year_variable["values"],
            ch_year_variable["valueTexts"]
        )
        if label.isdigit()
    }

    ch_downloaded = []
    ch_failed = []

    for ch_year in range(2000, 2026):
        ch_file = ch_folder / f"switzerland_fatalities_{ch_year}.csv"

        if ch_file.exists() and ch_file.stat().st_size > 0:
            print(f"{ch_year}: Already downloaded")
            ch_downloaded.append(ch_year)
            continue

        ch_query = []

        for ch_variable in ch_variables:
            if ch_variable["code"] == "Unfallfolge":
                ch_values = ["974"]
            elif ch_variable["code"] == "Jahr":
                ch_values = [ch_year_codes[ch_year]]
            else:
                ch_values = ch_variable["values"]

            ch_query.append({
                "code": ch_variable["code"],
                "selection": {
                    "filter": "item",
                    "values": ch_values
                }
            })

        ch_payload = {
            "query": ch_query,
            "response": {"format": "csv"}
        }

        try:
            ch_response = requests.post(
                ch_api,
                json=ch_payload,
                timeout=120
            )
            ch_response.raise_for_status()

            ch_file.write_bytes(ch_response.content)
            ch_downloaded.append(ch_year)

            print(f"{ch_year}: Downloaded")

        except requests.RequestException as ch_error:
            ch_failed.append(ch_year)
            print(f"{ch_year}: Failed - {ch_error}")

            if (
                ch_response.status_code in (403, 429)
                if "ch_response" in locals()
                else False
            ):
                print("API restriction detected. Stopping.")
                break

        time.sleep(2)

    print("\nDownloaded years:", len(ch_downloaded))
    print("Failed years:", ch_failed)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.8 Switzerland Fatality Data Extraction

    Aggregate detailed road traffic fatality records into annual national totals for Switzerland from 2000 to 2025.
    """)
    return


@app.cell
def _(Path, pd):



    def extract_swiss_fatalities():
        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Fatalities"
        )

        annual_records = []
        missing_years = []

        for year in range(2000, 2026):
            csv_path = data_folder / f"switzerland_fatalities_{year}.csv"

            if not csv_path.exists():
                missing_years.append(year)
                continue

            # Read the Swiss API CSV
            df = pd.read_csv(
                csv_path,
                sep=None,
                engine="python",
                encoding="cp1252"
            )

            # The last column contains the annual fatality counts
            values = pd.to_numeric(
                df.iloc[:, -1],
                errors="coerce"
            )

            annual_records.append({
                "country": "Switzerland",
                "year": year,
                "road_deaths": int(values.sum())
            })

        fatalities = pd.DataFrame(annual_records)

        if missing_years:
            print("Missing years:", missing_years)

        if fatalities.empty:
            print("No Swiss fatality files found.")
            return None

        # Save the annual totals
        output_file = data_folder / "switzerland_fatalities_2000_2025.csv"
        fatalities.to_csv(output_file, index=False)

        print("Records:", len(fatalities))
        print("\nFirst five years:")
        print(fatalities.head().to_string(index=False))
        print("\nLast five years:")
        print(fatalities.tail().to_string(index=False))
        print("\nSaved:", output_file)

        return fatalities


    swiss_annual_fatalities = extract_swiss_fatalities()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.9 Switzerland Population Data Acquisition

    Retrieve annual population statistics for Switzerland to calculate comparable road fatality rates per 100,000 inhabitants.
    """)
    return


@app.cell
def _(requests):


    ch_population_api = (
        "https://www.pxweb.bfs.admin.ch/api/v1/en/"
        "px-x-0102030000_101/px-x-0102030000_101.px"
    )

    ch_population_response = requests.get(
        ch_population_api,
        timeout=60
    )
    ch_population_response.raise_for_status()

    ch_population_metadata = ch_population_response.json()

    print("Dataset:", ch_population_metadata.get("title"))

    for pop_variable in ch_population_metadata["variables"]:
        print("\nVariable:", pop_variable["text"])
        print("Code:", pop_variable["code"])
        print("Values:", pop_variable["values"][:10])
        print("Labels:", pop_variable["valueTexts"][:10])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.10 Switzerland Population Download

    Download the annual total permanent resident population of Switzerland for 2000–2025.
    """)
    return


@app.cell
def _(Path, pd, requests):
    import io

    def download_swiss_population():
        api_url = (
            "https://www.pxweb.bfs.admin.ch/api/v1/en/"
            "px-x-0102030000_101/px-x-0102030000_101.px"
        )

        metadata = requests.get(api_url, timeout=60).json()

        year_variable = next(
            variable for variable in metadata["variables"]
            if variable["code"] == "Jahr"
        )

        year_codes = [
            code
            for code, label in zip(
                year_variable["values"],
                year_variable["valueTexts"]
            )
            if label.isdigit() and 2000 <= int(label) <= 2025
        ]

        payload = {
            "query": [
                {
                    "code": "Jahr",
                    "selection": {
                        "filter": "item",
                        "values": year_codes
                    }
                },
                {
                    "code": "Geschlecht",
                    "selection": {
                        "filter": "item",
                        "values": ["0"]
                    }
                },
                {
                    "code": "Alter",
                    "selection": {
                        "filter": "item",
                        "values": ["0"]
                    }
                }
            ],
            "response": {
                "format": "csv"
            }
        }

        response = requests.post(
            api_url,
            json=payload,
            timeout=120
        )
        response.raise_for_status()

        population_df = pd.read_csv(
            io.BytesIO(response.content),
            sep=None,
            engine="python",
            encoding="cp1252"
        )

        print("Downloaded population data:")
        print(population_df.to_string(index=False))

        output_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Fatalities"
        )

        output_folder.mkdir(parents=True, exist_ok=True)

        output_file = output_folder / "switzerland_population_raw.csv"
        population_df.to_csv(output_file, index=False)

        print("\nSaved:", output_file)

        return population_df


    swiss_population_raw = download_swiss_population()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.11 Switzerland Fatality Rate Calculation

    Combine annual road fatalities and population data to calculate road traffic deaths per 100,000 inhabitants in Switzerland from 2000 to 2025.
    """)
    return


@app.cell
def _(Path, pd):


    def calculate_swiss_fatality_rates():
        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Fatalities"
        )

        fatalities = pd.read_csv(
            data_folder / "switzerland_fatalities_2000_2025.csv"
        )

        population = pd.read_csv(
            data_folder / "switzerland_population_raw.csv"
        )

        print("Population columns:", population.columns.tolist())
        print("\nFirst population records:")
        print(population.head().to_string(index=False))

        # Identify the year and population columns
        year_column = population.columns[0]
        value_column = population.columns[-1]

        population_clean = pd.DataFrame({
            "year": pd.to_numeric(population[year_column], errors="coerce"),
            "population": pd.to_numeric(
                population[value_column]
                    .astype(str)
                    .str.replace(" ", "", regex=False)
                    .str.replace(",", "", regex=False),
                errors="coerce"
            )
        })

        combined = fatalities.merge(
            population_clean,
            on="year",
            how="left",
            validate="one_to_one"
        )

        if combined["population"].isna().any():
            raise ValueError("Missing population values. Check the downloaded CSV.")

        if (combined["population"] <= 0).any():
            raise ValueError("Population values must be positive.")

        combined["fatalities_per_100k"] = (
            combined["road_deaths"] / combined["population"] * 100000
        )

        output_file = data_folder / "switzerland_fatality_rates_2000_2025.csv"
        combined.to_csv(output_file, index=False)

        print("\nSwitzerland fatality rates:")
        print(combined.to_string(index=False))
        print("\nSaved:", output_file)

        return combined


    swiss_fatality_rates = calculate_swiss_fatality_rates()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.12 Great Britain and Switzerland Data Integration

    Combine the annual road traffic fatality rates for Great Britain and Switzerland into one dataset for comparative analysis.
    """)
    return


@app.cell
def _(Path, pd):


    def combine_country_fatality_data():
        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Fatalities"
        )

        gb = pd.read_csv(
            data_folder / "great_britain_fatalities_2000_2025.csv"
        )

        ch = pd.read_csv(
            data_folder / "switzerland_fatality_rates_2000_2025.csv"
        )

        print("Great Britain columns:", gb.columns.tolist())
        print("Switzerland columns:", ch.columns.tolist())

        return gb, ch


    gb_comparison_source, ch_comparison_source = combine_country_fatality_data()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4.13 Final Fatality Comparison Dataset

    Standardize and combine annual road traffic fatalities, population figures and fatality rates for Great Britain and Switzerland from 2000 to 2025.
    """)
    return


@app.cell
def _():
    def create_final_fatality_dataset():
        from pathlib import Path
        import pandas as pd

        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Fatalities"
        )

        gb = pd.read_csv(
            data_folder / "great_britain_fatalities_2000_2025.csv"
        )

        ch = pd.read_csv(
            data_folder / "switzerland_fatality_rates_2000_2025.csv"
        )

        # Convert Great Britain population from millions to inhabitants
        gb["population"] = gb["population_millions"] * 1_000_000

        # Standardize both datasets
        columns = ["country", "year", "road_deaths", "population"]

        gb = gb[columns]
        ch = ch[columns]

        # Combine and calculate comparable fatality rates
        combined = pd.concat([gb, ch], ignore_index=True)

        combined["fatalities_per_100k"] = (
            combined["road_deaths"] / combined["population"] * 100_000
        )

        combined = combined.sort_values(
            ["year", "country"]
        ).reset_index(drop=True)

        # Validate completeness
        if len(combined) != 52:
            raise ValueError("Expected 52 records: 26 years × 2 countries.")

        if combined[["road_deaths", "population"]].isna().any().any():
            raise ValueError("Missing fatality or population values.")

        # Save final dataset
        output_file = data_folder / "gb_switzerland_fatality_comparison_2000_2025.csv"

        combined.to_csv(output_file, index=False)

        print("Total records:", len(combined))
        print("\nFirst records:")
        print(combined.head(6).to_string(index=False))

        print("\nLast records:")
        print(combined.tail(6).to_string(index=False))

        print("\nSaved:", output_file)

        return combined


    final_fatality_comparison = create_final_fatality_dataset()
    return


if __name__ == "__main__":
    app.run()
