from ekscluster import EksCluster
from vpc import Vpc
from iam import eks_role, ec2_role
from pulumi_aws import eks

vpc = Vpc("crypto-vpc", "10.100.0.0/16")

eks_cluster = EksCluster("crypto-eks", eks_role, vpc)

eks_node_group = eks.NodeGroup(
    "crypto-nodegroup",
    cluster_name=eks_cluster.name,
    node_group_name="crypto-nodegroup",
    node_role_arn=ec2_role.arn,
    subnet_ids=vpc.subnet_ids,
    tags={
        "Name": "crypto-nodegroup",
    },
    scaling_config=eks.NodeGroupScalingConfigArgs(
        desired_size=2,
        max_size=2,
        min_size=1,
    ),
)