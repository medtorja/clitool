#!/usr/bin/env python

import argparse
import json
import boto3

DEF_ENDPOINT_URL="http://localhost"
DEF_ENDPOINT_URL_S3= DEF_ENDPOINT_URL + ":4572"
DEF_ENDPOINT_URL_EC2= DEF_ENDPOINT_URL + ":4597"
DEF_ENDPOINT_URL_SQS= DEF_ENDPOINT_URL + ":4576"
DEF_REGION_NAME="us-east-1"


def create_stack(data, stackname):

    for p in data:

        if  (p['type'] == 's3'):
            print('creating buckets...')
            create_bucket(p['properties'], stackname)
            print('buckets created')
            
        elif (p['type'] == 'ec2'):
            print('creating instances...')
            create_instance(p['properties'], stackname)
            print('instances created')

        elif (p['type'] == 'sqs'):
            print('creating queues...')
            create_queue(p['properties'], stackname)
            print('queues created')

            
def list_stack(stackname):

    instances = list_instances(stackname)
    print("instances belonging to", stackname, "are: ", instances)

    buckets = list_buckets(stackname)
    print("buckets belonging to", stackname, "are: ", buckets)

    queues =  list_queues(stackname)
    print("queue belonging to", stackname, "are: ", queues)


def delete_stack(stackname):
    
    instances = list_instances(stackname)
    client = boto3.client('ec2', endpoint_url=DEF_ENDPOINT_URL_EC2,
                                    region_name=DEF_REGION_NAME)
    print('terminating instances...')
    client.terminate_instances(InstanceIds=instances)
    print('instances terminated')

    buckets = list_buckets(stackname)
    client = boto3.client('s3', endpoint_url=DEF_ENDPOINT_URL_S3,
                                    region_name=DEF_REGION_NAME)
    print('deleting buckets...')
    for bucket in buckets:
        client.delete_bucket(Bucket=bucket)
    print('buckets deleted')
    
    queues = list_queues(stackname)
    client = boto3.client('sqs', endpoint_url=DEF_ENDPOINT_URL_SQS,
                                region_name=DEF_REGION_NAME)
    print('deleting queues...')
    for queue in queues:
        client.delete_queue(QueueUrl=queue)
    print('queues deleted')


#######################
#   LIST FUNCTIONS
#######################


def list_instances(stackname):
    client = boto3.client('ec2', endpoint_url=DEF_ENDPOINT_URL_EC2,
                                    region_name=DEF_REGION_NAME)
    #I just want the running machines with the tag, not the terminated
    custom_filter = [{
        'Name':'tag:stack', 
        'Values': [stackname]},
        { 
        'Name': 'instance-state-name',
        'Values': ['running']}] 

    response = client.describe_instances(Filters=custom_filter)

    matching_instances = []

    if len(response['Reservations']) > 0:
        for r in response['Reservations']:
            matching_instances.append(r['Instances'][0]['InstanceId'])  
            
    return matching_instances

    
def list_buckets(stackname):

    client = boto3.client('s3', endpoint_url=DEF_ENDPOINT_URL_S3,
                                region_name=DEF_REGION_NAME)
    buckets = client.list_buckets()['Buckets']
    matching_buckets = []

    for idx, bucket in enumerate(buckets):
        tags = client.get_bucket_tagging(Bucket=bucket['Name'])['TagSet']
        for tag in tags:
            if tag['Key'] == 'stack' and tag['Value'] == stackname:
                matching_buckets.append(bucket['Name'])

    return matching_buckets


def list_queues(stackname):

    client = boto3.client('sqs', endpoint_url=DEF_ENDPOINT_URL_SQS,
                                        region_name=DEF_REGION_NAME)
    queues = client.list_queues()
    matching_queues = []
    queueUrls = queues.get('QueueUrls')

    if queueUrls:
        for queueUrl in queueUrls:
            tags = client.list_queue_tags(QueueUrl=queueUrl)['Tags']
            if 'stack' in tags and tags['stack'] == stackname:
                matching_queues.append(queueUrl)

    return matching_queues


#######################
#   UPDATE FUNCTIONS
#######################


def update_stack (data, stackname):
    for p in data:
        if  (p['type'] == 's3'):
            if not bucket_exists(p['properties']['bucket-name'], stackname):
                print('updating buckets...')
                create_bucket(p['properties'], stackname)
                print('buckets updated...')
            
        elif (p['type'] == 'ec2'):
            if not instance_exists(p['properties']['name'], stackname):
                print('updating instances...')
                create_instance(p['properties'], stackname)
                print('instances updated')

        elif (p['type'] == 'sqs'):
            if not queue_exists(p['properties']['name'], stackname):
                print('updating queues...')
                create_queue(p['properties'], stackname)
                print('queues updated')
    

def instance_exists(instace_name, stackname):
    client = boto3.client('ec2', endpoint_url=DEF_ENDPOINT_URL_EC2,
                                    region_name=DEF_REGION_NAME)

    #I just want the running machines with the tag, not the terminated
    custom_filter = [{
                    'Name':'tag:stack', 
                    'Values': [stackname]},
                    {
                    'Name':'tag:name', 
                    'Values': [instace_name]},
                    { 
                    'Name': 'instance-state-name',
                    'Values': ['running']}] 

    response = client.describe_instances(Filters=custom_filter)
    if len(response['Reservations']) > 0:
        return True
    else:
        return False


def bucket_exists(bucket_name, stackname):
    

    client = boto3.client('s3', endpoint_url=DEF_ENDPOINT_URL_S3,
                                region_name=DEF_REGION_NAME)
    buckets = client.list_buckets()['Buckets']

    for idx, bucket in enumerate(buckets):
        if buckets[0]['Name'] == stackname + '-' + bucket_name: 
            return True

    return False


def queue_exists(queue_name, stackname):

    client = boto3.client('sqs', endpoint_url=DEF_ENDPOINT_URL_SQS,
                                        region_name=DEF_REGION_NAME)

    queues = client.list_queues()

    queueUrls = queues.get('QueueUrls')

    if queueUrls:
        for queueUrl in queueUrls:
            tags = client.list_queue_tags(QueueUrl=queueUrl)['Tags']
            if 'name' in tags and tags['name'] == queue_name:
                return True

    return False


#######################
#   CREATE FUNCTIONS
#######################


def create_bucket(properties, stackname):
    client = boto3.resource('s3', endpoint_url=DEF_ENDPOINT_URL_S3,
                                        region_name=DEF_REGION_NAME)
    client.create_bucket(Bucket=stackname + '-' + properties['bucket-name'])
    bucket_tagging = client.BucketTagging(stackname + '-' +properties['bucket-name'])
    set_tag = bucket_tagging.put(Tagging={'TagSet':[{'Key':'stack', 'Value': stackname},{'Key':'name', 'Value': properties['bucket-name'] }]})
    

def create_instance(properties, stackname):
    client = boto3.resource('ec2', endpoint_url=DEF_ENDPOINT_URL_EC2,
                            region_name=DEF_REGION_NAME)
    instance = client.create_instances(ImageId = "ami-03cf127a",
                            MinCount = 1,
                            MaxCount = 1,
                            InstanceType = properties['type'],
                            BlockDeviceMappings=[{'DeviceName': '/dev/sda1', "Ebs" : {'DeleteOnTermination': True}}]
    )
    client.create_tags(Resources=[instance[0].id], Tags=[{'Key':'stack', 'Value':stackname},
                                                            {'Key':'name', 'Value':properties['name']}])


def create_queue(properties, stackname):
    client = boto3.client('sqs', endpoint_url=DEF_ENDPOINT_URL_SQS,
                                        region_name=DEF_REGION_NAME)
    queue = None
    if (properties['type'] == 'fifo'):
        queue = client.create_queue(QueueName=stackname + "-" + properties['name']+".fifo",
                                        Attributes={'FifoQueue': 'true'})
    else:
        queue = client.create_queue(QueueName=stackname + "-" + properties['name'])
    
    client.tag_queue(QueueUrl=queue['QueueUrl'], Tags={"stack":stackname})
    client.tag_queue(QueueUrl=queue['QueueUrl'], Tags={"name":properties['name']})


############
#   MAIN
############


def main():

    parser = argparse.ArgumentParser(description='create, update or delete aws stacks', 
    usage='python3 cli-tool.py {create [stack-file], update [stack-file], delete, list} --sn/stack-name namestack')
    
    parser.add_argument(
        'action', nargs='*', type=str)
    parser.add_argument(
        '-sn', '--stack_name', required=True, type=str, help='stack name')
    args = parser.parse_args()

    
    if (args.action[0] != 'create' and args.action[0] != 'update' and args.action[0] != 'delete' and args.action[0] != 'list'):
        print ('cli-tool.py: error: The first argument mus be create, update, delete or list')
        exit(0)

    if ((args.action[0] == 'create' or args.action[0] == 'update')and len(args.action) != 2):
        print ('cli-tool.py: error: json file for create or update incorrect')
        exit(0)

    if ((args.action[0] == 'delete' or args.action[0] == 'list') and len(args.action) != 1):
        print ('cli-tool.py: error: delete or list option does not need a file')
        exit(0)

    if args.action[0] == "delete":
        delete_stack (args.stack_name)
        exit(0)

    elif args.action[0] == "list":
        list_stack(args.stack_name)
        exit(0)

    #reading the json
    with open(args.action[1]) as json_file:
        data = []
        try:
            data = json.load(json_file)
        except ValueError as e:
            print ('invalid json: %s' % e)

    if args.action[0] == "create":
        create_stack(data, args.stack_name)
        exit(0)
    elif args.action[0] == "update":
        update_stack(data, args.stack_name)
        exit(0)


if __name__ == "__main__":
    main()
