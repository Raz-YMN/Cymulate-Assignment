from ekscluster import EksCluster
from vpc import Vpc
from iam import eks_role, ec2_role
from rds import RdsInstance, RdsAuroraCluster
import pulumi_aws as aws

vpc = Vpc("crypto-vpc", "10.100.0.0/16")

eks_cluster = EksCluster("crypto-eks", eks_role, vpc)

eks_node_group = aws.eks.NodeGroup(
    "crypto-nodegroup",
    cluster_name=eks_cluster.name,
    node_group_name="crypto-nodegroup",
    node_role_arn=ec2_role.arn,
    subnet_ids=vpc.private_subnet_ids,
    tags={
        "Name": "crypto-nodegroup",
    },
    scaling_config=aws.eks.NodeGroupScalingConfigArgs(
        desired_size=2,
        max_size=2,
        min_size=1,
    ),
)

rds_instance=RdsInstance(
    name="crypto-rds",
    instance_class=aws.rds.InstanceType.T3_MICRO,
    engine="mysql",
    engine_version="8.0",
    username="admin",
    password="123",
    db_name="crypto-mysql",
    db_subnet_group_name=vpc.private_subnet_group.name
)

rds_aurora=RdsAuroraCluster(
    name="crypto-aurora",
    engine=aws.rds.EngineType.AURORA_MYSQL,
    engine_version="5.7.mysql_aurora.2.03.2",
    username="admin",
    password="123",
    db_name="crypto-aurora",
    db_subnet_group_name=vpc.private_subnet_group.name,
    availability_zones=aws.get_availability_zones(),
)