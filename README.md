# s3shell

To run the shell: python3 s5Shell.py

- It will parse the config file and login to S3 and then it will wait for user input.
- If you enter any specific cloud input it will call the underlying method for it. For any other input, it will pass
it to the bash (Linux CLI)

Limitations:
- Not tested on Windows
- It will only create buckets in ca-central-1 region.
- You cannot use the command except create_bucket, list and cwlocn if you don't have any buckets.
