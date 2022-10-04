from hashlib import new;
import boto3;

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
    print('Instance created successfully!') 

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