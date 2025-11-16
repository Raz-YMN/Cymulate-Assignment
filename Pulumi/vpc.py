from pulumi_aws import ec2, get_availability_zones, rds

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

        # NAT for private subnets
        self._eip = ec2.Eip(f"{name}-nat-eip", vpc=True)
        self._nat_gateway = None

        zones = get_availability_zones()
        self._public_subnet_ids = []
        self._private_subnet_ids = []

        for i, zone in enumerate(zones.names):
            public_subnet = ec2.Subnet(
                f"{name}-public-{zone}",
                vpc_id=self._vpc.id,
                cidr_block=f"10.100.{i}.0/24",
                availability_zone=zone,
                map_public_ip_on_launch=True,
                tags={"Name": f"{name}-public-{zone}", **self._tags},
            )
            self._public_subnet_ids.append(public_subnet.id)

            private_subnet = ec2.Subnet(
                f"{name}-private-{zone}",
                vpc_id=self._vpc.id,
                cidr_block=f"10.100.{i + 100}.0/24",
                availability_zone=zone,
                map_public_ip_on_launch=False,
                tags={"Name": f"{name}-private-{zone}", **self._tags},
            )
            self._private_subnet_ids.append(private_subnet.id)

        # Create NAT gateway on first public subnet
        self._nat_gateway = ec2.NatGateway(
            f"{name}-nat",
            allocation_id=self._eip.id,
            subnet_id=self._public_subnet_ids[0],
            tags={"Name": f"{name}-nat", **self._tags}
        )

        self._public_rt = ec2.RouteTable(
            f"{name}-public-rt",
            vpc_id=self._vpc.id,
            routes=[ec2.RouteTableRouteArgs(
                cidr_block="0.0.0.0/0",
                gateway_id=self._igw.id
            )],
            tags={"Name": f"{name}-public-rt", **self._tags}
        )

        self._private_rt = ec2.RouteTable(
            f"{name}-private-rt",
            vpc_id=self._vpc.id,
            routes=[ec2.RouteTableRouteArgs(
                cidr_block="0.0.0.0/0",
                nat_gateway_id=self._nat_gateway.id
            )],
            tags={"Name": f"{name}-private-rt", **self._tags}
        )

        for public_subnet in self._public_subnet_ids:
            ec2.RouteTableAssociation(
                f"{name}-public-rta-{public_subnet}",
                subnet_id=public_subnet,
                route_table_id=self._public_rt.id
            )

        for private_subnet in self._private_subnet_ids:
            ec2.RouteTableAssociation(
                f"{name}-private-rta-{private_subnet}",
                subnet_id=private_subnet,
                route_table_id=self._private_rt.id
            )

        self._security_group = ec2.SecurityGroup(
            f"{name}-sg",
            vpc_id=self._vpc.id,
            description="Allow all HTTP(s) traffic to EKS Cluster",
            tags={
                "Name": f"{name}-eks-sg",
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

        self._private_subnet_group = rds.SubnetGroup(
            f"{name}-db-subnets",
            subnet_ids=self._private_subnet_ids,
            tags={"Name": f"{name}-db-subnets", **self._tags}
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
    def public_rt(self):
        return self._public_rt

    @property
    def private_rt(self):
        return self._private_rt

    @property
    def private_subnet_group(self):
        return self._private_subnet_group

    @property
    def public_subnet_ids(self):
        return self._public_subnet_ids

    @property
    def private_subnet_ids(self):
        return self._private_subnet_ids

    @property
    def sg(self):
        return self._security_group