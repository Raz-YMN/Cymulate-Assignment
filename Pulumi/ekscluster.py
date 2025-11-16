from pulumi_aws import iam, eks, ec2
from vpc import Vpc

class EksCluster:
    def __init__(self,
                 name: str,
                 role: iam.Role,
                 vpc: Vpc,
                 tags: dict[str, str] = None
                 ):
        self._name = name
        self._role = role
        self._vpc = vpc
        self._tags = tags or {}

        eks.Cluster(name, role_arn=role.arn, tags={
            "Name": name,
            **self._tags
        },
        vpc_config=eks.ClusterVpcConfigArgs(
            public_access_cidrs=["0.0.0.0/0"],
            security_group_ids=[vpc.sg.id],
            subnet_ids=vpc.private_subnet_ids,
        ))

    @property
    def name(self):
        return self._name

    @property
    def role(self):
        return self._role

    @property
    def vpc(self):
        return self._vpc

    @property
    def tags(self):
        return self._tags