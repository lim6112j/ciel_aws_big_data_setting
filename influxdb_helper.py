import os
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxDBHelper:
    def __init__(self):
        self.url = os.getenv('INFLUXDB_URL')
        self.token = os.getenv('INFLUXDB_TOKEN')
        self.org = os.getenv('INFLUXDB_ORG')
        self.bucket = os.getenv('INFLUXDB_BUCKET')
        
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org, verify_ssl=False)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    def write_aws_cloudwatch_metrics(self, metric_data):
        """Write AWS CloudWatch-style metrics to InfluxDB"""
        points = []
        for metric in metric_data:
            point = Point(metric['MetricName']) \
                .tag('Namespace', metric.get('Namespace', 'AWS/Custom')) \
                .tag('Region', os.getenv('AWS_REGION', 'us-east-1'))
            
            # Add dimensions as tags
            for dimension in metric.get('Dimensions', []):
                point = point.tag(dimension['Name'], dimension['Value'])
            
            # Add value
            point = point.field('Value', metric['Value']) \
                         .time(metric.get('Timestamp', datetime.now(timezone.utc)))
            
            points.append(point)
        
        self.write_api.write(bucket=self.bucket, record=points)

    def get_latest_metrics(self, measurement, hours=1):
        """Get latest metrics for a measurement"""
        query = f'''
        from(bucket: "{self.bucket}")
        |> range(start: -{hours}h)
        |> filter(fn: (r) => r._measurement == "{measurement}")
        |> last()
        '''
        return self.query_api.query(query)

    def close(self):
        """Close the InfluxDB client"""
        self.client.close()
