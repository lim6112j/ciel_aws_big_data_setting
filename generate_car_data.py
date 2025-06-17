import random
import time
import argparse
import os
import ssl
import urllib3
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def generate_car_data(duration):
    """Generates dummy car movement data and writes it to InfluxDB every 1 second."""

    start_time = time.time()
    end_time = start_time + (duration * 3600)  # Convert hours to seconds

    # Load environment variables
    load_dotenv()
    influxdb_url = os.getenv('INFLUXDB_URL')
    influxdb_token = os.getenv('INFLUXDB_TOKEN')
    influxdb_org = os.getenv('INFLUXDB_ORG')
    influxdb_bucket = os.getenv('INFLUXDB_BUCKET')

    # Initialize InfluxDB client with comprehensive SSL and connection settings
    client = InfluxDBClient(
        url=influxdb_url, 
        token=influxdb_token, 
        org=influxdb_org,
        verify_ssl=False,
        ssl_ca_cert=None,
        timeout=30000,
        retries=3
    )
    write_api = client.write_api(write_options=SYNCHRONOUS)

    current_time = start_time
    while current_time <= end_time:
        # Simulate car data
        latitude = round(random.uniform(34.0, 34.1), 6)  # Example range
        longitude = round(random.uniform(-118.2, -118.1), 6)  # Example range
        speed = round(random.uniform(0, 60), 2)  # Speed in mph
        heading = round(random.uniform(0, 359), 2)  # Heading in degrees

        # Create a Point object
        point = Point("car_data") \
            .tag("car_id", "1") \
            .field("latitude", latitude) \
            .field("longitude", longitude) \
            .field("speed", speed) \
            .field("heading", heading) \
            .time(int(current_time * 1e9), "ns")

        # Write the data to InfluxDB with error handling
        try:
            write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)
            print(f"Written data point at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}")
        except Exception as e:
            print(f"Error writing to InfluxDB: {e}")
            break

        current_time += 1
        time.sleep(1)

    # Close the client
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate car data and inject it into InfluxDB for a given duration.")
    parser.add_argument("--duration", type=int,
                        help="Duration in hours", required=True)

    args = parser.parse_args()

    generate_car_data(args.duration)
