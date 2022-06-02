"""
For testing and debugging

to see celery's task queue history, check out result.sqlite within sqlitebrowser

"""
import requests
jsonText = {
    "title":"Application Performance Monitoring AWS Lambda Functions with Sentry",
    "author":"Matt Makai",
    "date_published":2021,
    "lead_image_url":"https://www.fullstackpython.com/img/headers/python-lambda-sentry.jpg",
    "content":"\nAmazon Web Services (AWS) Lambda is a usage-based\ncomputing infrastructure service that can execute\nPython 3 code. One of the challenges of this\nenvironment is ensuring efficient performance of your Lambda Functions.\nApplication performance monitoring (APM) is particularly useful in these\nsituations because you are billed based on how long you use the\nresources.\nIn this post we will install and configure\nSentry's APM that works via a\nLambda layer.\nNote that if you are looking for error monitoring rather than performance\nmonitoring, take a look at\nHow to Monitor Python Functions on AWS Lambda with Sentry\nrather than following this post.\nFirst steps with AWS Lambda\nA local development environment is not\nrequired to follow this tutorial because all of the coding and configuration\ncan happen in a web browser through the\nAWS Console.\nSign into your existing AWS account\nor sign up for a new account. Lambda\ngives you the first 1 million requests for free so that you can execute\nbasic applications without no or low cost.\n\nWhen you log into your account, use the search box to enter\n\"lambda\" and select \"Lambda\" when it appears to get to the right\npage.\n\nIf you have already used Lambda before, you will see your existing Lambda\nfunctions in a searchable table. We're going to create a new function so\nclick the \"Create function\" button.\n\nThe create function page will give you several options for building a\nLambda function.\n\nClick the \"Browse Serverless App Repository\" selection box, then choose\nthe \"hello-world-python3\" starter app from within the\n\"Public applications\" section.\n\nThe hello-world-python3 starter app details page should look something\nlike the following screen:\n\nFill in some example text such as \"test\" under IdentityNameParameter\nand click the \"Deploy\" button:\n\nThe function will now be deployed. As soon as it is ready we can\ncustomize it and test it out before adding Sentry to capture any errors\nthat occur during execution.\nGo back to the Lambda functions main page and select your new deployed\nstarter app from the list.\n\nFind the orange \"Test\" button with a down arrow next to it like you\nsee in the image below, and then click the down arrow. Select\n\"Configure Test Event\".\n\nFill in the Event name as \"FirstTest\" or something similar, then\npress the \"Create\" button at the bottom of the modal window.\nClick the \"Test\" button and it will run the Lambda function with\nthe parameters from that new test event. You should see something\nlike the following output:\nResponse\n\"value1\" Function Logs\nSTART RequestId: 62fa2f25-669c-47b7-b4e7-47353b0bd914 Version: $LATEST\nvalue1 = value1\nvalue2 = value2\nvalue3 = value3\nEND RequestId: 62fa2f25-669c-47b7-b4e7-47353b0bd914\nREPORT RequestId: 62fa2f25-669c-47b7-b4e7-47353b0bd914 Duration: 0.30 ms Billed Duration: 1 ms Memory Size: 128 MB Max Memory Used: 43 MB Init Duration: 1.34 ms\n\nRequest ID\n62fa2f25-669c-47b7-b4e7-47353b0bd914\n\nThe code was successfully executed, so let's add Sentry's performance\nmonitoring and test some code that uses it.\nPerformance monitoring with Sentry\nGo to Sentry.io's homepage.\n\nSign into your account or sign up for a new free account. You will be at\nthe main account dashboard after logging in or completing the Sentry sign\nup process.\nSelect \"Performance\" on the left navigation bar, it will take you to the\nperformance monitoring page.\n\nClick \"Start Setup\" then go back over to AWS Lambda to complete the\nsteps for adding Sentry's Python layer to your Lambda function.\nThe easiest way to add Sentry to Lambda for this application\nis to configure an\nAWS Lambda Layer\nwith the necessary dependency for Sentry. Sentry has concise\ndocumentation on adding via Lambda Layers\nso we will walk through that way to configure it and test it\nout.\nScroll down to the \"Layers\" section while in your Lambda\nfunction configuration. Click the \"Add a layer\" button\":\n\nIn the \"Add layer\" screen, select the \"Specify an ARN\" option.\n\nNow to specify the Amazon Resource Name (ARN), we need to use\nthe Sentry documentation to get the right configuration string.\nUS-East-1 is the oldest and most commonly-used region so I'll\nuse that here in this tutorial but you should check which one\nyou are in if you are not certain.\n\nCopy that value into the Lambda Layer configuration, like this:\n\nThen press the \"Add\" button. You now have the Sentry dependency\nin your environment so code that relies upon that library can be\nused in the Lambda function.\nTesting performance monitoring\nLet's change our Python code in the Lambda function and test out\nthe APM agent.\nMake sure you are signed into your Sentry account and go to\nthis specific AWS Lambda set up guide.\nYou will see a \"DSN string\" that we need to set as an environment\nvariable on AWS Lambda to finish our setup. Copy the string that\nmatches your project as shown on that page in the highlighted green\nsection:\n\nWe will\nuse environment variables on AWS Lambda\nto store and access values like this Sentry DSN key.\nGo into the Lambda console to create a new environment variable. To do\nthat, click the \"Configuration\" tab within Lambda like you see here:\n\nThen click \"Edit\" and add a new environment variable with the key of SENTRY_DSN\nand the value of the DSN string that you copied from the Sentry screen. \n\nClick the \"Save\" button and go back to your Lambda function's code editor.\nReplace the code in your Lambda function with the following code:\nimport json\nimport os\nimport sentry_sdk\nimport time\nfrom sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration\nfrom sentry_sdk import start_transaction SENTRY_DSN = os.environ.get('SENTRY_DSN')\nsentry_sdk.init( dsn=SENTRY_DSN, traces_sample_rate=1.0,\n    integrations=[AwsLambdaIntegration()]\n)\n\nprint('Loading function')\n\n\ndef lambda_handler(event, context):\n    calc = 1000\n\n    # this is custom instrumentation, see docs: https://bit.ly/2WjT3AY\n    with start_transaction(op=\"task\", name=\"big calculation\"):\n        for i in range(1, 1000):\n            calc = calc * i\n\n    print(calc)\n    return event['key1']  # Echo back the first key value\n\nThe above code imports the Sentry dependencies, and then runs both\nautomatic instrumentation\nand custom instrumentation on the\ncode. Click the \"Deploy\" button and then \"Test\". The code will\nsuccessfully execute and when we go back to our Sentry performance\nmonitoring dashboard we will see some initial results, like this\nfollowing screenshot.\n\nLooks good, you have both the default and the specified transaction\nperformance recordings in the dashboard, and you can toggle between\nthem (or other transactions you record) through the user interface.\nWhat's Next?\nWe just wrote and executed a Python 3 function on AWS Lambda that\nused the basics of Sentry APM to get some initial performance\nmonitoring data.\nCheck out the AWS Lambda section for\nmore tutorials by other developers.\nFurther questions? Contact me on Twitter\n@fullstackpython\nor @mattmakai. I am also on GitHub with\nthe username mattmakai.\nSomething wrong with this post? Fork\nthis page's source on GitHub\nand submit a pull request.\n",
    "next_page_url":'null',
    "url":"https://www.fullstackpython.com/blog/application-performance-monitoring-aws-lambda-functions-sentry.html",
    "domain":"fullstackpython",
    "excerpt":"Learn how to use Sentry Application Performance Monitoring on AWS Lambda. Great post on fullstackpython.com!",
    "word_count":1113,
    "direction":"ltr",
    "total_pages":1,
    "rendered_pages":1
 }

res = requests.post('http://localhost:5000/inbound/add_article/4567', json=jsonText)

if res.ok:
    print(res.json())



