
def get_code(encoded):
    print("html.get_code")
    return f"""
    <!DOCTYPE html>
    <html>
        
        <head>
            <title>Strava Analytics Dashboard</title>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #eeeeee;
                    font-family: Helvetica;
                }}

            </style>
        </head>

        <body>
            <img src="strava-logo.jpg" width="100" height="100" style="position: absolute; top: 0; left: 0;">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 75%;">
                <h1 style="color: #434343; text-align: center;">Strava Analytics</h1>
                <p style="font-size: 16px; color: #434343; font-weight: bold; text-align: center;">Don't know what strava is? <a href="https://www.strava.com/athletes/98390356">Check out my profile</a></p>
                <img src='data:image/png;base64,{encoded}' alt="matplotlib fig derived from strava data" style="margin: 20px auto; width: 100%; border-radius: 10px; box-shadow: 0 10px 20px rgba(0, 0, 0, 0.19), 0 10px 20px rgba(0, 0, 0, 0.23);">
                <div style="width: 75%; margin: 0 auto; font-size: 20px; color: #434343;">
                    <p style="font-size: 22px; font-weight: bold; margin-bottom: 0;">This dashboard is updated daily at 11:30pm EST</p>
                    <ul style="margin: 0; padding-top: 5px;">
                        <li>The <a href="https://github.com/voynow/strava-ingestion-lambda">ingestion lambda</a> is responsible for querying the strava API and storing the data in S3</li>
                        <li>The <a href="https://github.com/voynow/strava-dashboard-lambda">dashboard lambda</a> queries the S3 data and updates the dashboard accordingly</li>
                    </ul>
                </div>
            </div>
        </body>

    </html>
    """