
import boto3
import json
import time

import utils.strava_api as strava_api
import utils.configs as configs


bucket_name = "strava-raw"
s3 = boto3.resource('s3')


def load_table(bucket, table):
    """ Get json table from s3
    """
    obj = s3.Object(bucket, table)
    return json.loads(obj.get()['Body'].read())


def validate_data(data):
    """ Validatation prior to put_object
    """
    ids = list(data.keys())
    if ids == sorted(ids):
        return True
    else:
        return False


def put_object(data, bucket, filename):
    """ Write json table to s3
    """
    if validate_data(data):
        s3_obj = s3.Object(bucket, filename)
        resp = s3_obj.put(Body=json.dumps(data))
    else:
        raise ValueError(f"{filename} data validation failure (IDs not ordered)")
    return resp


def append_new_data(new_data, existing_data):
    """ Append new activities to activities table
    """
    for key in sorted(new_data.keys()):
        item = new_data[key]
        
        if key not in existing_data and item is not None:
            print(f"New activity: id={key}")
            item['api_call_ts'] = time.strftime(configs.strfrmt)
            existing_data[key] = item
            
    return existing_data


def update_activities(access_token):
    """ write activities to strava-raw s3 bucket
    """
    table_name = "activities"
    filename = f"{table_name}.json"
    print(f"Updating {table_name} table: s3://{bucket_name}/{filename}")

    activities_from_api = strava_api.get_activities(access_token)
    existing_activities = load_table(bucket_name, filename)
    new_data = {str(activity['id']): activity for activity in activities_from_api}
    master_activities = append_new_data(new_data, existing_activities)

    put_object(master_activities, bucket_name, filename)


def laps_table_postprocess(table):
    """ list->dict formatting required for laps reponse
    """
    if isinstance(table, list):
        table = {lap['id']: lap for lap in table}
    return table


def get_table(ids, table_name, access_token):

    table = {}
    for idx, url in strava_api.get_urls(ids, table_name):
        print(f"Request: table={table_name}, url={url[:80]}")

        response = strava_api.get_request(access_token, url)
        if table_name == "laps":
            response = laps_table_postprocess(response)
        table[idx] = response
    return table


def update_tables(access_token):
    """
    """
    activity_ids = list(load_table(bucket_name, "activities.json").keys())

    for table_name in configs.activities_endpoints:
        filename = f"{table_name}.json"
        print(f"Updating {table_name} table: s3://{bucket_name}/{filename}")

        table = load_table(bucket_name, filename)
        missing_ids = [i for i in activity_ids if i not in table]
        new_data = get_table(missing_ids, table_name, access_token)
        master_table = append_new_data(new_data, table)

        put_object(master_table, bucket_name, filename)
