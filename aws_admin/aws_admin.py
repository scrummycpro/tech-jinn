import boto3
import sqlite3
import os
import random
import json
from datetime import datetime
import sys

class UserManager:
    def __init__(self, db_name="user_management.db"):
        # Initialize Boto3 clients
        self.iam = boto3.client('iam')
        self.s3 = boto3.client('s3')
        self.sts = boto3.client('sts')

        # Initialize SQLite database
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        # Create the users table if it doesn't exist
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            user_name TEXT,
            bucket_name TEXT,
            access_key_id TEXT,
            secret_access_key TEXT,
            timestamp TEXT,
            status TEXT
        )''')
        self.conn.commit()
        print("Database and table are ready.")

    def create_user_and_bucket(self, user_name):
        try:
            # Generate a random user ID
            user_id = str(random.randint(100000, 999999))
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Create IAM user
            try:
                user = self.iam.create_user(UserName=user_name)
                print(f"User {user_name} created successfully.")
            except self.iam.exceptions.EntityAlreadyExistsException:
                print(f"User {user_name} already exists.")
                return

            # Create S3 bucket
            bucket_name = f"{user_id}-bucket".lower()
            self.s3.create_bucket(Bucket=bucket_name)
            print(f"Bucket {bucket_name} created successfully.")

            # Create a policy that restricts the user to access only their specific bucket
            policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:ListBucket"
                        ],
                        "Resource": f"arn:aws:s3:::{bucket_name}"
                    },
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:PutObject",
                            "s3:GetObject",
                            "s3:DeleteObject"
                        ],
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }

            # Attach the policy to the IAM user
            self.iam.put_user_policy(
                UserName=user_name,
                PolicyName=f"{user_name}_S3AccessPolicy",
                PolicyDocument=json.dumps(policy_document)
            )
            print(f"Policy attached to user {user_name} restricting access to bucket {bucket_name}.")

            # Create access keys for the IAM user
            access_key = self.iam.create_access_key(UserName=user_name)
            access_key_id = access_key['AccessKey']['AccessKeyId']
            secret_access_key = access_key['AccessKey']['SecretAccessKey']
            print(f"Access keys created for user {user_name}.")

            # Save the user information in the SQLite database
            self.cursor.execute('''INSERT INTO users (user_id, user_name, bucket_name, access_key_id, secret_access_key, timestamp, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                (user_id, user_name, bucket_name, access_key_id, secret_access_key, timestamp, 'active'))
            self.conn.commit()
            print(f"User {user_name} information saved in database.")

            # Save the access keys locally
            with open(f"{user_name}_access_keys.txt", "w") as f:
                f.write(f"AWS Access Key ID: {access_key_id}\n")
                f.write(f"AWS Secret Access Key: {secret_access_key}\n")
            print(f"Access keys saved locally as {user_name}_access_keys.txt.")

        except Exception as e:
            print(f"An error occurred: {e}")

    def destroy_user(self, user_name):
        try:
            # Fetch user information from the database
            self.cursor.execute("SELECT user_id, bucket_name FROM users WHERE user_name=? AND status='active'", (user_name,))
            row = self.cursor.fetchone()

            if row:
                user_id, bucket_name = row

                # Delete the S3 bucket and its contents
                try:
                    print(f"Attempting to delete objects in bucket {bucket_name}...")

                    # Initialize the S3 resource to delete objects
                    s3_resource = boto3.resource('s3')
                    bucket = s3_resource.Bucket(bucket_name)

                    # Delete all objects in the bucket
                    bucket.objects.all().delete()
                    print(f"All objects in bucket {bucket_name} deleted successfully.")

                    # Delete the bucket itself
                    self.s3.delete_bucket(Bucket=bucket_name)
                    print(f"Bucket {bucket_name} deleted successfully.")
                except Exception as e:
                    print(f"Error deleting bucket {bucket_name}: {e}")

                # Detach and delete all inline policies from the IAM user
                try:
                    print(f"Attempting to delete inline policies for user {user_name}...")
                    
                    # List all inline policies
                    policies = self.iam.list_user_policies(UserName=user_name)
                    for policy_name in policies['PolicyNames']:
                        print(f"Deleting inline policy {policy_name} from user {user_name}...")
                        # Delete each inline policy
                        self.iam.delete_user_policy(UserName=user_name, PolicyName=policy_name)
                        print(f"Deleted policy {policy_name} from user {user_name}.")
                except Exception as e:
                    print(f"Error deleting inline policies for user {user_name}: {e}")

                # Detach managed policies from the IAM user
                try:
                    print(f"Attempting to detach managed policies for user {user_name}...")
                    
                    attached_policies = self.iam.list_attached_user_policies(UserName=user_name)
                    for policy in attached_policies['AttachedPolicies']:
                        print(f"Detaching managed policy {policy['PolicyName']} from user {user_name}...")
                        self.iam.detach_user_policy(UserName=user_name, PolicyArn=policy['PolicyArn'])
                        print(f"Detached managed policy {policy['PolicyName']} from user {user_name}.")
                except Exception as e:
                    print(f"Error detaching managed policies for user {user_name}: {e}")

                # Delete the IAM user
                try:
                    print(f"Attempting to delete IAM user {user_name}...")
                    
                    self.iam.delete_user(UserName=user_name)
                    print(f"User {user_name} deleted successfully.")
                except Exception as e:
                    print(f"Error deleting user {user_name}: {e}")

                # Update the status in the database
                self.cursor.execute("UPDATE users SET status='disabled' WHERE user_name=?", (user_name,))
                self.conn.commit()
                print(f"User {user_name} marked as disabled in the database.")
            else:
                print(f"User {user_name} not found or already disabled.")

        except Exception as e:
            print(f"An error occurred during user deletion: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python aws_user_manager.py <create|delete> <username>")
        sys.exit(1)

    action = sys.argv[1].lower()
    user_name = sys.argv[2]

    manager = UserManager()

    if action == "create":
        manager.create_user_and_bucket(user_name)
    elif action == "delete":
        manager.destroy_user(user_name)
    else:
        print("Unknown action. Use 'create' or 'delete'.")
