import marimo

__generated_with = "0.25.2"
app = marimo.App(auto_download=["html"])


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 03 — Historical Weather Data Acquisition

    **Source:** Open-Meteo Historical Weather API
    **Period:** 2000–2025

    Retrieve historical precipitation data for selected locations in Great Britain.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.1 API Exploration

    Test the historical weather API using hourly precipitation data for a selected location.
    """)
    return


@app.cell
def _():


    import requests
    import pandas as pd


    def explore_weather_api():
        url = "https://archive-api.open-meteo.com/v1/archive"

        params = {
            "latitude": 51.5074,
            "longitude": -0.1278,
            "start_date": "2020-01-01",
            "end_date": "2020-01-07",
            "hourly": "precipitation",
            "timezone": "GMT",
            "models": "era5"
        }

        response = requests.get(
            url,
            params=params,
            timeout=60
        )
        response.raise_for_status()

        data = response.json()

        print("HTTP status:", response.status_code)
        print("Request URL:", response.url)
        print("\nJSON keys:", list(data.keys()))

        print("\nLocation:")
        print("Latitude:", data.get("latitude"))
        print("Longitude:", data.get("longitude"))

        print("\nHourly variables:")
        print(list(data.get("hourly", {}).keys()))

        print("\nUnits:")
        print(data.get("hourly_units"))

        print("\nNumber of hourly observations:")
        print(len(data.get("hourly", {}).get("time", [])))

        return data


    weather_sample = explore_weather_api()
    return pd, requests, weather_sample


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.2 Weather Data Structure

    Convert the API response into a DataFrame and inspect the precipitation observations.
    """)
    return


@app.cell
def _(pd, weather_sample):



    def inspect_weather_data(weather_data):
        weather_df = pd.DataFrame(weather_data["hourly"])

        weather_df["time"] = pd.to_datetime(weather_df["time"])

        print("--- Weather Data Preview ---")
        print(weather_df.head(10).to_string(index=False))

        print("\n--- Dataset Information ---")
        print("Rows:", len(weather_df))
        print("Columns:", list(weather_df.columns))
        print("Missing values:")
        print(weather_df.isna().sum())

        print("\n--- Precipitation Statistics ---")
        print(weather_df["precipitation"].describe())

        return weather_df


    weather_preview = inspect_weather_data(weather_sample)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.3 Geographic Coverage Analysis

    Examine the geographic distribution of traffic monitoring locations to plan weather data collection.
    """)
    return


@app.cell
def _(pd):


    from pathlib import Path

    def examine_traffic_locations():
        traffic_folder = Path.home() / "Documents" / "CIP_HS2026_Group_108" / "Data" / "Traffic"

        files = sorted(traffic_folder.glob("*.csv"))

        locations = []

        for file in files:
            df = pd.read_csv(
                file,
                usecols=["latitude", "longitude"]
            )

            locations.append(df)

        traffic_coordinates = pd.concat(
            locations,
            ignore_index=True
        ).dropna()

        unique_coordinates = traffic_coordinates.drop_duplicates()

        print("--- Traffic Geographic Coverage ---")
        print("Files:", len(files))
        print("Total traffic records:", f"{len(traffic_coordinates):,}")
        print("Unique coordinates:", f"{len(unique_coordinates):,}")

        print("\nLatitude range:")
        print(unique_coordinates["latitude"].min())
        print(unique_coordinates["latitude"].max())

        print("\nLongitude range:")
        print(unique_coordinates["longitude"].min())
        print(unique_coordinates["longitude"].max())

        return unique_coordinates


    traffic_weather_coordinates = examine_traffic_locations()
    return Path, traffic_weather_coordinates


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.4 Weather Grid Resolution

    Compare geographic grid sizes to balance weather coverage and API download requirements.
    """)
    return


@app.cell
def _(pd, traffic_weather_coordinates):


    import numpy as np

    def compare_weather_grids(coordinates):
        results = []

        for grid_km in [10, 25, 50]:
            # Approximate conversion from kilometers to latitude degrees
            lat_step = grid_km / 111.0

            # Longitude degree width varies by latitude
            reference_lat = coordinates["latitude"].median()
            lon_step = grid_km / (
                111.0 * np.cos(np.radians(reference_lat))
            )

            grid_lat = (
                np.floor(coordinates["latitude"] / lat_step)
                * lat_step
            )

            grid_lon = (
                np.floor(coordinates["longitude"] / lon_step)
                * lon_step
            )

            grid_cells = pd.DataFrame({
                "grid_lat": grid_lat,
                "grid_lon": grid_lon
            }).drop_duplicates()

            results.append({
                "Grid size (km)": grid_km,
                "Weather locations": len(grid_cells),
                "Hourly observations per year": len(grid_cells) * 8760
            })

        result_df = pd.DataFrame(results)

        print("--- Weather Grid Comparison ---")
        print(result_df.to_string(index=False))

        return result_df


    weather_grid_comparison = compare_weather_grids(
        traffic_weather_coordinates
    )
    return compare_weather_grids, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.5 Combined Geographic Coverage

    Combine traffic and collision coordinates to evaluate weather coverage across the study area.
    """)
    return


@app.cell
def _(Path, compare_weather_grids, pd, traffic_weather_coordinates):



    def examine_combined_locations(traffic_coordinates):
        collision_folder = Path.home() / "Documents" / "CIP_HS2026_Group_108" / "Data" / "Collisions"

        collision_files = sorted(
            collision_folder.glob("collisions_*.csv")
        )

        collision_locations = []

        for file in collision_files:
            coordinates = pd.read_csv(
                file,
                usecols=["latitude", "longitude"]
            )
            collision_locations.append(coordinates)

        collision_coordinates = pd.concat(
            collision_locations,
            ignore_index=True
        ).dropna().drop_duplicates()

        combined_coordinates = pd.concat(
            [traffic_coordinates, collision_coordinates],
            ignore_index=True
        ).drop_duplicates()

        print("--- Combined Geographic Coverage ---")
        print("Collision files:", len(collision_files))
        print("Unique traffic coordinates:", f"{len(traffic_coordinates):,}")
        print("Unique collision coordinates:", f"{len(collision_coordinates):,}")
        print("Combined unique coordinates:", f"{len(combined_coordinates):,}")

        print("\n--- Grid Comparison ---")
        compare_weather_grids(combined_coordinates)

        return combined_coordinates


    combined_weather_coordinates = examine_combined_locations(
        traffic_weather_coordinates
    )
    return (combined_weather_coordinates,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.6 Weather Grid Generation

    Generate representative weather coordinates for geographic grid cells containing traffic and collision records.
    """)
    return


@app.cell
def _(combined_weather_coordinates, np, pd):



    def generate_weather_grid(coordinates, grid_km=50):
        reference_lat = coordinates["latitude"].median()

        lat_step = grid_km / 111.0
        lon_step = grid_km / (
            111.0 * np.cos(np.radians(reference_lat))
        )

        grid_data = pd.DataFrame({
            "grid_lat_index": np.floor(
                coordinates["latitude"] / lat_step
            ).astype(int),
            "grid_lon_index": np.floor(
                coordinates["longitude"] / lon_step
            ).astype(int)
        })

        grid_data = grid_data.drop_duplicates().reset_index(drop=True)

        grid_data["latitude"] = (
            grid_data["grid_lat_index"] + 0.5
        ) * lat_step

        grid_data["longitude"] = (
            grid_data["grid_lon_index"] + 0.5
        ) * lon_step

        grid_data["grid_id"] = [
            f"GRID_{i:03d}" for i in range(1, len(grid_data) + 1)
        ]

        grid_data = grid_data[
            ["grid_id", "latitude", "longitude",
             "grid_lat_index", "grid_lon_index"]
        ]

        print("--- Weather Grid ---")
        print("Grid resolution:", grid_km, "km")
        print("Weather locations:", len(grid_data))
        print("\nSample locations:")
        print(grid_data.head(10).to_string(index=False))

        return grid_data


    weather_grid = generate_weather_grid(
        combined_weather_coordinates,
        grid_km=50
    )
    return (weather_grid,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.7 Historical Weather Data Collection

    Collect daily precipitation, temperature, snowfall and wind speed data across Great Britain from 2000 to 2025.
    """)
    return


@app.cell
def _(Path, np, pd, requests, weather_grid):
    import time


    def collect_historical_weather(grid, n_locations=30):
        output_dir = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Weather"
            / "Daily"
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        # Select geographically distributed locations
        coordinates = grid[["latitude", "longitude"]].to_numpy(float)
        reference_lat = np.radians(grid["latitude"].median())

        positions = np.column_stack([
            coordinates[:, 0] * 111,
            coordinates[:, 1] * 111 * np.cos(reference_lat)
        ])

        selected = [int(np.argmax(coordinates[:, 0]))]
        minimum_distances = np.full(len(grid), np.inf)

        for _ in range(min(n_locations, len(grid)) - 1):
            distances = np.linalg.norm(
                positions - positions[selected[-1]],
                axis=1
            )
            minimum_distances = np.minimum(
                minimum_distances,
                distances
            )
            minimum_distances[selected] = -1
            selected.append(int(np.argmax(minimum_distances)))

        sample = grid.iloc[selected].copy()

        sample.to_csv(
            output_dir / "selected_weather_locations.csv",
            index=False
        )

        variables = [
            "precipitation_sum",
            "temperature_2m_mean",
            "snowfall_sum",
            "wind_speed_10m_max"
        ]

        expected_days = len(
            pd.date_range("2000-01-01", "2025-12-31")
        )

        downloaded = 0
        skipped = 0
        failed = []

        for index, (_, location) in enumerate(sample.iterrows(), 1):

            grid_id = location["grid_id"]
            file_path = output_dir / f"daily_weather_{grid_id}.csv"

            # Keep previously completed files
            if file_path.exists():
                try:
                    existing = pd.read_csv(file_path)

                    if (
                        len(existing) == expected_days
                        and set(variables).issubset(existing.columns)
                        and not existing[variables].isna().any().any()
                    ):
                        skipped += 1
                        print(f"[{index}/30] SKIPPED: {grid_id}")
                        continue

                except Exception:
                    pass

            params = {
                "latitude": float(location["latitude"]),
                "longitude": float(location["longitude"]),
                "start_date": "2000-01-01",
                "end_date": "2025-12-31",
                "daily": variables,
                "timezone": "GMT",
                "models": "era5"
            }

            success = False

            for attempt in range(1, 6):

                try:
                    response = requests.get(
                        "https://archive-api.open-meteo.com/v1/archive",
                        params=params,
                        timeout=180
                    )

                    # Handle API rate limiting
                    if response.status_code == 429:
                        retry_after = response.headers.get("Retry-After")

                        try:
                            wait_seconds = (
                                min(float(retry_after), 60)
                                if retry_after
                                else min(60 * attempt, 300)
                            )
                        except ValueError:
                            wait_seconds = min(60 * attempt, 300)

                        print(
                            f"[{index}/30] HTTP 429: "
                            f"waiting {wait_seconds:.0f} seconds "
                            f"before retry {attempt}/5"
                        )

                        if attempt < 5:
                            time.sleep(wait_seconds)

                        continue

                    if response.status_code == 403:
                        print(
                            f"[{index}/30] HTTP 403: "
                            "access denied; stopping requests"
                        )
                        failed.append(grid_id)
                        break

                    response.raise_for_status()

                    data = response.json()
                    daily_df = pd.DataFrame(data["daily"])

                    if len(daily_df) != expected_days:
                        raise ValueError(
                            f"Expected {expected_days} days, "
                            f"received {len(daily_df)}"
                        )

                    if not set(variables).issubset(daily_df.columns):
                        raise ValueError("Missing weather variables")

                    if daily_df[variables].isna().any().any():
                        raise ValueError("Missing weather observations")

                    daily_df.insert(0, "grid_id", grid_id)
                    daily_df["latitude"] = data["latitude"]
                    daily_df["longitude"] = data["longitude"]

                    # Save only when the file is complete
                    temp_path = file_path.with_suffix(".part")
                    daily_df.to_csv(temp_path, index=False)
                    temp_path.replace(file_path)

                    downloaded += 1
                    success = True

                    print(
                        f"[{index}/30] DOWNLOADED: "
                        f"{grid_id} ({len(daily_df):,} days)"
                    )
                    break

                except requests.RequestException as error:
                    print(
                        f"[{index}/30] Request attempt "
                        f"{attempt}/5 failed: {error}"
                    )
                    if attempt < 5:
                        time.sleep(15 * attempt)

                except (ValueError, KeyError) as error:
                    print(f"[{index}/30] Invalid data: {error}")
                    break

            if not success:
                if grid_id not in failed:
                    failed.append(grid_id)

            # Pause between API requests
            if success:
                time.sleep(20)

        print("\n--- Historical Weather Summary ---")
        print("Period: 2000–2025")
        print("Locations:", len(sample))
        print("Downloaded:", downloaded)
        print("Skipped:", skipped)
        print("Failed:", len(failed))
        print("Failed locations:", failed)

        return {
            "locations": len(sample),
            "downloaded": downloaded,
            "skipped": skipped,
            "failed": failed
        }


    historical_weather_result = collect_historical_weather(
        weather_grid,
        n_locations=30
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3.8 Weather Data Integration

    Combine daily weather observations from all 30 selected locations into one dataset covering Great Britain from 2000 to 2025.
    """)
    return


@app.cell
def _():
    def merge_weather_data():
        from pathlib import Path
        import pandas as pd

        weather_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Weather"
        )

        daily_folder = weather_folder / "Daily"

        weather_files = sorted(
            daily_folder.glob("daily_weather_GRID_*.csv")
        )

        if len(weather_files) != 30:
            raise ValueError(
                f"Expected 30 weather files, found {len(weather_files)}."
            )

        weather_frames = []

        for file in weather_files:
            df = pd.read_csv(file)

            # Add the grid identifier if it is not already present
            if "grid_id" not in df.columns:
                df["grid_id"] = file.stem.replace("daily_weather_", "")

            weather_frames.append(df)

        combined_weather = pd.concat(
            weather_frames,
            ignore_index=True
        )

        combined_weather["time"] = pd.to_datetime(
            combined_weather["time"]
        )

        # Check for duplicate observations
        duplicates = combined_weather.duplicated(
            subset=["grid_id", "time"]
        ).sum()

        if duplicates > 0:
            raise ValueError(
                f"Found {duplicates} duplicate grid/date records."
            )

        combined_weather = combined_weather.sort_values(
            ["grid_id", "time"]
        ).reset_index(drop=True)

        output_file = weather_folder / "weather_daily_2000_2025.csv"

        combined_weather.to_csv(output_file, index=False)

        print("Weather locations:", combined_weather["grid_id"].nunique())
        print("Total observations:", len(combined_weather))
        print("Date range:", combined_weather["time"].min().date(),
              "to", combined_weather["time"].max().date())

        print("\nFirst five records:")
        print(combined_weather.head().to_string(index=False))

        print("\nSaved:", output_file)

        return combined_weather


    weather_daily_combined = merge_weather_data()
    return


if __name__ == "__main__":
    app.run()
