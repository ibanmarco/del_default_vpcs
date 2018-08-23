import boto3
import sys

def scan_region(region_name, profile):

    try:
        char_len = len(region_name) + 12
        print("\nChecking in {}".format(region_name))
        print("*" * char_len)
        ec2 = boto3.client('ec2', region_name=region_name)

        response = ec2.describe_vpcs(
            Filters=[
                {
                    'Name': 'isDefault',
                    'Values': ['true']
                }
            ]
        )

        if len(response['Vpcs']) is 0:
            print("No default VPC found in {}".format(region_name))
        else:
            vpc_id = response['Vpcs'][0]['VpcId']
            print("Default {0} found in {1}".format(vpc_id, region_name))

            del_subnet(vpc_id, ec2)
            del_igw(vpc_id, ec2)
            del_vpc(vpc_id, ec2)

    except Exception as e:
        profiles = boto3.Session().available_profiles
        print("{}. The profiles you have available are:".format(e))
        print(" ".join(str(item) for item in profiles))


def del_subnet(vpc_id, ec2):

    response = ec2.describe_subnets(
        Filters=[
            {
                'Name': 'vpc-id',
                'Values': [vpc_id]
            }
        ]
    )

    for subnet in response['Subnets']:
        data = ec2.delete_subnet(SubnetId=subnet['SubnetId'])
        print("{0} found in {1} in {2}.... subnet removed !!".format(subnet['SubnetId'], vpc_id, region_name))


def del_igw(vpc_id, ec2):

    response = ec2.describe_internet_gateways(
        Filters=[
            {
                'Name': 'attachment.vpc-id',
                'Values': [vpc_id]
            }
        ]
    )

    if len(response['InternetGateways']) is 0:
        print("No IGW found attached to {}".format(vpc_id))
    else:
        igw_id = response['InternetGateways'][0]['InternetGatewayId']

        data = ec2.detach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
        )

        data = ec2.delete_internet_gateway(
            InternetGatewayId=igw_id
        )

        print("{} found and removed !!".format(response['InternetGateways'][0]['InternetGatewayId']))


def del_vpc(vpc_id, ec2):

    response = ec2.delete_vpc(
        VpcId=vpc_id
    )

    print("Default VPC removed in {}".format(region_name))


try:
    profile = sys.argv[1]
    boto3.setup_default_session(profile_name=profile)
    ec2 = boto3.client('ec2')
    regions = ec2.describe_regions()

    for region in regions['Regions']:
        scan_region(region['RegionName'], profile)

except Exception as e:
    profiles = boto3.Session().available_profiles
    print("{}. The profiles you have available are:".format(e))
    print(" ".join(str(item) for item in profiles))
