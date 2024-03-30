# s3shell

To install: pip install s3shell

- It will parse the config file and login to S3 and then it will wait for user input.
- If you enter any specific cloud input it will call the underlying method for it. For any other input, it will pass
it to the bash (Linux CLI)
- Requires full S3 and read only IAM access.

Limitations:
- Only works on POSIX, no Windows support
- You cannot use the command except create_bucket, list and cwlocn if you don't have any buckets.
