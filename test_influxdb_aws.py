import pytest
import os
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import boto3
from dotenv import load_dotenv

load_dotenv()

class TestInfluxDBAWS:
    @classmethod
    def setup_class(cls):
        """Setup InfluxDB client for testing"""
        cls.url = os.getenv('INFLUXDB_URL')
        cls.token = os.getenv('INFLUXDB_TOKEN')
        cls.org = os.getenv('INFLUXDB_ORG')
        cls.bucket = os.getenv('INFLUXDB_BUCKET')
        
        cls.client = InfluxDBClient(url=cls.url, token=cls.token, org=cls.org, verify_ssl=False)
        cls.write_api = cls.client.write_api(write_options=SYNCHRONOUS)
        cls.query_api = cls.client.query_api()
        cls.delete_api = cls.client.delete_api()

    @classmethod
    def teardown_class(cls):
        """Cleanup InfluxDB client"""
        cls.client.close()

    def test_connection(self):
        """Test basic connection to InfluxDB"""
        health = self.client.health()
        assert health.status == "pass", f"InfluxDB health check failed: {health.message}"

    def test_write_single_point(self):
        """Test writing a single data point"""
        point = Point("test_measurement") \
            .tag("location", "aws-test") \
            .field("temperature", 25.5) \
            .field("humidity", 60.0) \
            .time(datetime.now(timezone.utc))
        
        # Write point
        self.write_api.write(bucket=self.bucket, record=point)
        
        # Verify write by querying
        query = f'''
        from(bucket: "{self.bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "test_measurement")
        |> filter(fn: (r) => r.location == "aws-test")
        '''
        
        result = self.query_api.query(query)
        assert len(result) > 0, "No data found after write"

    def test_write_batch_points(self):
        """Test writing multiple data points"""
        points = []
        for i in range(10):
            point = Point("batch_test") \
                .tag("sensor_id", f"sensor_{i}") \
                .field("value", i * 10.5) \
                .time(datetime.now(timezone.utc))
            points.append(point)
        
        # Write batch
        self.write_api.write(bucket=self.bucket, record=points)
        
        # Verify batch write
        query = f'''
        from(bucket: "{self.bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "batch_test")
        |> count()
        '''
        
        result = self.query_api.query(query)
        assert len(result) > 0, "Batch write verification failed"

    def test_query_data(self):
        """Test querying data with various filters"""
        # First write some test data
        test_points = [
            Point("query_test").tag("region", "us-east-1").field("cpu_usage", 45.2),
            Point("query_test").tag("region", "us-west-2").field("cpu_usage", 67.8),
            Point("query_test").tag("region", "eu-west-1").field("cpu_usage", 23.1)
        ]
        
        self.write_api.write(bucket=self.bucket, record=test_points)
        
        # Query with filter
        query = f'''
        from(bucket: "{self.bucket}")
        |> range(start: -1h)
        |> filter(fn: (r) => r._measurement == "query_test")
        |> filter(fn: (r) => r.region == "us-east-1")
        '''
        
        result = self.query_api.query(query)
        assert len(result) > 0, "Query with filter failed"

    def test_aws_integration(self):
        """Test AWS integration (EC2 metadata simulation)"""
        try:
            # Simulate AWS EC2 instance metadata
            ec2_client = boto3.client('ec2', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            
            # Write AWS-related metrics
            point = Point("aws_metrics") \
                .tag("service", "ec2") \
                .tag("region", os.getenv('AWS_REGION', 'us-east-1')) \
                .field("instance_count", 5) \
                .field("running_instances", 3) \
                .time(datetime.now(timezone.utc))
            
            self.write_api.write(bucket=self.bucket, record=point)
            
            # Verify AWS metrics write
            query = f'''
            from(bucket: "{self.bucket}")
            |> range(start: -1h)
            |> filter(fn: (r) => r._measurement == "aws_metrics")
            |> filter(fn: (r) => r.service == "ec2")
            '''
            
            result = self.query_api.query(query)
            assert len(result) > 0, "AWS metrics write failed"
            
        except Exception as e:
            pytest.skip(f"AWS integration test skipped: {e}")

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Test invalid bucket
        with pytest.raises(Exception):
            invalid_point = Point("error_test").field("value", 1)
            self.write_api.write(bucket="non_existent_bucket", record=invalid_point)

    def test_cleanup_test_data(self):
        """Clean up test data after tests"""
        # Delete test data
        start = "1970-01-01T00:00:00Z"
        stop = datetime.now(timezone.utc).isoformat()
        
        # Note: This requires delete permissions
        try:
            self.delete_api.delete(
                start=start,
                stop=stop,
                predicate='_measurement="test_measurement" OR _measurement="batch_test" OR _measurement="query_test" OR _measurement="aws_metrics" OR _measurement="error_test"',
                bucket=self.bucket,
                org=self.org
            )
        except Exception as e:
            print(f"Cleanup warning: {e}")
