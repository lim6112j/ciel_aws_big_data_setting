### Summary of Data Transfer: InfluxDB to HDFS

This document outlines the commands used to export data from an InfluxDB v2 instance and prepare it for HDFS upload.

**1. Data Export from InfluxDB v2**

The following `curl` command was used to query the InfluxDB API directly. This method was chosen after initial attempts with the `influx` CLI failed due to configuration differences.

- **Command:**
  ```bash
  curl --request POST 'http://test.2bt.kr:8086/api/v2/query?org=mobble_commute' \
    --header 'Authorization: Token YOUR_INFLUXDB_TOKEN_HERE' \
    --header 'Accept: application/csv' \
    --header 'Content-type: application/vnd.flux' \
    --data 'from(bucket: "locations") |> range(start: 0) |> filter(fn: (r) => r._measurement == "locReports")' \
    > ~/workspace/locReports.csv
  ```
- **Purpose:** To export data from the `locReports` measurement into a local CSV file named `locReports.csv`.
- **Outcome:** The command successfully created the data file at `~/workspace/locReports.csv`.

**2. Verification of Exported File**

This command confirmed that the export was successful and the local file was created.

- **Command:**
  ```bash
  ls ~/workspace/locReports.csv
  ```
- **Purpose:** To verify the existence of the exported CSV file.
- **Outcome:** The command succeeded, confirming the file was ready for the next step.

**3. HDFS Upload (Pending)**

This command was prepared to upload the local file to HDFS but was not executed.

- **Command:**
  ```bash
  hdfs dfs -put ~/workspace/locReports.csv /user/byeongcheollim/workspace/locReports
  ```
- **Purpose:** To move the local `locReports.csv` file into the HDFS directory.

To schedule it to run daily at 2 AM:

1.  Run crontab -e
2.  Add this line:

1 0 2 \* \* \* /Users/byeongcheollim/influx_to_hdfs.sh >> /Users/byeongcheollim/influx_to_hdfs.log 2>&1
