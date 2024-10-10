from aws_cdk import App, CfnOutput, Environment, Stack
from aws_cdk.aws_ec2 import (
    SubnetSelection, SubnetType, Vpc, SecurityGroup, Peer, Port,
    Instance, InstanceType, MachineImage, BastionHostLinux
)
from aws_cdk.aws_elasticache import CfnCacheCluster, CfnSubnetGroup
from constructs import Construct


app = App()


US_WEST_2 = Environment(
    account='618537831167',
    region='us-west-2',
)


class RedisStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = Vpc.from_lookup(
            self,
            'VPC',
            vpc_id='vpc-ea3b6581'
        )

        # Create a security group for Redis
        redis_sg = SecurityGroup(
            self,
            'RedisSG',
            vpc=vpc,
            description='Security group for Redis cluster',
            allow_all_outbound=False
        )

        # Create a security group for the bastion host
        bastion_sg = SecurityGroup(
            self,
            'BastionSG',
            vpc=vpc,
            description='Security group for Bastion Host',
            allow_all_outbound=True
        )

        # Allow SSH access to the bastion host
        bastion_sg.add_ingress_rule(
            peer=Peer.any_ipv4(),
            connection=Port.tcp(22),
            description='Allow SSH access'
        )

        # Allow Redis access from the bastion host
        redis_sg.add_ingress_rule(
            peer=bastion_sg,
            connection=Port.tcp(6379),
            description='Allow Redis access from Bastion'
        )

        # Create a subnet group using public subnets
        subnet_group = CfnSubnetGroup(
            self,
            'RedisSubnetGroup',
            description='Subnet group for Redis cluster',
            subnet_ids=vpc.select_subnets(subnet_type=SubnetType.PUBLIC).subnet_ids
        )

        cache_cluster = CfnCacheCluster(
            self,
            'CacheCluster',
            num_cache_nodes=1,
            engine='redis',
            engine_version='7.1',
            cache_node_type='cache.t4g.small',
            cache_subnet_group_name=subnet_group.ref,
            vpc_security_group_ids=[redis_sg.security_group_id]
        )

        # Create a bastion host
        bastion_host = BastionHostLinux(
            self,
            'BastionHost',
            vpc=vpc,
            subnet_selection=SubnetSelection(subnet_type=SubnetType.PUBLIC),
            security_group=bastion_sg,
            instance_name='Redis-Bastion',
        )

        # Output the Redis endpoint
        CfnOutput(
            self,
            'RedisEndpoint',
            value=cache_cluster.attr_redis_endpoint_address,
            description='Redis Cluster Endpoint Address'
        )

        CfnOutput(
            self,
            'RedisPort',
            value=cache_cluster.attr_redis_endpoint_port,
            description='Redis Cluster Endpoint Port'
        )

        # Output the bastion host's public IP and public DNS name
        CfnOutput(
            self,
            'BastionPublicIP',
            value=bastion_host.instance_public_ip,
            description='Public IP address of the Bastion Host'
        )

        CfnOutput(
            self,
            'BastionPublicDNS',
            value=bastion_host.instance_public_dns_name,
            description='Public DNS name of the Bastion Host'
        )


RedisStack(
    app,
    'RedisStack',
    env=US_WEST_2,
)


app.synth()
