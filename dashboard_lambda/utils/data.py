import boto3
import datetime
import json
import numpy as np
import pandas as pd

raw_bucket = "strava-raw"
s3 = boto3.resource('s3')


def get_activities(bucket, table):
    """
    Get activities JSON from raw bucket
    """
    print("data.get_activities")
    obj = s3.Object(bucket, table)
    table = json.loads(obj.get()['Body'].read())
    return [data for _, data in table.items()]


def clean(df):
    
    print("data.clean")
    # update date col as pandas datetime
    df['date'] = pd.to_datetime(df['start_date'].apply(lambda x: x.split("T")[0]))
    df.drop(['start_date'], axis=1, inplace=True)
    
    # meters -> miles
    df['distance'] *= 0.000621371
    
    return df
    

def activities_to_df(activities):
    """
    Create pandas dataframe from list of activities
    """
    print("data.activities_to_df")
    keys = []
    [[keys.append(item) for item in activity] for activity in activities]
    unique_keys = set(keys)

    keys_by_activity = [[key for key in activity] for activity in activities]
    for keys in keys_by_activity:
        remove_keys = []
        for key in unique_keys:
            if key not in keys:
                remove_keys.append(key)
        for key in remove_keys:
            unique_keys.remove(key)
    
    activities = [{key: activity[key] for key in unique_keys} for activity in activities]
    return clean(pd.DataFrame(activities))


def fill_missing_dates(df):
    """
    Add rows for dates where no activity exists
    """
    print("data.fill_missing_dates")
    if 'date' not in df.columns:
        raise ValueError("Missing required column: 'date'")
    date_range = pd.date_range(df['date'].min(), datetime.date.today())
    dates_df = pd.DataFrame(date_range, columns=['date'])
    joined_df = dates_df.set_index('date').join(df.set_index('date'))
    
    return joined_df


def get_data():
    """ Prepare data for analytics
    """
    print("data.get_data")
    activities = get_activities(raw_bucket, "activities.json")
    df = activities_to_df(activities)

    run_df = df[df['type'] == 'Run']

    return run_df


def calc_moving_average():
    """ Apply transformation according to date, calculate moving averages
    """
    print("data.calc_moving_average")
    
    df = fill_missing_dates(get_data())
    df = df.groupby('date')[['total_elevation_gain', 'distance']].sum()

    df['distance'] = df['distance'].apply(lambda x: 0 if np.isnan(x) else x)
    df['distance_monthly_ma'] = df['distance'].rolling(30).sum().rolling(2).mean()
    df['distance_week_ma'] = df['distance'].rolling(7).sum().rolling(2).mean()

    return df


def load_table(bucket, table):
    """ Get json table from s3
    """
    print("data.load_table")
    obj = s3.Object(bucket, table)
    return json.loads(obj.get()['Body'].read())

    
def get_philly_heatmap():
    """ Get lat, lng data from activities (of type=run) in philadelphia
    """
    print("data.get_philly_heatmap")
    latlon_data = {"xs": [], "ys": []}

    for _, obj in load_table(raw_bucket, "streams.json").items():
        if 'latlng' in obj:
            y, x = np.transpose(obj['latlng']['data'])

            # only append data within philadelphia boundary
            if np.mean(x) > -75.4 and np.mean(x) < -75 and np.mean(y) > 39.6:
                latlon_data['xs'].append(x)
                latlon_data['ys'].append(-1 * y)

    # convert to hist
    hist, _, _ = np.histogram2d(
        np.hstack(latlon_data['ys']),
        np.hstack(latlon_data['xs']),
        bins=125)

    # pad array with zeros for better visualization
    hist = np.pad(hist, 2)

    # add 1 offset to avoid log(0)
    return np.log(hist + 1)
