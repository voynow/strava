
import base64
import boto3
from io import BytesIO
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import utils.html as html


dashbaord_bucket = "strava-dashboard"
html_filename = 'index.html'
s3 = boto3.client('s3')
figsize = (14, 6)


def create_fig(df, heatmap):
    """ matplotlib subplot for dashboard visualizations
    """
    print("dashboard.create_fig")
    # figure setup
    fig = plt.figure(constrained_layout=True, figsize=figsize)
    axs = fig.subplot_mosaic(
        [['Left', 'TopRight'],['Left', 'BottomRight']],
        gridspec_kw={'width_ratios':[1, 2]})
    fig.tight_layout(pad=3.0)

    # heatmap configuration
    axs['Left'].set_title("Philly Running Heatmap")
    axs['Left'].imshow(heatmap, cmap="hot")
    axs['Left'].tick_params(left=False, bottom=False)
    axs['Left'].axis('off')

    # Monthly mileage configuration
    axs['TopRight'].set_title('Monthly Mileage')
    axs['TopRight'].set_ylabel('Mileage')
    axs['TopRight'].plot(
        df.index, 
        df['distance_monthly_ma'], 
        c='#BD3446',
        linewidth=3
    )

    # Weekly mileage configuration
    axs['BottomRight'].set_title('Weekly Mileage')
    axs['BottomRight'].set_ylabel('Mileage')
    axs['BottomRight'].plot(
        df.index, 
        df['distance_week_ma'], 
        c='#348ABD', 
        linewidth=3
    )

    return fig


def update_dashboard(df, heatmap):
    """
    Generate html from matplotlib plot
    """
    print("dashboard.update_dashboard")
    tmpfile = BytesIO()
    fig = create_fig(df, heatmap)

    fig.savefig(tmpfile, format='png')
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    html_string = html.get_code(encoded)

    s3.put_object(
        Bucket=dashbaord_bucket,
        Key=html_filename,
        Body=html_string,
        ContentType="text/html",
    )
