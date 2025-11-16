from pulumi_aws import rds

class RdsBase:
    def __init__(self, name: str, tags: dict[str, str] = None):
        self.name = name
        self.tags = tags or {}

    def _format_tags(self):
        return {
            "Name": self.name,
            **self.tags,
        }

class RdsInstance(RdsBase):
    def __init__(self,
                 name: str,
                 instance_class: str,
                 engine: str,
                 engine_version: str,
                 username: str,
                 password: str,
                 db_name: str,
                 db_subnet_group_name: str,
                 allocated_storage: int = 10,
                 tags: dict[str, str] = None):

        super().__init__(name, tags)

        self.instance = rds.Instance(
            name,
            allocated_storage=allocated_storage,
            db_name=db_name,
            instance_class=instance_class,
            engine=engine,
            engine_version=engine_version,
            username=username,
            password=password,
            db_subnet_group_name=db_subnet_group_name,
            skip_final_snapshot=True,
            tags=self._format_tags(),
        )

class RdsAuroraCluster(RdsBase):
    def __init__(self,
                 name: str,
                 engine: str,
                 engine_version: str,
                 username: str,
                 password: str,
                 db_name: str,
                 db_subnet_group_name: str,
                 availability_zones=None,
                 allocated_storage: int = 10,
                 tags: dict[str, str] = None):

        super().__init__(name, tags)

        self.cluster = rds.Cluster(
            name,
            allocated_storage=allocated_storage,
            engine=engine,
            engine_version=engine_version,
            master_username=username,
            master_password=password,
            database_name=db_name,
            db_subnet_group_name=db_subnet_group_name,
            availability_zones=availability_zones,
            backup_retention_period=7,
            tags=self._format_tags(),
        )