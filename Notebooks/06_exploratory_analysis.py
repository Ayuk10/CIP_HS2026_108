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
    # 06 – Exploratory Data Analysis

    Explore trends and patterns in road traffic, collisions, weather conditions and road fatalities between 2000 and 2025. The analysis provides an initial understanding of the datasets before investigating the research questions in detail.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.1 Annual Traffic and Collision Trends

    Examine annual traffic volume and collision frequency in Great Britain to identify long-term trends and unusual changes.
    """)
    return


@app.cell
def _():
    def explore_annual_trends():
        from pathlib import Path
        import pandas as pd
        import matplotlib.pyplot as plt

        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Cleaned"
        )

        traffic = pd.read_csv(
            data_folder / "traffic_cleaned.csv",
            usecols=["year", "count_point_id", "all_motor_vehicles"]
        )

        collisions = pd.read_csv(
            data_folder / "collisions_cleaned.csv",
            usecols=["collision_year"]
        )

        # Summarize annual traffic volume
        traffic_annual = traffic.groupby("year").agg(
            mean_aadf=("all_motor_vehicles", "mean"),
            count_points=("count_point_id", "nunique")
        ).reset_index()

        # Count annual collisions
        collision_annual = (
            collisions.groupby("collision_year")
            .size()
            .reset_index(name="collisions")
            .rename(columns={"collision_year": "year"})
        )

        annual = traffic_annual.merge(
            collision_annual,
            on="year",
            how="inner"
        )

        print(annual.to_string(index=False))

        # Plot trends separately because the measurements have different units
        fig, axes = plt.subplots(2, 1, figsize=(11, 8))

        axes[0].plot(annual["year"], annual["mean_aadf"])
        axes[0].set_title("Average Daily Motor Vehicle Flow (2000–2025)")
        axes[0].set_ylabel("Mean AADF")
        axes[0].grid(alpha=0.3)

        axes[1].plot(annual["year"], annual["collisions"])
        axes[1].set_title("Reported Road Collisions (2000–2025)")
        axes[1].set_xlabel("Year")
        axes[1].set_ylabel("Number of collisions")
        axes[1].grid(alpha=0.3)

        plt.tight_layout()
        plt.show()

        return annual


    annual_traffic_collision_trends = explore_annual_trends()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.2 Initial Findings

    Annual road collisions in Great Britain declined considerably between 2000 and 2025, while average daily traffic volume fluctuated over the same period. Both indicators show a notable reduction around 2020.

    The different trends suggest that collision frequency cannot be explained by traffic volume alone. However, changes in traffic monitoring locations may affect annual averages, so further analysis is required before drawing conclusions about their relationship.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.3 Traffic Monitoring Coverage

    Examine the number of traffic count points recorded each year and identify locations consistently represented throughout 2000–2025. Changes in monitoring coverage may influence annual average traffic volume.
    """)
    return


@app.cell
def _():
    def analyze_traffic_coverage():
        from pathlib import Path
        import pandas as pd
        import matplotlib.pyplot as plt

        traffic_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Cleaned"
            / "traffic_cleaned.csv"
        )

        traffic = pd.read_csv(
            traffic_file,
            usecols=["year", "count_point_id", "all_motor_vehicles"]
        )

        # Count monitoring locations per year
        annual_coverage = (
            traffic.groupby("year")["count_point_id"]
            .nunique()
            .reset_index(name="count_points")
        )

        # Identify locations represented in all 26 years
        years_per_point = traffic.groupby("count_point_id")["year"].nunique()

        consistent_ids = years_per_point[
            years_per_point == 26
        ].index

        consistent_traffic = traffic[
            traffic["count_point_id"].isin(consistent_ids)
        ]

        # Compare overall mean AADF with consistently represented locations
        overall_mean = traffic.groupby("year")[
            "all_motor_vehicles"
        ].mean()

        consistent_mean = consistent_traffic.groupby("year")[
            "all_motor_vehicles"
        ].mean()

        annual_coverage["overall_mean_aadf"] = (
            annual_coverage["year"].map(overall_mean)
        )

        annual_coverage["consistent_mean_aadf"] = (
            annual_coverage["year"].map(consistent_mean)
        )

        print("Monitoring points represented in all 26 years:",
              len(consistent_ids))

        print("\nAnnual monitoring coverage:")
        print(annual_coverage.to_string(index=False))

        # Chart 1: Number of monitoring points
        plt.figure(figsize=(10, 4))
        plt.plot(
            annual_coverage["year"],
            annual_coverage["count_points"],
            marker="o"
        )
        plt.title("Traffic Monitoring Locations by Year")
        plt.xlabel("Year")
        plt.ylabel("Number of Count Points")
        plt.grid(alpha=0.3)
        plt.show()

        # Chart 2: Compare traffic trends
        plt.figure(figsize=(10, 4))
        plt.plot(
            annual_coverage["year"],
            annual_coverage["overall_mean_aadf"],
            label="All available locations"
        )
        plt.plot(
            annual_coverage["year"],
            annual_coverage["consistent_mean_aadf"],
            label="Consistent locations (2000–2025)"
        )
        plt.title("Mean AADF: All Locations vs Consistent Locations")
        plt.xlabel("Year")
        plt.ylabel("Mean AADF")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.show()

        return annual_coverage


    traffic_coverage_analysis = analyze_traffic_coverage()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.4 Traffic Coverage Findings

    The number of traffic monitoring locations varies considerably between 2000 and 2025. These changes influence the annual average daily traffic flow (AADF), producing fluctuations that may not reflect actual traffic changes.

    Restricting the analysis to locations represented throughout all 26 years produces a more stable trend. Therefore, consistently represented monitoring locations will be used for long-term traffic comparisons, while the complete dataset will be retained for geographical analysis.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.5 Geographical Matching Preparation

    Prepare traffic monitoring locations and collision coordinates for spatial matching. Collisions will be matched to the nearest traffic count point within the same year, subject to a maximum distance threshold.

    This approach enables location-based comparison of traffic volume and collision frequency. However, proximity does not necessarily mean that a collision occurred on the same road, so the matching distance and coverage must be evaluated before interpreting the results.
    """)
    return


@app.cell
def _():
    def inspect_spatial_coverage():
        from pathlib import Path
        import pandas as pd

        folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Cleaned"
        )

        traffic = pd.read_csv(
            folder / "traffic_cleaned.csv",
            usecols=["year", "count_point_id", "latitude", "longitude"]
        )

        collisions = pd.read_csv(
            folder / "collisions_cleaned.csv",
            usecols=["collision_year", "latitude", "longitude"]
        )

        print("TRAFFIC")
        print("Total records:", f"{len(traffic):,}")
        print("Missing coordinates:", f"{traffic[['latitude', 'longitude']].isna().any(axis=1).sum():,}")
        print("Duplicate count point/year combinations:",
              f"{traffic.duplicated(['year', 'count_point_id']).sum():,}")

        print("\nCOLLISIONS")
        print("Total records:", f"{len(collisions):,}")
        print("Missing coordinates:", f"{collisions[['latitude', 'longitude']].isna().any(axis=1).sum():,}")

        print("\nCoordinate ranges:")
        for name, df in [("Traffic", traffic), ("Collisions", collisions)]:
            print(
                f"{name}: latitude {df['latitude'].min():.3f} to {df['latitude'].max():.3f}, "
                f"longitude {df['longitude'].min():.3f} to {df['longitude'].max():.3f}"
            )


    inspect_spatial_coverage()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.6 Spatial Matching of Traffic and Collisions

    Match road collisions to their nearest traffic monitoring location within the same year using geographical coordinates.

    A maximum distance of 500 metres is applied to limit unsuitable matches. The matching rate and distance distribution will be evaluated before using the results to investigate the relationship between traffic volume and collision frequency.
    """)
    return


@app.cell
def _():
    def match_traffic_collisions():
        from pathlib import Path
        import pandas as pd
        import numpy as np
        from scipy.spatial import cKDTree

        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
        )

        traffic = pd.read_csv(
            data_folder / "Cleaned" / "traffic_cleaned.csv",
            usecols=[
                "year", "count_point_id",
                "easting", "northing",
                "all_motor_vehicles"
            ]
        )

        collisions = pd.read_csv(
            data_folder / "Cleaned" / "collisions_cleaned.csv",
            usecols=[
                "collision_year", "collision_index",
                "location_easting_osgr",
                "location_northing_osgr"
            ]
        )

        output_folder = data_folder / "Matched"
        output_folder.mkdir(parents=True, exist_ok=True)

        output_file = output_folder / "traffic_collision_matches.csv"

        total_matched = 0
        total_eligible = 0
        first_write = True

        for year in range(2000, 2026):
            year_traffic = traffic[traffic["year"] == year]
            year_collisions = collisions[
                collisions["collision_year"] == year
            ].dropna(
                subset=[
                    "location_easting_osgr",
                    "location_northing_osgr"
                ]
            )

            total_eligible += len(year_collisions)

            if year_traffic.empty or year_collisions.empty:
                continue

            # British National Grid coordinates are measured in metres
            traffic_coordinates = year_traffic[
                ["easting", "northing"]
            ].to_numpy()

            collision_coordinates = year_collisions[
                ["location_easting_osgr", "location_northing_osgr"]
            ].to_numpy()

            tree = cKDTree(traffic_coordinates)

            distances, indices = tree.query(
                collision_coordinates,
                k=1,
                distance_upper_bound=500
            )

            valid = np.isfinite(distances)

            matched = year_collisions.loc[
                valid, ["collision_index"]
            ].copy()

            nearest_points = year_traffic.iloc[
                indices[valid]
            ]

            matched["year"] = year
            matched["count_point_id"] = nearest_points[
                "count_point_id"
            ].to_numpy()

            matched["all_motor_vehicles"] = nearest_points[
                "all_motor_vehicles"
            ].to_numpy()

            matched["distance_m"] = distances[valid]

            matched.to_csv(
                output_file,
                mode="w" if first_write else "a",
                header=first_write,
                index=False
            )

            first_write = False
            total_matched += len(matched)

            print(
                f"{year}: {len(matched):,} / "
                f"{len(year_collisions):,} collisions matched"
            )

        print("\nTotal eligible collisions:", f"{total_eligible:,}")
        print("Total matched collisions:", f"{total_matched:,}")
        print(
            "Matching rate:",
            f"{total_matched / total_eligible * 100:.2f}%"
        )
        print("Saved:", output_file)


    match_traffic_collisions()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.7 Spatial Matching Assessment

    Using a 500-metre threshold, 1,971,849 of 3,995,500 eligible collisions (49.35%) were matched to traffic monitoring points within the same year.

    Matching coverage varied across years, particularly in 2002, when fewer monitoring points were available. Unmatched collisions are retained in the original dataset but excluded from the location-based comparison.

    Because geographical proximity does not guarantee that a collision occurred on the monitored road, the matching results are treated as approximate spatial associations rather than exact road-level matches.
    """)
    return


@app.cell
def _():
    def assess_matching_distances():
        from pathlib import Path
        import pandas as pd

        matched_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Matched"
            / "traffic_collision_matches.csv"
        )

        distances = pd.read_csv(
            matched_file,
            usecols=["distance_m"]
        )["distance_m"]

        print("Matching distance statistics (metres):")
        print(
            distances.describe(
                percentiles=[0.25, 0.50, 0.75, 0.90, 0.95]
            ).round(1).to_string()
        )

        print("\nMatches within each distance:")
        for threshold in [50, 100, 200, 300, 500]:
            count = (distances <= threshold).sum()
            print(
                f"{threshold:>3} m: {count:,} "
                f"({count / len(distances) * 100:.1f}% of matches)"
            )


    assess_matching_distances()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.8 Selection of Matching Distance

    The spatial matching assessment shows that 801,572 collisions (20.1% of eligible records) are located within 200 metres of a traffic monitoring point.

    A 200-metre threshold was selected for the primary analysis to reduce potential mismatches between nearby roads. The original 500-metre matches are retained for sensitivity analysis.

    Because the matching is based on geographical proximity rather than road network connectivity, the results represent approximate location-based relationships.
    """)
    return


@app.cell
def _():
    def prepare_200m_matches():
        from pathlib import Path
        import pandas as pd

        matched_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Matched"
        )

        matches = pd.read_csv(
            matched_folder / "traffic_collision_matches.csv"
        )

        matches_200m = matches[
            matches["distance_m"] <= 200
        ].copy()

        output_file = (
            matched_folder / "traffic_collision_matches_200m.csv"
        )

        matches_200m.to_csv(output_file, index=False)

        print("Collisions within 200 metres:", f"{len(matches_200m):,}")
        print("Unique monitoring points:", matches_200m["count_point_id"].nunique())
        print("Years covered:", matches_200m["year"].nunique())
        print("Saved:", output_file)

        return matches_200m


    traffic_collision_matches_200m = prepare_200m_matches()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.9 Traffic Volume and Collision Frequency

    Aggregate collisions by traffic monitoring point and year, then combine them with annual average daily traffic flow (AADF).

    Monitoring points without matched collisions are assigned a collision count of zero. This ensures that the analysis includes both locations with and without nearby reported collisions.
    """)
    return


@app.cell
def _():
    def aggregate_traffic_collisions():
        from pathlib import Path
        import pandas as pd

        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
        )

        # Load traffic monitoring records
        traffic = pd.read_csv(
            data_folder / "Cleaned" / "traffic_cleaned.csv",
            usecols=[
                "year",
                "count_point_id",
                "all_motor_vehicles",
                "road_type"
            ]
        )

        # Load collisions matched within 200 metres
        matches = pd.read_csv(
            data_folder / "Matched" / "traffic_collision_matches_200m.csv",
            usecols=["year", "count_point_id", "collision_index"]
        )

        # Count collisions for each monitoring point and year
        collision_counts = (
            matches.groupby(["year", "count_point_id"])
            .size()
            .reset_index(name="collision_count")
        )

        # Keep all traffic monitoring locations
        analysis = traffic.merge(
            collision_counts,
            on=["year", "count_point_id"],
            how="left",
            validate="one_to_one"
        )

        # Locations without matched collisions receive zero
        analysis["collision_count"] = (
            analysis["collision_count"]
            .fillna(0)
            .astype(int)
        )

        # Save analysis-ready dataset
        output_folder = data_folder / "Analysis"
        output_folder.mkdir(parents=True, exist_ok=True)

        output_file = (
            output_folder / "traffic_collision_analysis_200m.csv"
        )

        analysis.to_csv(output_file, index=False)

        print("Total monitoring point-year records:", f"{len(analysis):,}")
        print(
            "Records with nearby collisions:",
            f"{(analysis['collision_count'] > 0).sum():,}"
        )
        print(
            "Records without nearby collisions:",
            f"{(analysis['collision_count'] == 0).sum():,}"
        )
        print(
            "Total matched collisions:",
            f"{analysis['collision_count'].sum():,}"
        )

        print("\nFirst five records:")
        print(analysis.head().to_string(index=False))

        print("\nSaved:", output_file)

        return analysis


    traffic_collision_analysis = aggregate_traffic_collisions()
    return (traffic_collision_analysis,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.10 Relationship Between Traffic Volume and Collisions

    Examine the association between annual average daily traffic flow (AADF) and nearby collision frequency using correlation analysis and a scatter plot.

    Pearson correlation measures the strength of a linear relationship, while Spearman correlation assesses whether collision frequency generally increases with traffic volume.
    """)
    return


@app.cell
def _(traffic_collision_analysis):
    def analyze_traffic_collision_relationship():
        import pandas as pd
        import matplotlib.pyplot as plt

        analysis = traffic_collision_analysis[
            ["all_motor_vehicles", "collision_count"]
        ].dropna()

        # Calculate correlations
        pearson = analysis["all_motor_vehicles"].corr(
            analysis["collision_count"],
            method="pearson"
        )

        spearman = analysis["all_motor_vehicles"].corr(
            analysis["collision_count"],
            method="spearman"
        )

        print(f"Pearson correlation:  {pearson:.4f}")
        print(f"Spearman correlation: {spearman:.4f}")

        # Group traffic volumes into five categories
        analysis = analysis.copy()

        analysis["traffic_group"] = pd.qcut(
            analysis["all_motor_vehicles"],
            q=5,
            labels=[
                "Very Low",
                "Low",
                "Medium",
                "High",
                "Very High"
            ],
            duplicates="drop"
        )

        grouped = analysis.groupby(
            "traffic_group",
            observed=True
        ).agg(
            mean_aadf=("all_motor_vehicles", "mean"),
            mean_collisions=("collision_count", "mean"),
            observations=("collision_count", "size")
        )

        print("\nCollision frequency by traffic volume:")
        print(grouped.round(2).to_string())

        # Sample points for a readable scatter plot
        sample = analysis.sample(
            n=min(20000, len(analysis)),
            random_state=42
        )

        plt.figure(figsize=(10, 5))

        plt.scatter(
            sample["all_motor_vehicles"],
            sample["collision_count"],
            alpha=0.15,
            s=8
        )

        plt.title("Traffic Volume vs Nearby Road Collisions")
        plt.xlabel("Annual Average Daily Motor Vehicle Flow (AADF)")
        plt.ylabel("Collisions Within 200 Metres (Per Year)")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

        # Compare average collision counts across traffic groups
        plt.figure(figsize=(9, 5))

        plt.bar(
            grouped.index.astype(str),
            grouped["mean_collisions"]
        )

        plt.title("Average Nearby Collisions by Traffic Volume")
        plt.xlabel("Traffic Volume Category")
        plt.ylabel("Average Annual Collision Count")
        plt.tight_layout()
        plt.show()

        return grouped


    traffic_collision_relationship = analyze_traffic_collision_relationship()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.11 Traffic Volume and Collision Findings

    The analysis identifies a positive association between traffic volume and nearby collision frequency. Pearson correlation (0.1669) indicates a weak linear relationship, while Spearman correlation (0.3407) suggests a stronger positive rank-based relationship.

    Average annual nearby collisions increase from 0.42 at very low traffic locations to 2.32 at very high traffic locations. However, substantial variation remains between locations, indicating that traffic volume alone does not explain collision frequency.

    The findings are based on collisions matched within 200 metres of monitoring points and should be interpreted as spatial associations rather than direct evidence of causation or collision risk.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.12 Traffic and Collision Relationships by Road Type

    Compare the relationship between traffic volume and nearby collision frequency across major and minor roads to identify differences in road characteristics.
    """)
    return


@app.cell
def _(traffic_collision_analysis):
    def analyze_relationship_by_road_type():
        import pandas as pd
        import matplotlib.pyplot as plt

        analysis = traffic_collision_analysis[
            ["road_type", "all_motor_vehicles", "collision_count"]
        ].dropna()

        results = []

        for road_type, group in analysis.groupby("road_type"):
            results.append({
                "road_type": road_type,
                "observations": len(group),
                "mean_aadf": group["all_motor_vehicles"].mean(),
                "mean_collisions": group["collision_count"].mean(),
                "pearson": group["all_motor_vehicles"].corr(
                    group["collision_count"], method="pearson"
                ),
                "spearman": group["all_motor_vehicles"].corr(
                    group["collision_count"], method="spearman"
                )
            })

        summary = pd.DataFrame(results)

        print(summary.round(4).to_string(index=False))

        plt.figure(figsize=(9, 5))
        plt.bar(
            summary["road_type"],
            summary["mean_collisions"]
        )
        plt.title("Average Nearby Collisions by Road Type")
        plt.xlabel("Road Type")
        plt.ylabel("Average Annual Nearby Collisions")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.show()

        return summary


    road_type_relationship = analyze_relationship_by_road_type()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.13 Road Type Findings

    Major roads record higher average daily traffic volumes (20,781 vehicles) and more nearby collisions (1.57 annually) than minor roads (3,325 vehicles and 0.70 collisions).

    Both road types show positive correlations between traffic volume and collision frequency. The Pearson correlation is weaker for major roads (0.1250) than minor roads (0.2631), indicating differences in the strength of their linear relationships.

    These findings suggest that traffic volume is associated with collision frequency, but road characteristics and other factors may also contribute. The results describe nearby collision counts rather than traffic-adjusted collision risk.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.14 Weather Conditions and Collision Severity

    Examine how recorded weather conditions relate to road collision frequency and severity in Great Britain between 2000 and 2025.
    """)
    return


@app.cell
def _():
    def explore_collision_weather():
        from pathlib import Path
        import pandas as pd

        collision_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Cleaned"
            / "collisions_cleaned.csv"
        )

        weather_collisions = pd.read_csv(
            collision_file,
            usecols=[
                "collision_year",
                "weather_conditions",
                "collision_severity"
            ]
        )

        print("Recorded weather condition codes:")
        print(
            weather_collisions["weather_conditions"]
            .value_counts()
            .sort_index()
            .to_string()
        )

        print("\nCollision severity codes:")
        print(
            weather_collisions["collision_severity"]
            .value_counts()
            .sort_index()
            .to_string()
        )


    explore_collision_weather()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.15 Weather Conditions and Collision Severity Analysis

    Compare collision frequency and severity across recorded weather conditions. Fatal and serious collision percentages are calculated within each weather category to account for differences in the number of reported collisions.
    """)
    return


@app.cell
def _():
    def analyze_weather_severity():
        import pandas as pd
        import matplotlib.pyplot as plt
        from pathlib import Path

        weather_labels = {
            1: "Fine",
            2: "Rain",
            3: "Snow",
            4: "Fine + Wind",
            5: "Rain + Wind",
            6: "Snow + Wind",
            7: "Fog / Mist",
            8: "Other"
        }

        collision_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Cleaned"
            / "collisions_cleaned.csv"
        )

        # Load collision weather and severity data
        df = pd.read_csv(
            collision_file,
            usecols=["weather_conditions", "collision_severity"]
        )

        # Exclude unknown and missing weather conditions
        df = df[
            df["weather_conditions"].isin(weather_labels)
        ].copy()

        # Assign readable weather categories
        df["weather"] = df["weather_conditions"].map(weather_labels)

        # Identify fatal and serious collisions
        df["fatal_or_serious"] = df["collision_severity"].isin([1, 2])

        # Calculate collision frequency and severity by weather
        summary = df.groupby("weather").agg(
            collisions=("collision_severity", "size"),
            fatal_collisions=(
                "collision_severity",
                lambda x: (x == 1).sum()
            ),
            serious_collisions=(
                "collision_severity",
                lambda x: (x == 2).sum()
            ),
            fatal_serious_pct=("fatal_or_serious", "mean")
        )

        summary["fatal_serious_pct"] *= 100
        summary = summary.sort_values("collisions", ascending=False)

        print("Collision frequency and severity by weather:")
        print(summary.round(2).to_string())

        # Visualize fatal or serious collision percentages
        plt.figure(figsize=(10, 5))

        plt.bar(
            summary.index,
            summary["fatal_serious_pct"]
        )

        plt.title("Percentage of Fatal or Serious Collisions by Weather")
        plt.xlabel("Weather Condition")
        plt.ylabel("Fatal or Serious Collisions (%)")
        plt.xticks(rotation=30, ha="right")
        plt.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.show()

        return summary


    weather_severity_summary = analyze_weather_severity()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.16 Weather and Collision Severity Findings

    Collision severity varies across recorded weather conditions. Fine weather with high winds (18.79%) and fog or mist (18.71%) show the highest proportions of fatal or serious collisions, while snow without high winds shows the lowest (12.65%).

    These findings suggest that weather conditions may be associated with collision severity. However, differences in driving behaviour, traffic exposure and road characteristics may also influence the results. Therefore, the observed relationships should not be interpreted as causal effects.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.17 Weather Grid Coverage Assessment

    Assess the geographical coverage of the 30 selected weather grid locations by calculating their distances to road collisions in Great Britain.

    This helps determine an appropriate matching distance and identify collisions for which nearby weather observations are unavailable.
    """)
    return


@app.cell
def _():
    def assess_weather_grid_coverage():
        from pathlib import Path
        import pandas as pd
        import numpy as np
        from scipy.spatial import cKDTree

        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
        )

        weather = pd.read_csv(
            data_folder / "Weather" / "weather_daily_2000_2025.csv",
            usecols=["grid_id", "latitude", "longitude"]
        ).drop_duplicates("grid_id")

        collisions = pd.read_csv(
            data_folder / "Cleaned" / "collisions_cleaned.csv",
            usecols=["latitude", "longitude"]
        ).dropna()

        collision_sample = collisions.sample(
            n=min(100_000, len(collisions)),
            random_state=42
        )

        # Convert latitude and longitude to radians
        weather_coords = np.radians(
            weather[["latitude", "longitude"]].to_numpy()
        )

        collision_coords = np.radians(
            collision_sample[["latitude", "longitude"]].to_numpy()
        )

        # Convert geographical coordinates into 3D unit-sphere coordinates
        def to_xyz(coords):
            lat = coords[:, 0]
            lon = coords[:, 1]

            return np.column_stack([
                np.cos(lat) * np.cos(lon),
                np.cos(lat) * np.sin(lon),
                np.sin(lat)
            ])

        tree = cKDTree(to_xyz(weather_coords))

        chord_distances, indices = tree.query(
            to_xyz(collision_coords),
            k=1
        )

        # Convert spherical chord distance into kilometres
        distances_km = (
            2 * 6371 * np.arcsin(
                np.clip(chord_distances / 2, 0, 1)
            )
        )

        print("Weather grid locations:", len(weather))
        print("Sampled collisions:", len(collision_sample))

        print("\nDistance to nearest weather grid (km):")
        print(
            pd.Series(distances_km).describe(
                percentiles=[0.25, 0.50, 0.75, 0.90, 0.95]
            ).round(2).to_string()
        )

        print("\nCollisions within each distance:")
        for threshold in [10, 20, 30, 40, 50]:
            count = (distances_km <= threshold).sum()

            print(
                f"{threshold:>2} km: {count:,} "
                f"({count / len(distances_km) * 100:.1f}%)"
            )


    assess_weather_grid_coverage()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.18 Weather Matching Distance Selection

    The coverage assessment shows that approximately 34.8% of sampled collisions are within 30 km of a selected weather grid location, increasing to 61.4% within 50 km.

    A maximum distance of 30 km is selected for the primary analysis to reduce geographical uncertainty. A 50 km threshold will be considered for sensitivity analysis.

    Because weather conditions can vary across locations, the matched observations represent approximate local weather conditions rather than measurements taken directly at collision sites.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.19 Collision and Weather Data Integration

    Match road collisions to the nearest weather grid location within 30 km and combine them with daily precipitation, temperature, snowfall and wind speed observations.

    The resulting dataset will be used to examine associations between weather conditions and collision frequency and severity. Daily weather measurements are approximate and may not represent conditions at the exact time of a collision.
    """)
    return


@app.cell
def _():
    def match_collisions_to_weather():
        from pathlib import Path
        import pandas as pd
        import numpy as np
        from scipy.spatial import cKDTree

        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
        )

        weather = pd.read_csv(
            data_folder / "Cleaned" / "weather_cleaned.csv"
        )

        collisions = pd.read_csv(
            data_folder / "Cleaned" / "collisions_cleaned.csv",
            usecols=[
                "collision_index",
                "collision_year",
                "date",
                "latitude",
                "longitude",
                "collision_severity",
                "weather_conditions"
            ]
        )

        # Prepare daily weather observations
        weather["date"] = pd.to_datetime(weather["time"]).dt.normalize()

        weather_locations = (
            weather[["grid_id", "latitude", "longitude"]]
            .drop_duplicates("grid_id")
            .reset_index(drop=True)
        )

        # Keep collisions with valid coordinates and dates
        collisions["date"] = pd.to_datetime(
            collisions["date"],
            errors="coerce"
        ).dt.normalize()

        eligible = collisions.dropna(
            subset=["latitude", "longitude", "date"]
        ).copy()

        # Convert geographical coordinates to 3D unit-sphere coordinates
        def to_xyz(coordinates):
            radians = np.radians(coordinates)
            lat = radians[:, 0]
            lon = radians[:, 1]

            return np.column_stack([
                np.cos(lat) * np.cos(lon),
                np.cos(lat) * np.sin(lon),
                np.sin(lat)
            ])

        weather_xyz = to_xyz(
            weather_locations[["latitude", "longitude"]].to_numpy()
        )

        collision_xyz = to_xyz(
            eligible[["latitude", "longitude"]].to_numpy()
        )

        tree = cKDTree(weather_xyz)

        chord_distances, indices = tree.query(
            collision_xyz,
            k=1
        )

        distances_km = (
            2 * 6371 * np.arcsin(
                np.clip(chord_distances / 2, 0, 1)
            )
        )

        # Keep collisions within 30 km
        within_30km = distances_km <= 30

        matched = eligible.loc[within_30km].copy()

        matched["grid_id"] = weather_locations.iloc[
            indices[within_30km]
        ]["grid_id"].to_numpy()

        matched["weather_distance_km"] = distances_km[within_30km]

        # Join weather observations using grid location and date
        weather_daily = weather[
            [
                "grid_id",
                "date",
                "precipitation_sum",
                "temperature_2m_mean",
                "snowfall_sum",
                "wind_speed_10m_max"
            ]
        ]

        matched = matched.merge(
            weather_daily,
            on=["grid_id", "date"],
            how="left",
            validate="many_to_one"
        )

        # Save matched dataset
        output_folder = data_folder / "Matched"
        output_folder.mkdir(parents=True, exist_ok=True)

        output_file = (
            output_folder / "collision_weather_matches_30km.csv"
        )

        matched.to_csv(output_file, index=False)

        print("Total collisions:", f"{len(collisions):,}")
        print("Eligible collisions:", f"{len(eligible):,}")
        print("Matched within 30 km:", f"{len(matched):,}")

        print(
            "Matching rate:",
            f"{len(matched) / len(eligible) * 100:.2f}%"
        )

        print(
            "Missing matched weather observations:",
            f"{matched['precipitation_sum'].isna().sum():,}"
        )

        print("\nFirst five records:")
        print(matched.head().to_string(index=False))

        print("\nSaved:", output_file)

        return output_file


    collision_weather_matched_file = match_collisions_to_weather()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.20 Weather Matching Results

    A total of 1,395,216 collisions (34.92% of eligible records) were matched to daily weather observations within 30 km. All matched collisions have corresponding weather data.

    The matched dataset provides a basis for examining relationships between weather conditions and collision severity. However, the observations represent daily weather near collision locations rather than conditions at the exact collision time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.21 Daily Weather and Collision Severity

    Examine how precipitation, snowfall, temperature and wind speed are associated with the proportion of fatal or serious road collisions.
    """)
    return


@app.cell
def _():
    def analyze_daily_weather_severity():
        from pathlib import Path
        import pandas as pd
        import matplotlib.pyplot as plt

        matched_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Matched"
            / "collision_weather_matches_30km.csv"
        )

        df = pd.read_csv(
            matched_file,
            usecols=[
                "collision_severity",
                "precipitation_sum",
                "temperature_2m_mean",
                "snowfall_sum",
                "wind_speed_10m_max"
            ]
        )

        df["fatal_or_serious"] = df["collision_severity"].isin([1, 2])

        # Define weather categories
        df["rain_day"] = df["precipitation_sum"] >= 1
        df["snow_day"] = df["snowfall_sum"] > 0
        df["windy_day"] = df["wind_speed_10m_max"] >= 40

        weather_variables = {
            "Rain (≥1 mm)": "rain_day",
            "Snowfall (>0 cm)": "snow_day",
            "Strong wind (≥40 km/h)": "windy_day"
        }

        results = []

        for label, column in weather_variables.items():
            for condition in [False, True]:
                subset = df[df[column] == condition]

                results.append({
                    "weather_condition": label,
                    "condition_present": condition,
                    "collisions": len(subset),
                    "fatal_serious_pct": (
                        subset["fatal_or_serious"].mean() * 100
                    )
                })

        summary = pd.DataFrame(results)

        print("Daily weather and collision severity:")
        print(summary.round(2).to_string(index=False))

        # Compare fatal/serious percentages
        chart_data = summary.pivot(
            index="weather_condition",
            columns="condition_present",
            values="fatal_serious_pct"
        )

        chart_data.columns = ["Condition absent", "Condition present"]

        chart_data.plot(
            kind="bar",
            figsize=(10, 5)
        )

        plt.title("Fatal or Serious Collision Percentage by Daily Weather")
        plt.xlabel("Weather Condition")
        plt.ylabel("Fatal or Serious Collisions (%)")
        plt.xticks(rotation=15, ha="right")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.show()

        return summary


    daily_weather_severity_results = analyze_daily_weather_severity()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.22 Daily Weather and Collision Severity Findings

    The analysis shows differences in collision severity across daily weather conditions. Fatal or serious collisions account for 14.56% of collisions on rainy days, compared with 15.65% on days without significant rainfall. Snowfall days also show a lower proportion (13.57% versus 15.27%).

    In contrast, strong-wind days have a higher proportion of fatal or serious collisions (16.26%) than days without strong winds (15.19%).

    These findings indicate associations between daily weather conditions and collision severity, but they do not establish causation. Driving behaviour, traffic exposure, geographical coverage and the use of daily rather than hourly weather observations may influence the results.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.23 Daily Weather and Collision Frequency

    Aggregate collisions by weather grid location and date, including days with zero recorded collisions. Compare average daily collision counts under different precipitation, snowfall and wind conditions.

    The analysis examines associations rather than collision risk, since daily traffic exposure is not available.
    """)
    return


@app.cell
def _():
    def analyze_weather_collision_frequency():
        from pathlib import Path
        import pandas as pd
        import matplotlib.pyplot as plt

        data_folder = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
        )

        # Load daily weather observations
        weather = pd.read_csv(
            data_folder / "Cleaned" / "weather_cleaned.csv",
            usecols=[
                "grid_id",
                "time",
                "precipitation_sum",
                "snowfall_sum",
                "wind_speed_10m_max"
            ]
        )

        weather["date"] = pd.to_datetime(weather["time"])

        # Load collisions matched to weather grids
        matches = pd.read_csv(
            data_folder / "Matched" / "collision_weather_matches_30km.csv",
            usecols=["grid_id", "date", "collision_index"]
        )

        matches["date"] = pd.to_datetime(matches["date"])

        # Count collisions by grid and date
        daily_counts = (
            matches.groupby(["grid_id", "date"])
            .size()
            .reset_index(name="collision_count")
        )

        # Preserve all weather observation days, including zero collisions
        daily = weather.merge(
            daily_counts,
            on=["grid_id", "date"],
            how="left",
            validate="one_to_one"
        )

        daily["collision_count"] = (
            daily["collision_count"].fillna(0).astype(int)
        )

        # Define exploratory weather conditions
        daily["Rain (≥1 mm)"] = daily["precipitation_sum"] >= 1
        daily["Snowfall (>0 cm)"] = daily["snowfall_sum"] > 0
        daily["Strong wind (≥40 km/h)"] = (
            daily["wind_speed_10m_max"] >= 40
        )

        results = []

        for condition in [
            "Rain (≥1 mm)",
            "Snowfall (>0 cm)",
            "Strong wind (≥40 km/h)"
        ]:
            for present in [False, True]:
                subset = daily[daily[condition] == present]

                results.append({
                    "weather_condition": condition,
                    "condition_present": present,
                    "grid_days": len(subset),
                    "total_collisions": subset["collision_count"].sum(),
                    "mean_daily_collisions": subset["collision_count"].mean()
                })

        summary = pd.DataFrame(results)

        print("Weather and daily collision frequency:")
        print(summary.round(3).to_string(index=False))

        print("\nTotal collisions:", f"{daily['collision_count'].sum():,}")
        print("Total grid-days:", f"{len(daily):,}")

        # Save analysis-ready daily dataset
        output_folder = data_folder / "Analysis"
        output_folder.mkdir(parents=True, exist_ok=True)

        daily.to_csv(
            output_folder / "weather_collision_daily_30km.csv",
            index=False
        )

        # Visualize daily collision frequency
        chart_data = summary.pivot(
            index="weather_condition",
            columns="condition_present",
            values="mean_daily_collisions"
        )

        chart_data.columns = [
            "Condition absent",
            "Condition present"
        ]

        chart_data.plot(kind="bar", figsize=(10, 5))

        plt.title("Average Daily Nearby Collisions by Weather Condition")
        plt.xlabel("Weather Condition")
        plt.ylabel("Average Collisions per Grid-Day")
        plt.xticks(rotation=15, ha="right")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.show()

        return summary


    weather_collision_frequency_results = (
        analyze_weather_collision_frequency()
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.24 Weather and Collision Frequency Findings

    Average daily nearby collision counts are lower during rainfall (4.12 versus 5.56), snowfall (4.03 versus 4.93) and strong winds (0.83 versus 6.04).

    These differences may reflect changes in travel behaviour, seasonal patterns and geographical characteristics rather than weather effects alone.

    Further analysis is required to account for differences between weather grid locations and years before drawing conclusions about the relationship between weather and collision frequency.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.25 Annual Weather and Collision Frequency Comparison

    Compare daily collision frequency during windy and non-windy conditions within each year to determine whether the observed difference remains consistent over time.
    """)
    return


@app.cell
def _():
    def analyze_annual_wind_collision_frequency():
        from pathlib import Path
        import pandas as pd
        import matplotlib.pyplot as plt

        daily_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Analysis"
            / "weather_collision_daily_30km.csv"
        )

        df = pd.read_csv(
            daily_file,
            usecols=[
                "date",
                "wind_speed_10m_max",
                "collision_count"
            ],
            parse_dates=["date"]
        )

        df["year"] = df["date"].dt.year
        df["windy"] = df["wind_speed_10m_max"] >= 40

        annual = (
            df.groupby(["year", "windy"])
            .agg(
                grid_days=("collision_count", "size"),
                mean_collisions=("collision_count", "mean")
            )
            .reset_index()
        )

        print("Annual collision frequency by wind condition:")
        print(annual.round(2).to_string(index=False))

        chart = annual.pivot(
            index="year",
            columns="windy",
            values="mean_collisions"
        )

        chart = chart.rename(
            columns={
                False: "No strong wind",
                True: "Strong wind"
            }
        )

        chart.plot(figsize=(11, 5), marker="o")

        plt.title("Daily Collision Frequency by Wind Condition and Year")
        plt.xlabel("Year")
        plt.ylabel("Average Collisions per Grid-Day")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

        return annual


    annual_wind_collision_results = (
        analyze_annual_wind_collision_frequency()
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.26 Annual Wind Analysis Findings

    Average daily collision frequency is consistently lower during strong-wind conditions across 2000–2025. Both windy and non-windy observations also show a long-term decline in collision frequency.

    The persistent difference cannot be explained by annual trends alone. Differences in geographical coverage, road networks and traffic exposure may influence the results, requiring further analysis at individual weather grid locations.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.27 Wind and Collision Frequency by Weather Grid

    Compare average daily collision frequency during windy and non-windy conditions within each weather grid location to assess whether geographical differences influence the observed relationship.
    """)
    return


@app.cell
def _():
    def analyze_wind_by_grid():
        from pathlib import Path
        import pandas as pd
        import matplotlib.pyplot as plt

        daily_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Analysis"
            / "weather_collision_daily_30km.csv"
        )

        df = pd.read_csv(
            daily_file,
            usecols=[
                "grid_id",
                "wind_speed_10m_max",
                "collision_count"
            ]
        )

        df["windy"] = df["wind_speed_10m_max"] >= 40

        summary = (
            df.groupby(["grid_id", "windy"])
            .agg(
                grid_days=("collision_count", "size"),
                mean_collisions=("collision_count", "mean")
            )
            .reset_index()
        )

        comparison = summary.pivot(
            index="grid_id",
            columns="windy",
            values="mean_collisions"
        ).rename(
            columns={
                False: "No strong wind",
                True: "Strong wind"
            }
        )

        print("Collision frequency by weather grid:")
        print(comparison.round(2).to_string())

        print(
            "\nGrids with both conditions:",
            comparison.dropna().shape[0]
        )

        comparison.plot(
            kind="bar",
            figsize=(13, 5)
        )

        plt.title("Daily Collision Frequency by Weather Grid and Wind Condition")
        plt.xlabel("Weather Grid Location")
        plt.ylabel("Average Collisions per Grid-Day")
        plt.xticks(rotation=90)
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        plt.show()

        return comparison


    wind_grid_comparison = analyze_wind_by_grid()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.28 Geographical Differences in Weather Analysis

    Collision frequency varies substantially between weather grid locations. Some grids record many nearby collisions, while others record very few.

    Within individual grids, differences between windy and non-windy days appear considerably smaller than in the overall comparison. This suggests that geographical differences influence the observed relationship between wind conditions and collision frequency.

    Further analysis should control for location and year before interpreting the association.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.29 Location-Adjusted Wind and Collision Frequency

    Compare windy and non-windy collision frequency within the same weather grid and year. This reduces the influence of geographical differences and long-term changes in collision frequency.
    """)
    return


@app.cell
def _():
    def analyze_adjusted_wind_frequency():
        from pathlib import Path
        import pandas as pd
        import numpy as np

        daily_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Analysis"
            / "weather_collision_daily_30km.csv"
        )

        df = pd.read_csv(
            daily_file,
            usecols=[
                "grid_id",
                "date",
                "wind_speed_10m_max",
                "collision_count"
            ],
            parse_dates=["date"]
        )

        df["year"] = df["date"].dt.year
        df["windy"] = df["wind_speed_10m_max"] >= 40

        # Compare conditions within each grid and year
        grouped = (
            df.groupby(["grid_id", "year", "windy"])
            .agg(
                days=("collision_count", "size"),
                mean_collisions=("collision_count", "mean")
            )
            .reset_index()
        )

        comparison = grouped.pivot(
            index=["grid_id", "year"],
            columns="windy",
            values=["days", "mean_collisions"]
        )

        # Require at least 10 days under each condition
        comparison = comparison[
            (comparison[("days", False)] >= 10) &
            (comparison[("days", True)] >= 10)
        ].copy()

        comparison["difference"] = (
            comparison[("mean_collisions", True)]
            - comparison[("mean_collisions", False)]
        )

        print("Grid-year comparisons:", len(comparison))
        print(
            "Average difference in collisions per grid-day:",
            round(comparison["difference"].mean(), 3)
        )
        print(
            "Median difference:",
            round(comparison["difference"].median(), 3)
        )

        print(
            "Grid-years with higher collisions on windy days:",
            round((comparison["difference"] > 0).mean() * 100, 1),
            "%"
        )

        return comparison


    adjusted_wind_comparison = analyze_adjusted_wind_frequency()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.30 Location-Adjusted Wind Findings

    Comparing windy and non-windy days within the same weather grid and year produces an average difference of only −0.06 collisions per day, with a median difference of zero.

    This is substantially smaller than the difference observed in the overall comparison, suggesting that geographical and annual differences influence the results.

    The findings do not provide strong evidence of a large association between strong winds and collision frequency after accounting for location and year. However, other factors, including seasonality and traffic exposure, remain unaccounted for.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.31 Location-Adjusted Rainfall and Snowfall Analysis

    Compare collision frequency on rainy, snowy and other days within the same weather grid and year to reduce the influence of geographical differences and long-term trends.
    """)
    return


@app.cell
def _():
    def analyze_adjusted_precipitation_frequency():
        from pathlib import Path
        import pandas as pd

        daily_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Analysis"
            / "weather_collision_daily_30km.csv"
        )

        df = pd.read_csv(
            daily_file,
            usecols=[
                "grid_id",
                "date",
                "precipitation_sum",
                "snowfall_sum",
                "collision_count"
            ],
            parse_dates=["date"]
        )

        df["year"] = df["date"].dt.year

        conditions = {
            "Rain (≥1 mm)": df["precipitation_sum"] >= 1,
            "Snowfall (>0 cm)": df["snowfall_sum"] > 0
        }

        results = []

        for label, condition in conditions.items():
            subset = df.assign(condition_present=condition)

            grouped = (
                subset.groupby(["grid_id", "year", "condition_present"])
                .agg(
                    days=("collision_count", "size"),
                    mean_collisions=("collision_count", "mean")
                )
                .reset_index()
            )

            comparison = grouped.pivot(
                index=["grid_id", "year"],
                columns="condition_present",
                values=["days", "mean_collisions"]
            )

            # Require at least 10 days in both groups
            comparison = comparison.dropna()

            comparison = comparison[
                (comparison[("days", False)] >= 10) &
                (comparison[("days", True)] >= 10)
            ]

            difference = (
                comparison[("mean_collisions", True)]
                - comparison[("mean_collisions", False)]
            )

            results.append({
                "weather_condition": label,
                "grid_year_comparisons": len(comparison),
                "average_difference": difference.mean(),
                "median_difference": difference.median(),
                "pct_higher_on_condition_days": (
                    (difference > 0).mean() * 100
                )
            })

        summary = pd.DataFrame(results)

        print("Location- and year-adjusted comparisons:")
        print(summary.round(3).to_string(index=False))

        return summary


    adjusted_precipitation_results = (
        analyze_adjusted_precipitation_frequency()
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.32 Weather and Collision Frequency Findings

    After comparing observations within the same weather grid and year, rainfall shows a small positive average difference (+0.173 collisions per grid-day), while snowfall shows a negative difference (−0.290). Strong winds also show a small negative difference (−0.060).

    The median differences are close to zero, suggesting that the typical grid-year experiences relatively little change in collision frequency across these conditions.

    Overall, weather is associated with differences in collision frequency and severity, but the relationships are influenced by geographical and temporal factors. The results do not establish causation or account for changes in traffic exposure.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.33 Road Fatality Rates: Great Britain vs Switzerland

    Compare annual road traffic fatalities per 100,000 inhabitants in Great Britain and Switzerland between 2000 and 2025. Population-adjusted rates allow comparisons between countries of different sizes.
    """)
    return


@app.cell
def _():
    def compare_road_fatality_rates():
        from pathlib import Path
        import pandas as pd
        import matplotlib.pyplot as plt

        fatalities_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Cleaned"
            / "fatalities_cleaned.csv"
        )

        fatalities = pd.read_csv(fatalities_file)

        print("Annual road fatality rates:")
        print(
            fatalities.pivot(
                index="year",
                columns="country",
                values="fatalities_per_100k"
            ).round(2).to_string()
        )

        plt.figure(figsize=(11, 5))

        for country, group in fatalities.groupby("country"):
            group = group.sort_values("year")

            plt.plot(
                group["year"],
                group["fatalities_per_100k"],
                marker="o",
                markersize=3,
                label=country
            )

        plt.title("Road Traffic Fatalities per 100,000 Inhabitants (2000–2025)")
        plt.xlabel("Year")
        plt.ylabel("Fatalities per 100,000 Inhabitants")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

        return fatalities


    fatality_rate_comparison = compare_road_fatality_rates()
    return (fatality_rate_comparison,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.34 Road Fatality Comparison Findings

    Road traffic fatality rates declined substantially in both Great Britain and Switzerland between 2000 and 2025.

    Great Britain's rate decreased from approximately 6.1 to 2.28 fatalities per 100,000 inhabitants, while Switzerland's decreased from approximately 8.2 to 2.34.

    Although Switzerland initially recorded a higher fatality rate, the difference between the countries narrowed considerably. By 2025, both countries had similar population-adjusted fatality rates.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.35 Long-Term Changes in Road Fatality Rates

    Calculate the absolute and percentage changes in road traffic fatality rates between 2000 and 2025 to compare improvements in Great Britain and Switzerland.
    """)
    return


@app.cell
def _(fatality_rate_comparison):
    def analyze_fatality_rate_changes():
        import pandas as pd

        df = fatality_rate_comparison[
            ["country", "year", "fatalities_per_100k"]
        ].copy()

        results = []

        for country, group in df.groupby("country"):
            start_rate = group.loc[
                group["year"] == 2000, "fatalities_per_100k"
            ].iloc[0]

            end_rate = group.loc[
                group["year"] == 2025, "fatalities_per_100k"
            ].iloc[0]

            results.append({
                "country": country,
                "rate_2000": start_rate,
                "rate_2025": end_rate,
                "absolute_change": end_rate - start_rate,
                "percentage_change": (
                    (end_rate - start_rate) / start_rate * 100
                )
            })

        summary = pd.DataFrame(results)

        print("Road fatality rate changes (2000–2025):")
        print(summary.round(2).to_string(index=False))

        return summary


    fatality_rate_changes = analyze_fatality_rate_changes()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.36 Final Findings: Great Britain vs Switzerland

    Between 2000 and 2025, road traffic fatality rates declined by 62.36% in Great Britain and 71.47% in Switzerland.

    Switzerland achieved the larger percentage reduction, narrowing the initial difference between the two countries. By 2025, Great Britain recorded 2.28 fatalities per 100,000 inhabitants, compared with 2.34 in Switzerland.

    Both countries demonstrate substantial long-term improvements in population-adjusted road safety outcomes. However, these rates do not account for differences in distance travelled, road networks or traffic exposure.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.37 Additional Road Safety Comparisons

    Visualize the percentage reduction in fatality rates, the annual difference between Great Britain and Switzerland, and the total number of road traffic deaths.

    These comparisons provide additional perspectives on long-term road safety improvements between 2000 and 2025.
    """)
    return


@app.cell
def _():
    def visualize_additional_fatality_comparisons():
        from pathlib import Path
        import pandas as pd
        import matplotlib.pyplot as plt

        fatalities_file = (
            Path.home()
            / "Documents"
            / "CIP_HS2026_Group_108"
            / "Data"
            / "Cleaned"
            / "fatalities_cleaned.csv"
        )

        df = pd.read_csv(fatalities_file)

        colors = {
            "Great Britain": "#0072B2",
            "Switzerland": "#E69F00"
        }

        # Chart 1: Percentage reduction in fatality rates
        summary = []

        for country, group in df.groupby("country"):
            rates = group.set_index("year")["fatalities_per_100k"]

            reduction = (
                (rates.loc[2000] - rates.loc[2025])
                / rates.loc[2000] * 100
            )

            summary.append({
                "country": country,
                "reduction": reduction
            })

        reductions = pd.DataFrame(summary)

        plt.figure(figsize=(8, 5))

        bars = plt.bar(
            reductions["country"],
            reductions["reduction"],
            color=[colors[c] for c in reductions["country"]]
        )

        for bar in bars:
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 1,
                f"{bar.get_height():.1f}%",
                ha="center"
            )

        plt.title("Reduction in Road Fatality Rates (2000–2025)")
        plt.ylabel("Reduction (%)")
        plt.ylim(0, 85)
        plt.tight_layout()
        plt.show()

        # Chart 2: Difference in fatality rates
        rates = df.pivot(
            index="year",
            columns="country",
            values="fatalities_per_100k"
        )

        difference = (
            rates["Switzerland"] - rates["Great Britain"]
        )

        plt.figure(figsize=(11, 5))

        plt.plot(
            difference.index,
            difference.values,
            color="#0072B2",
            linewidth=2
        )

        plt.axhline(0, color="gray", linestyle="--")

        plt.title("Fatality Rate Difference: Switzerland Minus Great Britain")
        plt.xlabel("Year")
        plt.ylabel("Difference per 100,000 Inhabitants")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

        # Chart 3: Annual road traffic deaths
        plt.figure(figsize=(11, 5))

        for country, group in df.groupby("country"):
            group = group.sort_values("year")

            plt.plot(
                group["year"],
                group["road_deaths"],
                label=country,
                color=colors[country],
                linewidth=2
            )

        plt.title("Annual Road Traffic Deaths (2000–2025)")
        plt.xlabel("Year")
        plt.ylabel("Number of Road Traffic Deaths")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()


    visualize_additional_fatality_comparisons()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6.38 Additional Findings: Great Britain and Switzerland

    The additional visualizations confirm substantial improvements in road safety in both countries between 2000 and 2025.

    Switzerland recorded a larger percentage reduction in population-adjusted fatality rates (71.47%) than Great Britain (62.36%). The difference between the countries narrowed considerably, with both recording similar fatality rates by 2025.

    Annual road traffic deaths also declined in both countries. However, differences in population size make fatality rates per 100,000 inhabitants more suitable for international comparison than absolute death counts.

    Overall, the findings indicate long-term improvements in road safety and a convergence in fatality rates between Great Britain and Switzerland.
    """)
    return


if __name__ == "__main__":
    app.run()
