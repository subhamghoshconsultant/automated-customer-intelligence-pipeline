import json
import boto3
import csv
import io

# Initialize AWS Service Clients
s3_client = boto3.client('s3')
pinpoint_client = boto3.client('pinpoint')

# Application Configuration (Replace with your actual AWS IDs)
PINPOINT_APP_ID = "YOUR_PINPOINT_PROJECT_ID"
CHURN_THRESHOLD = 0.70  # Trigger action if churn risk is greater than 70%

def lambda_handler(event, context):
    """
    Triggered when SageMaker Canvas drops a batch prediction CSV into the S3 bucket.
    Parses the file and triggers personalized retention campaigns via Amazon Pinpoint.
    """
    # 1. Parse bucket and file details from the S3 Event Trigger
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    
    print(f"Processing new SageMaker predictions from: s3://{bucket_name}/{file_key}")
    
    try:
        # 2. Fetch the prediction file from S3
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        csv_content = s3_object['Body'].read().decode('utf-8')
        
        # 3. Process the CSV data
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        for row in csv_reader:
            # Expected CSV columns from SageMaker Canvas output: customer_id, phone, email, churn_probability
            customer_id = row.get('customer_id')
            phone_number = row.get('phone')
            email_address = row.get('email')
            churn_risk = float(row.get('churn_probability', 0.0))
            
            # 4. Filter for high-risk customers needing immediate retention offers
            if churn_risk >= CHURN_THRESHOLD:
                print(f"High Churn Risk Detected ({churn_risk*100}%): Sending offer to Customer {customer_id}")
                
                # 5. Dispatch targeted promotional offer via Amazon Pinpoint
                send_retention_offer(customer_id, phone_number, email_address)
                
        return {
            'statusCode': 200,
            'body': json.dumps('Customer intelligence pipeline executed successfully.')
        }
        
    except Exception as e:
        print(f"Error executing pipeline: {str(e)}")
        raise e

def send_retention_offer(customer_id, phone, email):
    """
    Helper function to send SMS and Email communications using Amazon Pinpoint.
    """
    try:
        response = pinpoint_client.send_messages(
            ApplicationId=PINPOINT_APP_ID,
            MessageRequest={
                'Addresses': {
                    phone: {'ChannelType': 'SMS'}
                },
                'MessageConfiguration': {
                    'SMSMessage': {
                        'Body': "We miss you! Use code 'LOYAL20' to get 20% off your next package renewal.",
                        'MessageType': 'TRANSACTIONAL'
                    }
                }
            }
        )
        return response
    except Exception as e:
        print(f"Failed to send Pinpoint message to {customer_id}: {str(e)}")
        return None
