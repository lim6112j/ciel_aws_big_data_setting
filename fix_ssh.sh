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
echo "--- STEP 2: Attempting SSH Connections ---"

# Try different common usernames
USERNAMES=("admin" "ec2-user" "ubuntu")
HOST="ec2-3-35-11-66.ap-northeast-2.compute.amazonaws.com"
KEY_FILE="ciel_big_data_ed25519.pem"

for username in "${USERNAMES[@]}"; do
    echo ""
    echo "Trying to connect with username: $username"
    echo "Running: ssh -o ConnectTimeout=10 -o BatchMode=yes -i \"$KEY_FILE\" $username@$HOST"
    
    # Attempt connection with timeout and non-interactive mode
    ssh -o ConnectTimeout=10 -o BatchMode=yes -i "$KEY_FILE" "$username@$HOST" "echo 'Connection successful with user: $username'" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "SUCCESS! You can connect using:"
        echo "ssh -i \"$KEY_FILE\" $username@$HOST"
        exit 0
    else
        echo "Failed to connect with username: $username"
    fi
done

echo ""
echo "--- All automatic attempts failed ---"
echo "Try manual connection with verbose output to see detailed error:"
echo "ssh -v -i \"$KEY_FILE\" admin@$HOST"
echo ""
echo "Or try with a different username if you know the correct one for your EC2 instance."
