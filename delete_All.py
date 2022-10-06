#!/usr/bin/env python3
import sys
import boto3
 # list and terminate all instances
ec2 = boto3.resource('ec2')
instance_list = ec2.instances.all()
print('Terminating all instances...')
for instance in instance_list:
    print('Terminating instance: ' + instance.id)
    instance.terminate()
print('All instances successfully terminated.')

exec(open("delete_buckets.py").read())

# ec2 = boto3.resource('ec2')
# for instance_id in sys.argv[1:]:
#     instance = ec2.Instance(instance_id)
#     response = instance.terminate()
#     print (response)
