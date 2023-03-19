# Data ingestion from RAPID API to AWS S3 using AWS Lambda

This project contains the AWS CDK kit implemented for deplpying an AWS Lambda function that can extract data from API and load it to a 
AWS S3 bucket. The Lambda function is integrated with AWS Eventbridge to manage scheculing and is also integrated with AWS SNS to send 
error notifications to the SNS topic.

The cdk.json file tells the CDK Toolkit how to execute your app.

# Deployment instructions

1. Create a new directory, navigate to that directory in a terminal and clone the GitHub repository:
    ```git clone ```


2. create a virtualenv on MacOS and Linux:
    
    ```python3 -m venv .venv```


3. After the init process completes and the virtualenv is created, you can use the following step to activate your virtualenv.
    
    ```source .venv/bin/activate```

    On Windows machine you can use
        
    ```.venv\Scripts\activate.bat```

4. Once the virtualenv is activated, you can install the required dependencies.
    
    ```pip install -r requirements.txt```

5. To setup Rapid API

    ```Vist link *https://rapidapi.com/theoddsapi/api/live-sports-odds/* subscribe with your email ID to generate the API Access Key. Once the API key is generated add it to AWS Secrets Manager with the secrets name *X-RapidAPI-Key*```


6. To get SNS Error Notifications

    You can subscribe to SNS topic *SportsLambda-Response* to receive SNS notifications

7. From the command line, use AWS CDK to synthesize an AWS CloudFormation

    ```cdk synth```

8. Expected results

    Should install stacks as the image below

    ![cdk stacks](Initial_cdk_deploy_output)


