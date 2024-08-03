import os
from datetime import datetime, timedelta
from typing import Dict, List

import polars as pl
from dotenv import load_dotenv
from stravalib.client import Client
from stravalib.model import Activity

load_dotenv()


def activities_to_df(activities: List[Activity]) -> pl.DataFrame:
    """
    Converts a list of activities into polars DataFrame

    :param activities: List of activity objects to be converted to DataFrame
    :return: A polars DataFrame with activities data
    """
    df_schema = {
        "id": pl.UInt64,
        "name": pl.Utf8,
        "distance": pl.Float64,
        "moving_time": pl.Duration,
        "total_elevation_gain": pl.Float64,
        "start_date_local": pl.Datetime,
    }
    df_builder: Dict[str, List] = {}

    for activity in activities:
        for attribute in df_schema:
            if attribute not in df_builder:
                df_builder[attribute] = []
            if activity.sport_type == "Run":
                df_builder[attribute].append(getattr(activity, attribute))

    return pl.DataFrame(
        {col: pl.Series(df_builder[col], dtype=df_schema[col]) for col in df_schema}
    )


def preprocess_activities_df(df: pl.DataFrame) -> pl.DataFrame:
    """
    Cleans and transforms the activities DataFrame by sorting, converting units,
    and adding derived columns.

    :param df: The initial polars DataFrame containing activity data
    :return: A transformed polars DataFrame with cleansed data
    """
    # Define transformation operations for each column
    col_operations = [
        pl.col("start_date_local").dt.strftime("%a").alias("day_of_week"),
        pl.col("start_date_local").dt.week().alias("week_of_year"),
        pl.col("start_date_local").dt.year().alias("year"),
        (pl.col("distance") / 1609.34).alias("distance_in_miles"),
        (pl.col("total_elevation_gain") * 3.28084).alias("elevation_gain_in_feet"),
        (pl.col("moving_time") / 60).alias("moving_time_in_minutes"),
        ((pl.col("moving_time") / 60) / (pl.col("distance") / 1609.34)).alias(
            "pace_minutes_per_mile"
        ),
    ]

    # Apply transformations, sorting, and column removals
    return (
        df.sort("start_date_local")
        .with_columns(col_operations)
        .drop(["distance", "total_elevation_gain", "moving_time"])
    )


def get_activities_df(strava_client: Client) -> pl.DataFrame:
    """
    Fetches and returns activities data for a given athlete ID as a DataFrame,
    cleansed and processed

    :param athlete_id: The Strava athlete ID
    :return: A cleaned and processed DataFrame of the athlete's activities
    """
    timedelta_6_weeks = datetime.now() - timedelta(weeks=7)
    activities = strava_client.get_activities(after=timedelta_6_weeks)
    raw_df = activities_to_df(activities)
    return preprocess_activities_df(raw_df)


def get_days_of_week_summary(activities_df: pl.DataFrame) -> pl.DataFrame:
    """
    Aggregate activities DataFrame by day of the week and calculate
    summary statistics for each day
    ------------------------------------------------------------
    day_of_week	number_of_runs	avg_miles	avg_minutes	avg_pace
    "Mon"	    6	            7.585097	7.2053e7	9.5744e6
    "Tue"	    7	            3.317314	3.4145e7	1.0248e7
    ...
    ------------------------------------------------------------
    :param activities_df: The DataFrame containing activities data
    :return: A DataFrame with summary statistics for each day of the week
    """
    days_of_week_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    return (
        activities_df.groupby("day_of_week")
        .agg(
            [
                pl.col("id").count().alias("number_of_runs"),
                pl.col("distance_in_miles").mean().alias("avg_miles"),
                pl.col("moving_time_in_minutes").mean().alias("avg_minutes"),
                pl.col("pace_minutes_per_mile").mean().alias("avg_pace"),
            ]
        )
        .with_columns(
            pl.col("day_of_week")
            .apply(lambda x: days_of_week_order.index(x))
            .alias("day_order")
        )
        .sort("day_order")
        .drop("day_order")
    )


def get_weekly_summary(activities_df: pl.DataFrame) -> pl.DataFrame:
    """
    Aggregate activities DataFrame by week of the year and calculate
    load for each week
    --------------------------------------
    year	week_of_year	total_distance
    2024	23	            7.585097
    2024	22	            3.317314
    ...
    --------------------------------------
    :param activities_df: The DataFrame containing activities data
    :return: A DataFrame with weekly load for each week of the year
    """
    return (
        activities_df.groupby(["year", "week_of_year"])
        .agg(
            [
                pl.col("distance_in_miles").sum().alias("total_distance"),
            ]
        )
        .sort(["year", "week_of_year"])
        .reverse()
    )