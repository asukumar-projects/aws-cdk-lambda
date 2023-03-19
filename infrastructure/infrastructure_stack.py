from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_s3 as s3_,
    aws_logs as logs,
    aws_sns as sns,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_cloudwatch as cloudwatch,
    core
)


class InfrastructureStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **Kwargs) -> None:
        super().__init__(scope, construct_id, **Kwargs)

        bucket = s3_.Bucket(self, "landing",bucket_name="sports-odd-lnding")
        
        #Create an SNS topic
        my_topic = sns.Topic(self, 'Topic-for-SportsLambda-Response',topic_name='SportsLambda-Response')

        #Create an cloudWatch Metric Bucket --Not in use
        metric = cloudwatch.Metric(
          namespace =  'SportsOdd',
            metric_name = 'LatencyError'
                )
        
        #Create a CloudWatch Log group and stream --Not in use
        my_log_group = logs.LogGroup(self, 'SportsOdd',log_group_name='SportsOdd')
        
        my_log_stream = logs.LogStream(self, 'SportsOdd-stream',
                                       log_stream_name='SportsOdd-stream',
                                       log_group=my_log_group)
        
        #Create lambda Function
        lambdaFn = lambda_.Function(
            self, 
            id="SportsOddFunction",
            function_name='SportsOddFunction',
            code=lambda_.Code.from_asset("./compute/"),
            handler="Sports_Odd_Data.lambda_handler",
            timeout=core.Duration.seconds(900),
            runtime=lambda_.Runtime.PYTHON_3_9,
            environment={'TOPIC_ARN': my_topic.topic_arn,
                         'BUCKET_NAME': bucket.bucket_name,
                         'METRIC': metric.metric_name,
                         'LOG_GROUP': my_log_group.log_group_name,
                         'LOG_STREAM': my_log_stream.log_stream_name
                         }
        )

        #Grant Lambda read and write access to to the S3 Bucket
        bucket.grant_read_write(lambdaFn)

        #Schecule Lambda function
        rule = events.Rule(
            self, "SportsOdd-EventRule",
            rule_name='SportsOddFunction-EventRule',
            #schedule=events.Schedule.rate(core.Duration.minutes(10)),
            schedule=events.Schedule.rate(core.Duration.hours(24))
        )
        rule.add_target(targets.LambdaFunction(lambdaFn))
    
        #IAM Policy for the Lambda Function
        lambdaFn.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                'logs:PutLogEvents',
                'cloudwatch:PutMetricData',
                'sns:Publish',
                'secretsmanager:GetSecretValue'
            ],
            resources=['*',my_log_group.log_group_arn],
        ))
