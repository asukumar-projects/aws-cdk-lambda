from aws_cdk import core as cdk

from aws_cdk import core
from aws_cdk import aws_lambda
class InfrastructureStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        random_drinks_function = aws_lambda.Function(
            self,
            id="RandomDrinkFunction",
            code=aws_lambda.Code.from_asset("./compute/"),
            handler="random_drink_lambda_hander",
            runtime=aws_lambda.Runtime.PYTHON_3_8
        )

    
        # example resource
        # queue = sqs.Queue(
        #     self, "InfrastructureQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
