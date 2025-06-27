#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# InfluxDB Details
INFLUX_TOKEN="YOUR_INFLUXDB_TOKEN_HERE"
INFLUX_ORG="mobble_commute"
INFLUX_HOST="http://test.2bt.kr:8086"
INFLUX_QUERY=\'\'\'from(bucket: "locations") |> range(start: 0) |> filter(fn: (r) => r._measurement == "locReports")\'\'\'

# File Paths
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOCAL_CSV_FILE="/Users/byeongcheollim/workspace/locReports_${TIMESTAMP}.csv"
HDFS_DEST_DIR="/user/byeongcheollim/workspace/locReports"
SUMMARY_FILE="/Users/byeongcheollim/summary.md"

# --- Script Execution ---

echo "Starting data transfer for ${TIMESTAMP}..."

# 1. Export data from InfluxDB
echo "Exporting data from InfluxDB to ${LOCAL_CSV_FILE}..."
curl --silent --request POST "${INFLUX_HOST}/api/v2/query?org=${INFLUX_ORG}" \
  --header "Authorization: Token ${INFLUX_TOKEN}" \
  --header "Accept: application/csv" \
  --header "Content-type: application/vnd.flux" \
  --data "${INFLUX_QUERY}" \
  -o "${LOCAL_CSV_FILE}"

if [ ! -s "${LOCAL_CSV_FILE}" ]; then
    echo "Error: Export failed or the resulting file is empty. Aborting."
    exit 1
fi
echo "Export successful."

# 2. Create HDFS directory if it doesn't exist
hdfs dfs -mkdir -p "${HDFS_DEST_DIR}"

# 3. Upload the file to HDFS
echo "Uploading ${LOCAL_CSV_FILE} to HDFS..."
hdfs dfs -put "${LOCAL_CSV_FILE}" "${HDFS_DEST_DIR}/"
echo "Upload successful."

# 4. Clean up the local file
echo "Cleaning up local file: ${LOCAL_CSV_FILE}..."
rm "${LOCAL_CSV_FILE}"

# 5. Create the summary markdown file
echo "Creating summary file at ${SUMMARY_FILE}..."
cat <<EOF > "${SUMMARY_FILE}"
# Automated InfluxDB to HDFS Transfer Summary

This report was generated automatically by the `influx_to_hdfs.sh` script.

## Run Details

- **Execution Timestamp:** ${TIMESTAMP}
- **Status:** Success

## Actions Performed

1.  **Data Export:**
    - **Source Measurement:** `locReports`
    - **Destination Local File:** `${LOCAL_CSV_FILE}` (This file was temporary and has been removed)

2.  **HDFS Upload:**
    - **Source Local File:** `${LOCAL_CSV_FILE}`
    - **Uploaded To HDFS Path:** `${HDFS_DEST_DIR}/${LOCAL_CSV_FILE##*/}`

3.  **Cleanup:**
    - The local file `${LOCAL_CSV_FILE}` was successfully removed after upload.
EOF

echo "Process complete. Summary created at ${SUMMARY_FILE}"
