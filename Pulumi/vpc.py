from pulumi_aws import ec2, get_availability_zones

class Vpc:
    def __init__(self,
                 name: str,
                 cidr_block: str,
                 tags: dict[str, str] = None):

        self._name = name
        self._cidr_block = cidr_block
        self._tags = tags or {}

        self._vpc = ec2.Vpc(
            name,
            cidr_block=self._cidr_block,
            tags={
                "Name": name,
                **self._tags
            }
        )

        self._igw = ec2.InternetGateway(
            f"{name}-igw",
            vpc_id=self._vpc.id,
            tags={
                "Name": f"{name}-igw",
                **self._tags
            }
        )

        self._route_table = ec2.RouteTable(
            f"{name}-rt",
            vpc_id=self._vpc.id,
            routes=[
                ec2.RouteTableRouteArgs(
                    cidr_block="0.0.0.0/0",
                    gateway_id=self._igw.id,
                )
            ],
            tags={
                "Name": f"{name}-rt",
                **self._tags
            }
        )

        zones = get_availability_zones()
        self._subnet_ids = []

        for i, zone in enumerate(zones.names):
            subnet = ec2.Subnet(
                f"{name}-subnet-{zone}",
                vpc_id=self._vpc.id,
                availability_zone=zone,
                cidr_block=f"10.100.{i}.0/24",
                map_public_ip_on_launch=True,
                assign_ipv6_address_on_creation=False,
                tags={"Name": f"{name}-{zone}-subnet",
                      **self._tags
                      },
            )

            # Associate subnet with rt
            ec2.RouteTableAssociation(
                f"{name}-rta-{zone}",
                route_table_id=self._route_table.id,
                subnet_id=subnet.id,
            )

            self._subnet_ids.append(subnet.id)

        self._security_group = ec2.SecurityGroup(
            f"{name}-sg",
            vpc_id=self._vpc.id,
            description="Allow all HTTP(s) traffic to EKS Cluster",
            tags={"Name": f"{name}-eks-sg",
                  **self._tags
                  },
            ingress=[
                ec2.SecurityGroupIngressArgs(
                    cidr_blocks=["0.0.0.0/0"],
                    from_port=443,
                    to_port=443,
                    protocol="tcp",
                    description="Allow pods to communicate with the cluster API server.",
                ),
                ec2.SecurityGroupIngressArgs(
                    cidr_blocks=["0.0.0.0/0"],
                    from_port=80,
                    to_port=80,
                    protocol="tcp",
                    description="Allow internet access to pods.",
                ),
            ],
            egress=[
                ec2.SecurityGroupEgressArgs(
                    cidr_blocks=["0.0.0.0/0"],
                    from_port=0,
                    to_port=0,
                    protocol="-1",
                    description="Allow outbound traffic.",
                )
            ],
        )

    @property
    def id(self):
        return self._vpc.id

    @property
    def vpc(self):
        return self._vpc

    @property
    def name(self):
        return self._name

    @property
    def cidr_blocks(self):
        return self._cidr_block

    @property
    def tags(self):
        return self._tags

    @property
    def igw(self):
        return self._igw

    @property
    def rt(self):
        return self._route_table

    @property
    def subnet_ids(self):
        return self._subnet_ids

    @property
    def sg(self):
        return self._security_group