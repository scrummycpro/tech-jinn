import sqlite3
import boto3
import os
import random
import json
from datetime import datetime

class UserManager:
    def __init__(self, db_name="user_management.db"):
        self.db_name = db_name
        self.iam = boto3.client('iam')
        self.s3 = boto3.client('s3')

    def _get_connection(self):
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def create_user_and_bucket(self, user_name):
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Generate a random user ID
            user_id = str(random.randint(100000, 999999))
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Create IAM user
            user = self.iam.create_user(UserName=user_name)
            print(f"User {user_name} created successfully.")

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
            cursor.execute('''INSERT INTO users (user_id, user_name, bucket_name, access_key_id, secret_access_key, timestamp, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (user_id, user_name, bucket_name, access_key_id, secret_access_key, timestamp, 'active'))
            conn.commit()
            print(f"User {user_name} information saved in database.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

    def get_last_50_users(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_name, bucket_name, status, access_key_id, secret_access_key FROM users ORDER BY id DESC LIMIT 50")
        users = cursor.fetchall()
        conn.close()
        return users

    def export_user_credentials_to_csv(self, user_name, csv_filename):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT access_key_id, secret_access_key FROM users WHERE user_name=?", (user_name,))
        user = cursor.fetchone()
        conn.close()

        if user:
            with open(csv_filename, 'w') as csv_file:
                csv_file.write(f"UserName,AWS Access Key ID,AWS Secret Access Key\n")
                csv_file.write(f"{user_name},{user[0]},{user[1]}\n")
            return csv_filename
        return None

    def destroy_user(self, user_name):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Fetch user information from the database
            cursor.execute("SELECT user_id, bucket_name FROM users WHERE user_name=? AND status='active'", (user_name,))
            row = cursor.fetchone()

            if row:
                user_id, bucket_name = row

                # Attempt to delete the S3 bucket and its contents
                try:
                    s3_resource = boto3.resource('s3')
                    bucket = s3_resource.Bucket(bucket_name)
                    bucket.objects.all().delete()
                    bucket.delete()
                    print(f"Bucket {bucket_name} deleted successfully.")
                except Exception as e:
                    print(f"Error deleting bucket {bucket_name}: {e}")

                # Attempt to delete the IAM user's access keys
                try:
                    access_keys = self.iam.list_access_keys(UserName=user_name)
                    for access_key in access_keys['AccessKeyMetadata']:
                        self.iam.delete_access_key(UserName=user_name, AccessKeyId=access_key['AccessKeyId'])
                        print(f"Deleted access key {access_key['AccessKeyId']} for user {user_name}.")
                except Exception as e:
                    print(f"Error deleting access keys for user {user_name}: {e}")

                # Attempt to delete IAM user policies
                try:
                    policies = self.iam.list_user_policies(UserName=user_name)
                    for policy_name in policies['PolicyNames']:
                        self.iam.delete_user_policy(UserName=user_name, PolicyName=policy_name)
                        print(f"Deleted policy {policy_name} from user {user_name}.")
                except Exception as e:
                    print(f"Error deleting policies for user {user_name}: {e}")

                # Attempt to delete the IAM user
                try:
                    self.iam.delete_user(UserName=user_name)
                    print(f"User {user_name} deleted successfully.")
                except Exception as e:
                    print(f"Error deleting user {user_name}: {e}")

                # Update the status in the database to 'disabled'
                cursor.execute("UPDATE users SET status='disabled' WHERE user_name=?", (user_name,))
                conn.commit()
                print(f"User {user_name} status updated to 'disabled' in the database.")
            else:
                print(f"User {user_name} not found or already disabled.")
        except Exception as e:
            print(f"An error occurred during user deletion: {e}")
        finally:
            conn.close()
