import marimo

__generated_with = "0.25.2"
app = marimo.App(auto_download=["html"])


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 02 — Road Collision Data Acquisition

    **Source:** UK Department for Transport (STATS19)
    **Period:** 2000–2025

    Acquire and inspect reported road collision records.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.1 Data Source Exploration

    Identify the official collision data files and their download links.
    """)
    return


@app.cell
def _():

    import requests
    import marimo as mo
    import pandas as pd
    from pathlib import Path


    from html.parser import HTMLParser
    from urllib.parse import urljoin

    class CollisionLinkParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []
            self.href = None

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                self.href = dict(attrs).get("href")

        def handle_data(self, data):
            if self.href and "Collisions" in data:
                self.links.append((data.strip(), self.href))

        def handle_endtag(self, tag):
            if tag == "a":
                self.href = None


    def find_collision_downloads():
        page_url = (
            "https://www.gov.uk/government/"
            "statistical-data-sets/road-safety-open-data"
        )

        response = requests.get(page_url, timeout=30)
        response.raise_for_status()

        parser = CollisionLinkParser()
        parser.feed(response.text)

        for title, href in parser.links:
            print(title)
            print(urljoin(page_url, href))
            print("-" * 50)

        return parser.links


    collision_download_links = find_collision_downloads()

    return Path, collision_download_links, mo, requests, urljoin


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.2 Download File Inspection

    Check the historical collision dataset's download URL, format and file size.
    """)
    return


@app.cell
def _(requests):

    def inspect_collision_download(download_url):
        headers = {
            "Range": "bytes=0-1023"
        }

        try:
            with requests.get(
                download_url,
                headers=headers,
                stream=True,
                timeout=30
            ) as file_response:

                print("HTTP status:", file_response.status_code)
                print("Content type:", file_response.headers.get("Content-Type"))
                print("Content length:", file_response.headers.get("Content-Length"))
                print("Content range:", file_response.headers.get("Content-Range"))
                print("Accept ranges:", file_response.headers.get("Accept-Ranges"))

                if file_response.status_code == 206:
                    print("Partial download supported.")
                elif file_response.status_code == 200:
                    print("Server returned 200; partial download not confirmed.")

                file_response.raise_for_status()

        except requests.RequestException as error:
            print("Inspection failed:", str(error))


    inspect_collision_download(
        "https://data.dft.gov.uk/road-accidents-safety-data/dft-road-casualty-statistics-collision-1979-latest-published-year.csv"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.3 Annual Collision Files

    Identify available annual CSV files to avoid downloading the complete historical dataset.
    """)
    return


@app.cell
def _(collision_download_links, urljoin):

    def list_collision_files():
        annual_files = {}

        for title, href in collision_download_links:
            title_lower = title.lower()

            if "collisions" not in title_lower:
                continue

            # Identify single-year files
            for year in range(2000, 2026):
                if title.strip().endswith(str(year)):
                    annual_files[year] = urljoin(
                        "https://www.gov.uk", href
                    )
                    break

        print("Available annual collision files:\n")

        for year, file_url in sorted(annual_files.items()):
            print(f"{year}: {file_url}")

        missing_years = [
            year for year in range(2000, 2026)
            if year not in annual_files
        ]

        print("\nAnnual files found:", len(annual_files))
        print("Years without individual links:", missing_years)

        return annual_files


    collision_annual_files = list_collision_files()
    return (collision_annual_files,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.4 Annual Collision Data Collection

    Download the available annual collision CSV files (2021–2025).
    """)
    return


@app.cell
def _(Path, collision_annual_files, requests):



    def download_annual_collisions():
        output_dir = Path.home() / "Documents" / "CIP_HS2026_Group_108" / "Data" / "Collisions"
        output_dir.mkdir(parents=True, exist_ok=True)

        for year, file_url in sorted(collision_annual_files.items()):
            output_file = output_dir / f"collisions_{year}.csv"

            if output_file.exists() and output_file.stat().st_size > 0:
                print(f"{year}: Already downloaded")
                continue

            print(f"Downloading {year}...")

            try:
                with requests.get(
                    file_url,
                    stream=True,
                    timeout=120
                ) as response:
                    response.raise_for_status()

                    with output_file.open("wb") as file:
                        for chunk in response.iter_content(
                            chunk_size=1024 * 1024
                        ):
                            if chunk:
                                file.write(chunk)

                print(
                    f"{year}: Saved "
                    f"{output_file.stat().st_size / 1024**2:.1f} MB"
                )

            except Exception as error:
                output_file.unlink(missing_ok=True)
                print(f"{year}: Failed - {error}")


    download_annual_collisions()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.5 Historical Collision Data (2000–2020)

    Retrieve the historical STATS19 dataset and extract the required years using chunk processing.
    """)
    return


@app.cell
def _(Path, requests):

    import csv
    from contextlib import ExitStack

    def extract_historical_collisions():
        source_url = (
            "https://data.dft.gov.uk/road-accidents-safety-data/"
            "dft-road-casualty-statistics-collision-1979-latest-published-year.csv"
        )

        output_dir = Path.home() / "Documents" / "CIP_HS2026_Group_108" / "Data" / "Collisions"
        output_dir.mkdir(parents=True, exist_ok=True)

        years = range(2000, 2021)
        counts = {year: 0 for year in years}
        temp_paths = {}

        try:
            with ExitStack() as stack:
                response = stack.enter_context(
                    requests.get(
                        source_url,
                        stream=True,
                        timeout=(30, 180)
                    )
                )
                response.raise_for_status()

                # Decode lines without wrapping response.raw
                lines = (
                    line.decode("utf-8-sig")
                    for line in response.iter_lines()
                )

                reader = csv.DictReader(lines)

                if not reader.fieldnames:
                    raise ValueError("CSV header not found")

                writers = {}

                for year in years:
                    temp_path = output_dir / f"collisions_{year}.part"
                    temp_paths[year] = temp_path

                    output_file = stack.enter_context(
                        temp_path.open(
                            "w", newline="", encoding="utf-8"
                        )
                    )

                    writer = csv.DictWriter(
                        output_file,
                        fieldnames=reader.fieldnames
                    )
                    writer.writeheader()
                    writers[year] = writer

                for record in reader:
                    year_text = record.get("collision_year", "")

                    if year_text.isdigit():
                        year = int(year_text)

                        if year in writers:
                            writers[year].writerow(record)
                            counts[year] += 1

            # Finalize files only after successful extraction
            for year, temp_path in temp_paths.items():
                final_path = output_dir / f"collisions_{year}.csv"
                temp_path.replace(final_path)

            print("\nHistorical extraction completed.")

            for year, count in counts.items():
                print(f"{year}: {count:,} records")

            print("Total:", f"{sum(counts.values()):,}")

            return counts

        except Exception as error:
            for temp_path in temp_paths.values():
                temp_path.unlink(missing_ok=True)
            raise


    historical_collision_counts = extract_historical_collisions()
    return (csv,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 2.6 Collision Data Verification

    Verify the downloaded collision files, record counts and year consistency.
    """)
    return


@app.cell
def _(Path, csv):



    def verify_collision_data():
        folder = Path.home() / "Documents" / "CIP_HS2026_Group_108" / "Data" / "Collisions"

        total_records = 0
        verified_years = 0
        issues = []

        for year in range(2000, 2026):
            file_path = folder / f"collisions_{year}.csv"

            if not file_path.exists():
                issues.append(f"{year}: Missing file")
                print(f"{year}: MISSING")
                continue

            record_count = 0
            incorrect_years = 0

            with file_path.open(
                "r", encoding="utf-8-sig", newline=""
            ) as file:
                reader = csv.DictReader(file)

                if "collision_year" not in (reader.fieldnames or []):
                    issues.append(f"{year}: Missing collision_year column")
                    continue

                for record in reader:
                    record_count += 1

                    if str(record.get("collision_year", "")).strip() != str(year):
                        incorrect_years += 1

            if record_count == 0 or incorrect_years > 0:
                issues.append(
                    f"{year}: {record_count} rows, "
                    f"{incorrect_years} incorrect years"
                )
                status = "CHECK"
            else:
                verified_years += 1
                status = "OK"

            total_records += record_count

            print(f"{year}: {record_count:,} collisions | {status}")

        print("\n--- Verification Summary ---")
        print("Years verified:", f"{verified_years}/26")
        print("Total collision records:", f"{total_records:,}")
        print("Issues found:", len(issues))

        if issues:
            print("\nIssues:")
            for issue in issues:
                print("-", issue)

        return {
            "verified_years": verified_years,
            "total_records": total_records,
            "issues": issues
        }


    collision_verification = verify_collision_data()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2.7 Collision Data Integration

    Combine annual road collision records from 2000 to 2025 into one dataset for further analysis.
    """)
    return


@app.cell
def _():
    def merge_collision_data():
        from pathlib import Path
        import pandas as pd

        collision_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Collisions"
        )

        collision_files = sorted(
            collision_folder.glob("collisions_????.csv")
        )

        if len(collision_files) != 26:
            raise ValueError(
                f"Expected 26 collision files, found {len(collision_files)}."
            )

        output_file = (
            collision_folder / "collisions_2000_2025_combined.csv"
        )

        total_records = 0

        # Write in chunks to avoid loading millions of rows into memory
        with open(output_file, "w", encoding="utf-8", newline="") as output:

            first_chunk = True

            for file in collision_files:
                file_records = 0

                for chunk in pd.read_csv(
                    file,
                    chunksize=50_000,
                    low_memory=False
                ):
                    chunk.to_csv(
                        output,
                        index=False,
                        header=first_chunk
                    )

                    first_chunk = False
                    file_records += len(chunk)

                total_records += file_records
                print(f"{file.stem}: {file_records:,} records")

        print("\nAnnual files:", len(collision_files))
        print("Total collision records:", f"{total_records:,}")
        print("Saved:", output_file)

        return output_file


    collision_combined_file = merge_collision_data()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2.8 Collision Data Structure Validation

    Check whether annual collision datasets use consistent column names before performing analysis.
    """)
    return


@app.cell
def _():
    def validate_collision_columns():
        from pathlib import Path
        import pandas as pd

        folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Collisions"
        )

        files = sorted(folder.glob("collisions_????.csv"))

        reference_columns = None
        differences = []

        for file in files:
            columns = pd.read_csv(file, nrows=0).columns.tolist()

            if reference_columns is None:
                reference_columns = columns

            if columns != reference_columns:
                differences.append({
                    "year": file.stem[-4:],
                    "column_count": len(columns),
                    "missing_columns": sorted(set(reference_columns) - set(columns)),
                    "extra_columns": sorted(set(columns) - set(reference_columns)),
                    "different_order": set(columns) == set(reference_columns)
                })

        print("Files checked:", len(files))
        print("Reference column count:", len(reference_columns))

        if differences:
            print("\nColumn differences found:")
            for difference in differences:
                print(difference)
        else:
            print("All annual collision files have identical columns and order.")


    validate_collision_columns()
    return


if __name__ == "__main__":
    app.run()
