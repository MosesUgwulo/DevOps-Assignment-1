from cgitb import html
from os import system
import time
import boto3
import webbrowser
import random
import string
import urllib

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
        UserData="""#!/bin/bash
            yum install httpd -y
            systemctl enable httpd
            systemctl start httpd
            echo "Content-type: text/html"
            echo '<html>' > index.html
            echo '<head>' >> index.html
            echo '<title>DevOps1</title>' >> index.html
            echo '</head>' >> index.html
            echo '<body>' >> index.html
            echo '<h1>DevOps1</h1>' >> index.html
        
            echo '<br>' >> index.html
            echo '<h1>' >> index.html
            echo 'Instance ID: ' >> index.html
            echo $(curl http://169.254.169.254/latest/meta-data/instance-id) >> index.html
            echo '</h1>' >> index.html

            echo '<br>' >> index.html
            echo '<h1>' >> index.html
            echo 'AMI ID: ' >> index.html
            echo $(curl http://169.254.169.254/latest/meta-data/ami-id) >> index.html
            echo '</h1>' >> index.html
            
            echo '<br>' >> index.html
            echo '<h1>' >> index.html
            echo 'Instance Type: ' >> index.html 
            echo $(curl http://169.254.169.254/latest/meta-data/instance-type) >> index.html
            echo '</h1>' >> index.html

            echo '<br>' >> index.html
            echo '<img src="http://devops.witdemo.net/logo.jpg">' >> index.html

            echo '</body>' >> index.html
            echo '</html>' >> index.html
            cp index.html /var/www/html/index.html
        """ 
    )
    

except Exception as e:
    print("An error occured while creating EC2 instance, check error.txt or console for more details")
    print(e)
    errorfile = open("error.log", "w")
    errorfile.write(str(e))
    errorfile.close()
    print("Error file created")

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
    time.sleep(20) # Wait 15 seconds
    print("Opening web browser to : " + new_instance[0].public_ip_address) # Print message

    webbrowser.open('http://' + new_instance[0].public_ip_address) # Open web browser to instance public IP


    # generate 6 random characters
def randomString(stringLength=6):
    letters = string.ascii_lowercase
    numbers = string.digits
    return ''.join(random.choice(letters + numbers) for i in range(stringLength))

try:
    # create an S3 bucket
    print('\nCreating S3 bucket...')
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3') # Create S3 client

    new_bucket = s3.create_bucket(
        Bucket='mugwulo-' + randomString(),
        ACL='public-read',
    ) 
    
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


    # download a file from a url
    print('\nDownloading logo from url...') # Print message
    url = 'http://devops.witdemo.net/logo.jpg' # Set url
    urllib.request.urlretrieve(url, 'logo.jpg') # Download file from url
    print('File successfully downloaded.') # Print message

    s3_client.upload_file('logo.jpg', new_bucket.name, 'logo.jpg',
        ExtraArgs={
            'ContentType': 'image/jpg',
            'ACL': 'public-read',
        }
    )

    print('Uploading files to S3 bucket...') # Print message
    s3_client.upload_file('index.html', new_bucket.name, 'index.html',
        ExtraArgs={
            'ContentType': 'text/html',
            'ACL': 'public-read',
        } 
    )

    print('\nOpening web browser to : ' + new_bucket.name + '.s3-website-us-east-1.amazonaws.com') # Print message
    webbrowser.open('http://' + new_bucket.name + '.s3-website-us-east-1.amazonaws.com') # Open web browser to bucket website

except Exception as e:
    print("An error occured while creating S3 bucket, check error.txt or console for more details")
    print(e)
    errorfile = open("error.log", "w")
    errorfile.write(str(e))
    errorfile.close()
    print("Error file created")

try:
    # write both URLs to a file
    print('\nWriting URLs to file...')
    file = open('mugwulo.txt', 'w')
    file.write('Instance URL: http://' + new_instance[0].public_ip_address + '\nS3 Bucket URL: http://' + new_bucket.name + '.s3-website-us-east-1.amazonaws.com')
    file.close()
    print('File successfully written.\n')

except Exception as e:
    print("An error occured while writing URLs to file, check error.txt or console for more details")
    print(e)
    errorfile = open("error.log", "w")
    errorfile.write(str(e))
    errorfile.close()
    print("Error file created")

