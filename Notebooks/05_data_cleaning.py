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
    # 05 – Data Cleaning and Preparation

    This notebook examines the completeness, consistency and quality of the traffic, collision, weather and fatality datasets before analysis.
    """)
    return


@app.cell
def _():
    def load_project_datasets():
        from pathlib import Path
        import pandas as pd

        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
        )

        traffic = pd.read_csv(
            data_folder / "Traffic" / "traffic_2000_2025_combined.csv",
            low_memory=False
        )

        collisions = pd.read_csv(
            data_folder / "Collisions" / "collisions_2000_2025_combined.csv",
            low_memory=False
        )

        weather = pd.read_csv(
            data_folder / "Weather" / "weather_daily_2000_2025.csv"
        )

        fatalities = pd.read_csv(
            data_folder / "Fatalities"
            / "gb_switzerland_fatality_comparison_2000_2025.csv"
        )

        datasets = {
            "Traffic": traffic,
            "Collisions": collisions,
            "Weather": weather,
            "Fatalities": fatalities
        }

        for name, df in datasets.items():
            print(f"{name}: {len(df):,} rows, {len(df.columns)} columns")

        return datasets


    project_datasets = load_project_datasets()
    return (project_datasets,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.2 Data Quality Assessment

    Examine missing values, duplicate records and data types to identify potential data quality issues across the four datasets.
    """)
    return


@app.cell
def _(project_datasets):
    def assess_data_quality(datasets):
        import pandas as pd

        for name, df in datasets.items():
            print(f"\n{'=' * 55}")
            print(f"{name.upper()} DATASET")
            print(f"{'=' * 55}")

            print(f"Rows: {len(df):,}")
            print(f"Columns: {len(df.columns)}")

            missing = df.isna().sum()
            missing = missing[missing > 0].sort_values(ascending=False)

            print("\nMissing values:")
            if missing.empty:
                print("No missing values")
            else:
                print(
                    pd.DataFrame({
                        "Missing": missing,
                        "Percentage": (
                            missing / len(df) * 100
                        ).round(2)
                    }).to_string()
                )

            print("\nDuplicate rows:", f"{df.duplicated().sum():,}")

            print("\nData types:")
            print(df.dtypes.to_string())


    assess_data_quality(project_datasets)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.3 Data Cleaning and Standardization

    The data quality assessment identified missing values in the traffic and collision datasets. Rather than removing incomplete records, we evaluated whether the missing information affects our research questions.

    ### Traffic Data
    Approximately 23% of records have missing junction names or road lengths. Since traffic volume, year and geographical coordinates are complete, these missing values do not prevent our main analysis.

    **Decision:** Retain the records because removing or estimating missing values could reduce data coverage or introduce inaccuracies.

    ### Collision Data
    Approximately 22% of adjusted severity values and 0.07% of geographical coordinates are missing.

    **Decision:** Use the complete `collision_severity` column instead of adjusted severity. Records without coordinates will only be excluded from geographical analyses, as they remain useful for other analyses.

    ### Weather and Fatality Data
    Both datasets contain no missing values or duplicate records. Only data types and numerical consistency need to be checked.

    ### Cleaning Approach
    The cleaning process focuses on standardizing dates, validating key measurements and preserving valid records. Missing values are left unchanged unless they directly affect a specific analysis.
    """)
    return


@app.cell
def _(project_datasets):
    def clean_project_datasets(datasets):
        import pandas as pd

        traffic = datasets["Traffic"].copy()
        collisions = datasets["Collisions"].copy()
        weather = datasets["Weather"].copy()
        fatalities = datasets["Fatalities"].copy()

        # Traffic: validate key measurements
        traffic = traffic[
            traffic["year"].between(2000, 2025)
            & (traffic["all_motor_vehicles"] >= 0)
        ].copy()

        # Collisions: standardize dates and validate severity
        collisions["date"] = pd.to_datetime(
            collisions["date"],
            dayfirst=True,
            errors="coerce"
        )

        collisions = collisions[
            collisions["collision_year"].between(2000, 2025)
            & collisions["collision_severity"].isin([1, 2, 3])
        ].copy()

        # Weather: convert observation dates
        weather["time"] = pd.to_datetime(
            weather["time"],
            errors="coerce"
        )

        # Fatalities: validate population and deaths
        fatalities = fatalities[
            fatalities["year"].between(2000, 2025)
            & (fatalities["population"] > 0)
            & (fatalities["road_deaths"] >= 0)
        ].copy()

        cleaned = {
            "Traffic": traffic,
            "Collisions": collisions,
            "Weather": weather,
            "Fatalities": fatalities
        }

        print("Cleaning summary:\n")

        for name, df in cleaned.items():
            original = len(datasets[name])
            remaining = len(df)

            print(
                f"{name}: {remaining:,} records "
                f"({original - remaining:,} excluded)"
            )

        print("\nInvalid collision dates:",
              collisions["date"].isna().sum())

        print("Invalid weather dates:",
              weather["time"].isna().sum())

        return cleaned


    cleaned_project_datasets = clean_project_datasets(project_datasets)
    return (cleaned_project_datasets,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5.4 Save Cleaned Datasets

    Save the validated and standardized datasets in a separate `Cleaned` folder. The original datasets are preserved to ensure reproducibility and allow comparison with the source data.
    """)
    return


@app.cell
def _(cleaned_project_datasets):
    def save_cleaned_datasets(datasets):
        from pathlib import Path

        cleaned_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Cleaned"
        )

        cleaned_folder.mkdir(parents=True, exist_ok=True)

        filenames = {
            "Traffic": "traffic_cleaned.csv",
            "Collisions": "collisions_cleaned.csv",
            "Weather": "weather_cleaned.csv",
            "Fatalities": "fatalities_cleaned.csv"
        }

        for name, df in datasets.items():
            output_file = cleaned_folder / filenames[name]

            df.to_csv(output_file, index=False)

            print(f"{name}: {len(df):,} records saved")

        print("\nCleaned datasets saved to:", cleaned_folder)


    save_cleaned_datasets(cleaned_project_datasets)
    return


if __name__ == "__main__":
    app.run()
