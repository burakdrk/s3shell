import unittest
from unittest.mock import patch
import sys
import configparser
import os
from s3shell import S3Func
import io
from contextlib import redirect_stdout


def get_config():
    config = configparser.ConfigParser()

    try:
        with open(os.path.expanduser('~')+'/.s3shell.conf') as f:
            config.read_file(f)
    except Exception as e:
        print('Could not read the config file, make sure it exists and formatted correctly. {}'.format(e))
        sys.exit(1)
    
    return config

class TestS3Func(unittest.TestCase):
    def setUp(self):
        config = get_config()
        self.access_key = config['default']['aws_access_key_id']
        self.secret_key = config['default']['aws_secret_access_key']
        self.region = config['default']['region']
        self.s3 = S3Func(self.access_key, self.secret_key, self.region)

    def test_parsePath(self):
        parsed_path = self.s3._S3Func__parsePath('test_path')
        self.assertEqual(parsed_path, '/test_path')

    def test_parsePathWithSlash(self):
        parsed_path = self.s3._S3Func__parsePath('/test_path')
        self.assertEqual(parsed_path, '/test_path')

    def test_objectExists(self):
        exists = self.s3._S3Func__objectExists('test_bucket', 'test_key')
        self.assertFalse(exists)

    def test_deleteBucket(self):
        bucket_path = '/test-bucket-s3shell'
        self.s3.deleteBucket(bucket_path)

        with io.StringIO() as buf, redirect_stdout(buf):
            self.s3.listDirectory('/')
            output = buf.getvalue()
            self.assertNotIn('test-bucket-s3shell', output)

    def test_createBucket(self):
        bucket_path = '/test-bucket-s3shell'
        self.s3.createBucket(bucket_path)

        with io.StringIO() as buf, redirect_stdout(buf):
            self.s3.listDirectory('/')
            output = buf.getvalue()
            self.assertIn('test-bucket-s3shell', output)


if __name__ == '__main__':
    unittest.main()
