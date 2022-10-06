from cgitb import html
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
        KeyName='MosesKeyPair' # Key pair name
    )
    

except Exception as e:
    print("An error occured while creating EC2 instance...")
    print(e)
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

    # stop the instance after its running
    print('Stopping instance to add meta data...')
    new_instance[0].stop()
    new_instance[0].wait_until_stopped()
    new_instance[0].reload()
    print('[Current state: ' + new_instance[0].state['Name'] + ']\n')

    # edit the instance meta data
    print('Adding meta data...')
    new_instance[0].modify_attribute(
        UserData={
            'Value': '''#!/bin/bash
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
            ''' 
        }
    )
    print('Meta data successfully added.\n')
# 169.254.169.254/latest/meta-data/instance-id
    # start the instance
    print('Starting instance...')
    new_instance[0].start()
    new_instance[0].wait_until_running()
    new_instance[0].reload()
    print('[Current state: ' + new_instance[0].state['Name'] + ']\n')

    print("Waiting to be redirected to the webserver...") # Print message
    time.sleep(15) # Wait 15 seconds
    print("Opening web browser to : " + new_instance[0].public_ip_address) # Print message

    webbrowser.open('http://' + new_instance[0].public_ip_address) # Open web browser to instance public IP

try:
    # create an S3 bucket
    print('\nCreating S3 bucket...')
    s3 = boto3.resource('s3')

    # generate 6 random characters
    def randomString(stringLength=6):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))

    new_bucket = s3.create_bucket(Bucket='mugwulo-' + randomString(),
        ACL='public-read',
    ) 
    
    new_bucket.wait_until_exists() # wait until bucket exists
    print('Bucket successfully created: ' + new_bucket.name) # Print bucket name
    print('\nEnabling static website hosting...') # enable static website hosting

    new_bucket.Acl().put(ACL='public-read') # Make bucket public

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

    s3_client = boto3.client('s3') # Create S3 client

    print('Uploading files to S3 bucket...') # Print message
    s3_client.upload_file('index.html', new_bucket.name, 'index.html',
        ExtraArgs={
            'ContentType': 'text/html',
            'ACL': 'public-read',
        } 
    )

    s3_client.upload_file('script.js', new_bucket.name, 'script.js',
        ExtraArgs={
            'ContentType': 'text/javascript',
            'ACL': 'public-read',
        }
    )

    s3_client.upload_file('style.css', new_bucket.name, 'style.css',
        ExtraArgs={
            'ContentType': 'text/css',
            'ACL': 'public-read',
        }
    )


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

    # set permissions for the files
    print('\nSetting permissions for files...') # Print message
    new_bucket.Object('index.html').Acl().put(ACL='public-read') # Set index.html permissions
    new_bucket.Object('style.css').Acl().put(ACL='public-read') # Set style.css permissions
    new_bucket.Object('script.js').Acl().put(ACL='public-read') # Set script.js permissions
    s3_client.put_object_acl(ACL='public-read', Bucket=new_bucket.name, Key='logo.jpg') # Set logo.jpg permissions
    print('Permissions successfully set.') # Print message


    # put the image into the index.html file
    print('\nAdding image to index.html...') # Print message
    index_html = new_bucket.Object('index.html').get()['Body'].read().decode('utf-8') # Get index.html file
    index_html1 = index_html.replace('logo.jpg', 'https://' + new_bucket.name + '.s3.amazonaws.com/logo.jpg') # Replace logo.jpg with url
    new_bucket.Object('index.html').put(Body=index_html1) # Put index.html file
    print('Image successfully added.') # Print message

    print('\nOpening web browser to : ' + new_bucket.name + '.s3-website-us-east-1.amazonaws.com') # Print message
    webbrowser.open('http://' + new_bucket.name + '.s3-website-us-east-1.amazonaws.com') # Open web browser to bucket website

except Exception as e:
    print("An error occured while creating S3 bucket...")
    print(e)
    print("Exiting...")