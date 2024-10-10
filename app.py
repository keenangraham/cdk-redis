from aws_cdk import App
from aws_cdk import CfnOutput
from aws_cdk import Environment
from aws_cdk import Stack

from aws_cdk.aws_ec2 import SubnetSelection
from aws_cdk.aws_ec2 import SubnetType
from aws_cdk.aws_ec2 import Vpc
from aws_cdk.aws_ec2 import SecurityGroup
from aws_cdk.aws_ec2 import Peer
from aws_cdk.aws_ec2 import Port
from aws_cdk.aws_ec2 import BastionHostLinux

from aws_cdk.aws_elasticache import CfnCacheCluster
from aws_cdk.aws_elasticache import CfnSubnetGroup

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

        redis_sg = SecurityGroup(
            self,
            'RedisSG',
            vpc=vpc,
            description='Security group for Redis cluster',
            allow_all_outbound=False
        )

        bastion_sg = SecurityGroup(
            self,
            'BastionSG',
            vpc=vpc,
            description='Security group for Bastion Host',
            allow_all_outbound=True
        )

        bastion_sg.add_ingress_rule(
            peer=Peer.any_ipv4(),
            connection=Port.tcp(22),
            description='Allow SSH access'
        )

        redis_sg.add_ingress_rule(
            peer=bastion_sg,
            connection=Port.tcp(6379),
            description='Allow Redis access from Bastion'
        )

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

        bastion_host = BastionHostLinux(
            self,
            'BastionHost',
            vpc=vpc,
            subnet_selection=SubnetSelection(subnet_type=SubnetType.PUBLIC),
            security_group=bastion_sg,
            instance_name='Redis-Bastion',
        )

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
