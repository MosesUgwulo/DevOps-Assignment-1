import boto3
import subprocess
from os import system

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

# get instance by id
instance = ec2.Instance('i-03244b35048e81c1c')
ip_address = instance.public_ip_address


system("chmod 400 MosesKeyPair.pem")
system(f"scp -o StrictHostKeyChecking=no -i MosesKeyPair.pem monitor.sh ec2-user@{ip_address}:.")
system(f"ssh -i MosesKeyPair.pem ec2-user@{ip_address} 'chmod 700 monitor.sh'")
system(f"ssh -i MosesKeyPair.pem ec2-user@{ip_address} './monitor.sh'")
system(f"ssh -i MosesKeyPair.pem ec2-user@{ip_address} 'ls -l'")