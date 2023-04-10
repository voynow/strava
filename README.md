 

# Strava Dashboard & Ingestion
This repository provides code for creating and managing a dashboard of Strava data. This includes a dashboard module for visualizing the data and an ingestion module for retrieving data from the Strava API.

## Requirements
The following Python libraries are required to run this code:
* Numpy 
* Matplotlib
* Boto3 
* Requests
* Selenium 
* Pandas

## Files
### dashboard_lambda/lambda_function.py
This code takes data from the utils module and generates a moving average from it. It then creates a heatmap to represent Philadelphia data and sends the data frames and heatmap to an update_dashboard function in the dashboard module. Finally, it returns a value of 1.
### dashboard_lambda/utils/dashboard.py
This code creates a dashboard updates it with data from given data frames and a heatmap. Finally, it uploads the page to an s3 bucket in order to create a live dashboard.
### dashboard_lambda/utils/data.py
This function prepares activity data stored on Amazon S3 and prepares it for analytics.
### dashboard_lambda/utils/html.py
This code returns an html page with the Strava logo in the top left corner, a title and a link to the profile of the user, an encoded visualization of the data, and a link to the code on github at the bottom.
### ingestion_lambda/lambda_function.py
This code imports two utility libraries and uses their functions to update activities and related tables in an S3 bucket. It then returns 1.
### ingestion_lambda/utils/configs.py
This code imports the utils.secrets_manager module which will be used to get secrets. It then unpacks the secrets and defines parameters for creating a figure. 
### ingestion_lambda/utils/s3ops.py
This code downloads a json table from s3, validates it, then reaches out to an external Strava API to request missing data which it appends to the json table and writes back to S3.
### ingestion_lambda/utils/secrets_manager.py
This code creates a Secrets Manager Client using the boto3 library, to retrieve stored configuration details from AWS Secrets Manager.
### ingestion_lambda/utils/strava_api.py
This code attempts to access the Strava API, as well as construct requests to the Straval API for activities, and validate responses.