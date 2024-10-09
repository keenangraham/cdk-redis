from aws_cdk import App
from aws_cdk import CfnOutput
from aws_cdk import Environment
from aws_cdk import Stack
from aws_cdk import Size

from aws_cdk.aws_ec2 import SubnetSelection
from aws_cdk.aws_ec2 import SubnetType

from aws_cdk.aws_secretsmanager import Secret as SMSecret

from aws_cdk.aws_iam import Role
from aws_cdk.aws_iam import ServicePrincipal

from aws_cdk.aws_ec2 import Vpc

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


RedisStack(
    app,
    'RedisStack',
    env=US_WEST_2,
)


app.synth()
