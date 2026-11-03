import marimo

__generated_with = "0.25.2"
app = marimo.App(width="full", auto_download=["html"])


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.1 API Exploration

    Test the API response, query parameters and JSON structure before retrieving the full dataset.
    """)
    return


@app.cell
def _():
    import marimo as mo

    import requests

    url = "https://roadtraffic.dft.gov.uk/api/average-annual-daily-flow"

    # Request a small sample
    params = {
        "filter[year]": 2000,
        "page[size]": 5
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    traffic_data = response.json()

    # Inspect the HTTP response
    print("Status code:", response.status_code)
    print("Request URL:", response.url)
    print("Content type:", response.headers.get("Content-Type"))

    # Inspect JSON structure
    print("\nJSON keys:", list(traffic_data.keys()))
    print("Total records:", traffic_data.get("total"))
    print("Records returned:", len(traffic_data.get("data", [])))

    # Inspect first record
    if traffic_data.get("data"):
        print("\nFirst record:")
        print(traffic_data["data"][0])
    return mo, requests, url


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.2 Query Parameters and Pagination

    Compare API responses across different years, page sizes and page numbers.
    """)
    return


@app.cell
def _(requests, url):

    # Test different API query parameters
    test_requests = [
        {"filter[year]": 2000, "page[size]": 5},
        {"filter[year]": 2010, "page[size]": 5},
        {"filter[year]": 2020, "page[size]": 5},
        {"filter[year]": 2020, "page[size]": 10},
        {"filter[year]": 2020, "page[size]": 5, "page[number]": 2}
    ]

    for params_test in test_requests:
        try:
            test_response = requests.get(
                url,
                params=params_test,
                timeout=30
            )
            test_response.raise_for_status()

            result = test_response.json()

            print("Parameters:", params_test)
            print("Status:", test_response.status_code)
            print("Total records:", result.get("total"))
            print("Returned records:", len(result.get("data", [])))
            print("Current page:", result.get("current_page"))
            print("-" * 50)

        except requests.RequestException as error:
            print("Request failed:", error)
            print("-" * 50)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.3 Reusable API Function

    Create a function to retrieve traffic data with error handling and pagination support.
    """)
    return


@app.cell
def _(requests, url):

    def fetch_traffic_page(year, page=1, page_size=100):
        """Retrieve one page of annual traffic data."""

        params = {
            "filter[year]": year,
            "page[number]": page,
            "page[size]": page_size
        }

        try:
            api_response = requests.get(
                url,
                params=params,
                timeout=30
            )
            api_response.raise_for_status()

            result = api_response.json()

            if not isinstance(result, dict):
                raise ValueError("Unexpected API response format")

            records = result.get("data", [])

            if not isinstance(records, list):
                raise ValueError("Expected a list of records")

            return result

        except (requests.RequestException, ValueError) as error:
            print(f"Request failed for year {year}, page {page}: {error}")
            return None


    # Test the function
    test_result = fetch_traffic_page(
        year=2020,
        page=1,
        page_size=10
    )

    if test_result is not None:
        print("Total records:", test_result.get("total"))
        print("Current page:", test_result.get("current_page"))
        print("Records returned:", len(test_result["data"]))
    return (fetch_traffic_page,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.4 Automatic Pagination

    Retrieve multiple API pages automatically and combine their records into a single list.
    """)
    return


@app.cell
def _(fetch_traffic_page):

    def fetch_traffic_year(year, page_size=100, max_pages=None):
        """Retrieve traffic records for a year across multiple pages."""

        all_records = []
        page = 1

        while True:
            result = fetch_traffic_page(
                year=year,
                page=page,
                page_size=page_size
            )

            # Stop if the request failed
            if result is None:
                raise RuntimeError(
                    f"Data retrieval failed for year {year}, page {page}"
                )

            records = result["data"]

            # Stop when no more records are available
            if not records:
                break

            all_records.extend(records)

            print(
                f"Year {year} | Page {page} | "
                f"Retrieved {len(records)} records"
            )

            # Stop after the requested number of pages
            if max_pages is not None and page >= max_pages:
                break

            # Stop when the final page is reached
            last_page = result.get("last_page")

            if last_page is not None and page >= int(last_page):
                break

            if len(records) < page_size:
                break

            page += 1

        print(f"\nTotal records collected: {len(all_records)}")

        return all_records


    # Test automatic pagination
    traffic_2020_sample = fetch_traffic_year(
        year=2020,
        page_size=100,
        max_pages=3
    )

    print("Sample size:", len(traffic_2020_sample))
    return fetch_traffic_year, traffic_2020_sample


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.5 Data Validation

    Inspect the retrieved records for missing values, duplicate entries and year consistency.
    """)
    return


@app.cell
def _(traffic_2020_sample):

    # Check the records collected from the API
    print("Total records:", len(traffic_2020_sample))

    if traffic_2020_sample:

        # Inspect available fields
        first_record = traffic_2020_sample[0]

        print("\nAvailable fields:")
        print(list(first_record.keys()))

        # Check for exact duplicate records
        import json

        record_strings = [
            json.dumps(record, sort_keys=True)
            for record in traffic_2020_sample
        ]

        duplicates = len(record_strings) - len(set(record_strings))

        print("\nExact duplicate records:", duplicates)

        # Inspect the year field, if present
        year_fields = [
            key for key in first_record
            if "year" in key.lower()
        ]

        print("\nPossible year fields:", year_fields)

        for field in year_fields:
            values = {
                str(record.get(field))
                for record in traffic_2020_sample
            }
            print(f"{field}: {sorted(values)}")

        # Check missing values in each field
        missing_counts = {
            field: sum(
                record.get(field) is None
                for record in traffic_2020_sample
            )
            for field in first_record
        }

        print("\nMissing values:")
        for field, count in missing_counts.items():
            if count > 0:
                print(f"{field}: {count}")

    else:
        print("No records available for validation.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.6 Multi-Year Data Retrieval

    Retrieve traffic records for selected years to test automated data collection.
    """)
    return


@app.cell
def _(fetch_traffic_year):

    def test_multi_year_acquisition():
        test_years = [2000, 2010, 2020]
        all_records = []

        for selected_year in test_years:
            print(f"\nRetrieving traffic data for {selected_year}")

            yearly_records = fetch_traffic_year(
                year=selected_year,
                page_size=100,
                max_pages=2
            )

            all_records.extend(yearly_records)

        print("\n--- Acquisition Summary ---")
        print("Total records:", len(all_records))

        for selected_year in test_years:
            year_count = sum(
                str(record.get("year")) == str(selected_year)
                for record in all_records
            )
            print(f"Year {selected_year}: {year_count} records")

        return all_records


    traffic_multi_year = test_multi_year_acquisition()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.7 Dataset Size Assessment

    Check the number of available traffic records per year before downloading the complete dataset.
    """)
    return


@app.cell
def _(fetch_traffic_page):

    def assess_traffic_dataset():
        years = range(2000, 2026)
        yearly_counts = {}

        for selected_year in years:
            result = fetch_traffic_page(
                year=selected_year,
                page=1,
                page_size=1
            )

            if result is not None:
                total_records = result.get("total", 0)
                yearly_counts[selected_year] = total_records

                print(f"{selected_year}: {total_records:,} records")
            else:
                yearly_counts[selected_year] = None
                print(f"{selected_year}: Request failed")

        available_counts = [
            value for value in yearly_counts.values()
            if isinstance(value, int)
        ]

        print("\n--- Dataset Summary ---")
        print("Years checked:", len(yearly_counts))
        print("Total available records:", f"{sum(available_counts):,}")

        return yearly_counts


    traffic_yearly_counts = assess_traffic_dataset()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 1.8 Traffic Data Collection

    Retrieve traffic data for 2000–2025 using API pagination and save each year as a CSV file.
    """)
    return


@app.cell
def _(fetch_traffic_page):

    import csv
    from pathlib import Path

    def collect_traffic_data(start_year=2000, end_year=2025):
        output_dir = Path.home() / "Documents" / "CIP_HS2026_Group_108" / "Data" / "Traffic"
        output_dir.mkdir(parents=True, exist_ok=True)

        summary = {}

        for selected_year in range(start_year, end_year + 1):
            output_file = output_dir / f"traffic_{selected_year}.csv"
            page_number = 1
            records_saved = 0

            # Skip years already downloaded
            if output_file.exists():
                print(f"{selected_year}: File already exists, skipped")
                continue

            try:
                with output_file.open("w", newline="", encoding="utf-8") as file:
                    writer = None

                    while True:
                        result = fetch_traffic_page(
                            year=selected_year,
                            page=page_number,
                            page_size=250
                        )

                        if result is None:
                            raise RuntimeError(
                                f"API failed on page {page_number}"
                            )

                        records = result["data"]

                        if not records:
                            break

                        if writer is None:
                            writer = csv.DictWriter(
                                file,
                                fieldnames=list(records[0].keys()),
                                extrasaction="ignore"
                            )
                            writer.writeheader()

                        writer.writerows(records)
                        records_saved += len(records)

                        last_page = result.get("last_page")

                        if last_page is not None:
                            if page_number >= int(last_page):
                                break
                        elif len(records) < 250:
                            break

                        page_number += 1

                summary[selected_year] = records_saved
                print(f"{selected_year}: Saved {records_saved:,} records")

            except Exception as error:
                # Remove incomplete files
                output_file.unlink(missing_ok=True)
                print(f"{selected_year}: Failed - {error}")
                summary[selected_year] = None

        return summary


    # Start with one year to test file saving
    traffic_collection_summary = collect_traffic_data(
        start_year=2000,
        end_year=2025
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1.8 Traffic Data Integration

    Combine annual traffic volume records from 2000 to 2025 into one dataset for further analysis.
    """)
    return


@app.cell
def _():
    def merge_traffic_data():
        from pathlib import Path
        import pandas as pd

        traffic_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Traffic"
        )

        traffic_files = sorted(traffic_folder.glob("traffic_????.csv"))

        if len(traffic_files) != 26:
            raise ValueError(
                f"Expected 26 traffic files, found {len(traffic_files)}."
            )

        traffic_frames = []

        for file in traffic_files:
            df = pd.read_csv(file, low_memory=False)
            traffic_frames.append(df)

        combined_traffic = pd.concat(
            traffic_frames,
            ignore_index=True
        )

        output_file = traffic_folder / "traffic_2000_2025_combined.csv"

        combined_traffic.to_csv(output_file, index=False)

        print("Annual files:", len(traffic_files))
        print("Total traffic records:", len(combined_traffic))
        print("\nColumns:", combined_traffic.columns.tolist())
        print("\nFirst five records:")
        print(combined_traffic.head().to_string(index=False))
        print("\nSaved:", output_file)

        return combined_traffic


    traffic_data_combined = merge_traffic_data()
    return


if __name__ == "__main__":
    app.run()
