import json
import boto3

def lambda_handler(event, context):
    
    print("Received ec2 update",event)
    ec2 = boto3.resource("ec2")
    r53 = boto3.client("route53")
    hz_id = "" #Hosted Zone ID from Route53
    domain_name = "" #Your Domain Name

    ec2_update_data = event
    instance_id = ec2_update_data["detail"]["instance-id"]
    instance_state = ec2_update_data["detail"]["state"]
    print("EC2 ID received: ",instance_id)
    print("EC2 State received: ",instance_state)

    if instance_state == "running":
        ec2_instance = ec2.Instance(instance_id)
        ip = (ec2_instance.classic_address).public_ip
        print("Updating IP to ", ip)
        try:
            response = r53.change_resource_record_sets(
                HostedZoneId=hz_id,
                ChangeBatch={
                    'Comment': 'changing to %s' % (ip),
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': domain_name,
                                'Type': 'A',
                                'TTL': 300,
                                'ResourceRecords': [{'Value': ip}]
                            }
                        }]
                })
        except Exception as e:
            print(e)
            
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully updated!')
    }
