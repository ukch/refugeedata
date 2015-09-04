# refugeedata

Installation instructions:

1. Create an account on [Amazon Web Services](https://aws.amazon.com/).
2. Navigate to the [users page](https://console.aws.amazon.com/iam/home#users) and create a user, making sure the 'Generate an access key for each user' box is checked. On the following page click 'Show User Security Credentials' and make a note of both values.
3. Click on your new user's name, scroll down to 'Permissions' and click 'Attach Policy'. Search for a policy called *AmazonS3FullAccess* and add it.
4. Navigate to [Amazon S3](https://console.aws.amazon.com/s3) and create a bucket. Make sure not to select Frankfurt as a region for technical reasons. Make a note of your new bucket name.
5. (Optional) Create a [Sentry](https://getsentry.com) account and project for error logging purposes. Or just talk to us and we'll let you use ours. Make a note of the *DSN* for your project.
6. You're finally ready to click this button: [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)
7. Give your application a name (optional) and select a region.
8. Fill in the form using the data you made a note of earlier.
9. Click 'Deploy for Free'. Make yourself a cup of tea while the application deploys.
10. Click 'View' to log into the admin interface of your application.
