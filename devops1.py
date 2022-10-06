from hashlib import new
import json
import time
import boto3
import webbrowser

# Create EC2 client
ec2 = boto3.resource('ec2')

# Create a new EC2 instance
try:
    print('\nCreating EC2 instance...')

    new_instance = ec2.create_instances(
        ImageId='ami-026b57f3c383c2eec', # Amazon Linux 2 AMI (HVM), SSD Volume Type
        MinCount=1, # Minimum number of instances to launch
        MaxCount=1, # Maximum number of instances to launch
        InstanceType='t2.nano', # Instance type
        TagSpecifications=[ # Tag the instance
            {'ResourceType': 'instance', # Resource type is an instance
                'Tags': [ 
                    {'Key': 'Name', 'Value': 'DevOps1'}, # Tag name is DevOps1
                ]   
            },
        ],
        SecurityGroupIds=[
            'sg-0f7406fb4f316a5a0' # Security group ID
        ],
        KeyName='MosesKeyPair', # Key pair name
        UserData='''#!/bin/bash 
            sudo yum install httpd -y
            sudo systemctl enable httpd
            sudo systemctl start httpd
        ''' # User data script
    )
    

except:
    print("An error occured while creating EC2 instance...")
    print("Exiting...")

else:
    print('\nInstance successfully created:' + # Print instance ID
    '\n[ID: ' + new_instance[0].id + ']' + 
    '\n[Type: ' + new_instance[0].instance_type + ']' + # Print instance type
    '\n[Current state: ' + new_instance[0].state['Name'] + ']') # Print instance state
    new_instance[0].wait_until_running() # Wait until instance is running
    new_instance[0].reload() # Reload instance attributes
    print('[Current state: ' + new_instance[0].state['Name'] + ']' +
    '\n[Public IP: ' + new_instance[0].public_ip_address + ']\n') # Print instance public IP
    print("Waiting to be redirected to the webserver...") # Print message
    time.sleep(15) # Wait 15 seconds
    print("Opening web browser to : " + new_instance[0].public_ip_address) # Print message
    webbrowser.open('http://' + new_instance[0].public_ip_address) # Open web browser to instance public IP

try:
    # create an S3 bucket
    print('\nCreating S3 bucket...')
    s3 = boto3.resource('s3')
    new_bucket = s3.create_bucket(Bucket='bucket-' + str(time.time())) # Create bucket with unique name
    new_bucket.wait_until_exists() # wait until bucket exists
    print('Bucket successfully created: ' + new_bucket.name) # Print bucket name
    print('\nEnabling static website hosting...') # enable static website hosting
    website_configuration = {
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    }
    bucket_website = s3.BucketWebsite(new_bucket.name) # Create bucket website
    bucket_website.put(WebsiteConfiguration=website_configuration) # Put website configuration
    print('Static website hosting successfully enabled.') # Print message

    print('\nUploading index.html to S3 bucket...') # Print message
    new_bucket.upload_file('index.html', 'index.html') # Upload index.html to bucket
    print('index.html successfully uploaded to S3 bucket.') # Print message

    # uploading style.css to S3 bucket
    print('\nUploading style.css to S3 bucket...') # Print message
    new_bucket.upload_file('style.css', 'style.css') # Upload style.css to bucket
    print('style.css successfully uploaded to S3 bucket.') # Print message

    # uploading script.js to S3 bucket
    print('\nUploading script.js to S3 bucket...') # Print message
    new_bucket.upload_file('script.js', 'script.js') # Upload script.js to bucket
    print('script.js successfully uploaded to S3 bucket.') # Print message

    # bucket policy must allow access to the s3:GetObject action on the bucket
    print('\nCreating bucket policy...') # Print message
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [{
            'Sid': 'PublicReadGetObject',
            'Effect': 'Allow',
            'Principal': '*',
            'Action': ['s3:GetObject'],
            'Resource': ["arn:aws:s3:::" + new_bucket.name + "/*"]
        }]
    }
    bucket_policy = json.dumps(bucket_policy) # Convert bucket policy to JSON
    new_bucket.Policy().put(Policy=bucket_policy) # Put bucket policy
    print('Bucket policy successfully created.') # Print message

    # set permissions for the files
    print('\nSetting permissions for files...') # Print message
    new_bucket.Object('index.html').Acl().put(ACL='public-read') # Set index.html permissions
    new_bucket.Object('style.css').Acl().put(ACL='public-read') # Set style.css permissions
    new_bucket.Object('script.js').Acl().put(ACL='public-read') # Set script.js permissions
    print('Permissions successfully set.') # Print message
    

    print('\nOpening web browser to : ' + new_bucket.name + '.s3-website-us-east-1.amazonaws.com') # Print message
    webbrowser.open('http://' + new_bucket.name + '.s3-website-us-east-1.amazonaws.com') # Open web browser to bucket website



except:
    print("An error occured while terminating S3 bucket...")
    print("Exiting...")