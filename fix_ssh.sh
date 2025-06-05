#!/bin/bash

# --- IMPORTANT: HOW TO RUN THIS SCRIPT ---
# If you see a "permission denied" error when trying to run this script,
# you first need to make it executable. Run this command in your terminal:
#
# chmod +x fix_ssh.sh
#
# After that, you can run the script with:
#
# ./fix_ssh.sh
# -----------------------------------------

# This script contains the steps to fix the "Permission denied (publickey)" SSH error
# when connecting to an EC2 instance.
#
# Run these commands on your local machine.

# --- STEP 1: Set Correct Permissions for the Private Key ---
# Your private key file must be protected from being read by others.
# This is the most common reason for the "Permission denied" error.

echo "Setting required permissions for your private key..."
chmod 400 "ciel_big_data_ed25519.pem"

if [ $? -eq 0 ]; then
    echo "Permissions for 'ciel_big_data_ed25519.pem' set to 400 (read-only for you)."
else
    echo "Could not set permissions. Please run 'chmod 400 ciel_big_data_ed25519.pem' manually."
    exit 1
fi

echo ""
echo "--- STEP 2: Attempt to Connect Again ---"
echo "Try connecting with the 'admin' user first:"
echo "ssh -i \"ciel_big_data_ed25519.pem\" admin@ec2-3-35-11-66.ap-northeast-2.compute.amazonaws.com"
echo ""
echo "If that fails, try the default username for your EC2 instance's OS."
echo "Common usernames are 'ec2-user' (for Amazon Linux, RHEL) or 'ubuntu' (for Ubuntu)."
echo ""
echo "Example for Amazon Linux:"
echo "ssh -i \"ciel_big_data_ed25519.pem\" ec2-user@ec2-3-35-11-66.ap-northeast-2.compute.amazonaws.com"
echo ""
echo "Example for Ubuntu:"
echo "ssh -i \"ciel_big_data_ed25519.pem\" ubuntu@ec2-3-35-11-66.ap-northeast-2.compute.amazonaws.com"
echo ""

echo "--- STEP 3: Use Verbose Mode for Debugging (If Still Failing) ---"
echo "If you still can't connect, use the '-v' flag to get detailed error information."
echo "Replace YOUR_USERNAME with the username you are trying ('admin', 'ec2-user', etc.)."
echo ""
echo "ssh -v -i \"ciel_big_data_ed25519.pem\" YOUR_USERNAME@ec2-3-35-11-66.ap-northeast-2.compute.amazonaws.com"
