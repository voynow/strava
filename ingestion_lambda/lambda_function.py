
import utils.s3ops as s3ops
import utils.strava_api as strava_api


def lambda_handler(event, context):
    """
    """
    access_token = strava_api.get_access_token()

    s3ops.update_activities(access_token)
    s3ops.update_tables(access_token)

    return 1
