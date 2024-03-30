import boto3
import pathlib

## Class for S3 Functionality
class S3Func:
    # Constructor to initialize the functionality object and authenticate
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, region_name: str = 'ca-central-1'):
        self.session = boto3.Session(aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key)
        self.s3Client = self.session.client('s3')
        self.s3Res = self.session.resource('s3')
        self.region_name = region_name
        self.workingDir = '/'
        self.user = self.session.client('iam').get_user().get('User').get('UserName') or 'root'

        try:
            self.hasBuckets = True if len(self.s3Client.list_buckets().get('Buckets')) > 0 else False
        except Exception:
            raise Exception('You could not be connected to your S3 storage\nPlease review procedures for authenticating your account on AWS S3')

    # Private helper function that checks user entered paths and resolves them to absolute. S3 functions always deal with absolute paths.
    def __parsePath(self, path: str):
        if path.endswith('/') and len(path) > 1:
            path = path[:-1]

        if path.startswith('~'): path = path[1:] or '/'
        
        if path.startswith('/'): # if entered path is absolute
            return str(pathlib.PosixPath(path).resolve())
        else:
            return str(pathlib.PosixPath(self.workingDir, path).resolve())

    # Private helper to check if the object with the key already exists.
    def __objectExists(self, bucket, key):
        try:
            self.s3Client.head_object(Bucket=bucket, Key=key)
        except Exception:
            return False

        return True

    # Method to copy local files to an S3 location (locs3cp)
    def localToCloud(self, local_path: str, s3_path: str):
        if not self.hasBuckets: raise Exception('You cannot use this command if you have no buckets.')

        parsed_path = self.__parsePath(s3_path)

        bucket = parsed_path.split('/')[1]
        key = '/'.join(parsed_path.split('/')[2:])

        # Check format
        if not key or not bucket: raise Exception('Unsuccessful copy. Make sure the format is: locs3cp /<bucket name>/<full pathname of S3 object>')

        # Check if S3 file already exists
        if self.__objectExists(bucket, key): raise Exception('Unsuccessful copy. Make sure the S3 file does not already exist.')

        try:
            self.s3Res.Bucket(bucket).upload_file(local_path, key)
        except Exception:
            raise Exception('Unsuccessful copy. Make sure the local file exists.')

    # Method to copy S3 files to a local location (s3loccp)
    def cloudToLocal(self, s3_path: str, local_path: str):
        if not self.hasBuckets: raise Exception('You cannot use this command if you have no buckets.')

        parsed_path = self.__parsePath(s3_path)

        bucket = parsed_path.split('/')[1]
        key = '/'.join(parsed_path.split('/')[2:])

        # Check format
        if not key or not bucket: raise Exception('Unsuccessful copy. Make sure the format is: s3loccp /<bucket name>/<full pathname of S3 file> <full/relative pathname of the local file>')
        
        try:
            self.s3Client.download_file(bucket, key, local_path)
        except Exception:
            raise Exception('Unsuccessful copy. Make sure the S3 file exists.')

    # Method to copy from S3 to S3
    def copyObject(self, path1: str, path2: str):
        if not self.hasBuckets: raise Exception('You cannot use this command if you have no buckets.')

        parsed_path1 = self.__parsePath(path1)
        parsed_path2 = self.__parsePath(path2)

        from_bucket = parsed_path1.split('/')[1]
        from_object = '/'.join(parsed_path1.split('/')[2:])
        to_bucket = parsed_path2.split('/')[1]
        to_object = '/'.join(parsed_path2.split('/')[2:])

        if not from_object or not to_object:
            raise Exception('Cannot perform copy. Cannot copy a bucket.')

        # Check if source does not exist
        if not self.__objectExists(from_bucket, from_object) and not self.__objectExists(from_bucket, from_object+'/'):
            raise Exception('Cannot perform copy. The source object does not exist.')

        # Check if destination already exists
        if self.__objectExists(to_bucket, to_object) or self.__objectExists(to_bucket, to_object+'/'):
            raise Exception('Cannot perform copy. The destination object already exists.')

        try:
            copy_source = {'Bucket': from_bucket, 'Key': from_object if self.__objectExists(from_bucket, from_object) else from_object+'/'}
            self.s3Client.copy(copy_source, to_bucket, to_object)
        except Exception:
            raise Exception('Cannot perform copy.')

    # Method to create a bucket in S3.
    def createBucket(self, bucket_path: str):
        bucket_name = bucket_path[1:]

        # Check format
        if bucket_path[0] != '/' or not bucket_name:
            raise Exception('Cannot create bucket. Make sure the format is: create_bucket /<bucket name>')

        try:
            self.s3Client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': self.region_name})
        except Exception:
            raise Exception('Cannot create a bucket. Make sure the bucket name: {} is not taken'.format(bucket_name))

        self.hasBuckets = True

    # Method to delete a bucket in S3
    def deleteBucket(self, bucket_path: str):
        if not self.hasBuckets: raise Exception('You cannot use this command if you have no buckets.')
        
        bucket_name = bucket_path[1:]

        # Check format
        if bucket_path[0] != '/' or not bucket_name:
            raise Exception('Cannot delete bucket. Make sure the format is: delete_bucket /<bucket name>')

        # Check if trying to delete the current bucket
        if bucket_name == self.workingDir.split('/')[1]:
            raise Exception('Cannot delete bucket. You cannot delete the bucket that you are currently in.')

        try:
            objects = self.s3Client.list_objects_v2(Bucket=bucket_name)

            # Check if the bucket is not empty
            if objects['KeyCount'] > 0:
                raise Exception
                
            self.s3Client.delete_bucket(Bucket=bucket_name)

            # Update the thing
            self.hasBuckets = True if len(self.s3Client.list_buckets().get('Buckets')) > 0 else False
        except Exception:
            raise Exception('Cannot delete bucket. Make sure the bucket: {} exists and is empty.'.format(bucket_name))

    # Method to delete a file or directory in S3
    def deleteObject(self, path: str):
        if not self.hasBuckets: raise Exception('You cannot use this command if you have no buckets.')

        parsed_path = self.__parsePath(path)

        prefix = '/'.join(parsed_path.split('/')[2:])+'/'
        bucket = parsed_path.split('/')[1]

        if parsed_path == self.workingDir:
            raise Exception('Cannot perform delete. You cannot delete the directory that you are currently in.')

        if prefix == '/':
            raise Exception('Cannot perform delete. You cannot delete a bucket with this command.')

        try:
            # Check if trying to delete a directory
            res = self.s3Client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            # Check if directory is not empty
            if res.get('KeyCount') > 1:
                raise Exception
            # If its empty
            elif res.get('KeyCount') == 1:
                self.s3Client.delete_object(Bucket=bucket, Key=prefix)
                return
        except Exception:
            raise Exception('Cannot perform delete. Make sure the directory is empty.')

        # If it's a file
        try:
            # If it does not exist
            if not self.__objectExists(bucket, prefix.rstrip('/')):
                raise Exception

            self.s3Client.delete_object(Bucket=bucket, Key=prefix.rstrip('/'))
        except Exception:
            raise Exception('Cannot perform delete. Make sure the object exists.')

    # Method to create a folder within a bucket
    def createDirectory(self, path: str):
        if not self.hasBuckets: raise Exception('You cannot use this command if you have no buckets.')

        parsed_path = self.__parsePath(path)

        key = '/'.join(parsed_path.split('/')[2:])+'/'
        bucket = parsed_path.split('/')[1]

        # Format check
        if key == '/':
            raise Exception('Cannot create folder. Make sure the format is: <full or relative pathname for the folder>')

        # Check if directory already exists
        if self.__objectExists(bucket, key):
            raise Exception('Cannot create folder. Make sure it does not already exist.')
    
        try:
            self.s3Client.put_object(Bucket=bucket, Body=b'', Key=key)
        except Exception:
            raise Exception('Cannot create folder.')
    
    # Method to change the current working directory
    def changeDirectory(self, path: str):
        if not self.hasBuckets: raise Exception('You cannot use this command if you have no buckets.')

        parsed_path = self.__parsePath(path)

        prefix = '/'.join(parsed_path.split('/')[2:])
        bucket = parsed_path.split('/')[1]

        if parsed_path == '/':
            self.workingDir = parsed_path
            return

        # Check if the bucket exists.
        if not prefix:
            try:
                self.s3Client.head_bucket(Bucket=bucket)
            except Exception:
                raise Exception('Cannot change folder. Make sure it exists.')

            self.workingDir = parsed_path
            return
            
        # Check if the folder exists.
        if not self.__objectExists(bucket, prefix+'/'): raise Exception('Cannot change folder. Make sure it exists.')

        self.workingDir = parsed_path

    # Method to list the desired directory within S3
    def listDirectory(self, path='', long=False):
        parsed_path = self.__parsePath(path)

        if parsed_path == '/':
            self.__listBuckets(long) 
        else:
            self.__listObjects(parsed_path, long)

    # Private helper method to list the buckets only (for /)
    def __listBuckets(self, long: bool):
        try:
            buckets = self.s3Client.list_buckets()

            for bucket in buckets.get('Buckets'):
                if long:
                    print('Type: Bucket, Creation Date: {}, Size: {}B, Name: {}'.format(bucket.get('CreationDate'), sum([object.size for object in self.s3Res.Bucket(str(bucket.get('Name'))).objects.all()]), bucket.get('Name')))
                else:
                    print(bucket.get('Name'))
        except Exception:
            raise Exception('Cannot list contents of this S3 location. Make sure it exists and the format is: list [-l] [/<bucket name>/<full pathname for directory or file>]')

    # Private helper method to list objects within a bucket
    def __listObjects(self, parsed_path: str, long: bool):
        prefix = '/'.join(parsed_path.split('/')[2:])+'/'
        bucket = parsed_path.split('/')[1]
        toPrint: list[str] = []

        try:
            objects = self.s3Client.list_objects_v2(Bucket=bucket, Prefix='' if prefix=='/' else prefix, Delimiter='/')
            # Check if anything exists
            if objects.get('KeyCount') == 0 and prefix != '/': raise Exception('Cannot list contents of this S3 location. Make sure it exists and the format is: list [-l] [/<bucket name>/<full pathname for directory or file>]')

            # For files
            if objects.get('Contents'):
                for object in objects.get('Contents'):
                    key = str(object.get('Key')).split(prefix,1)
                    index = 1 if not key[0] else 0

                    if not key[index].split('/')[0]: continue

                    if long:
                        toPrint.append('Type: File, Size: ' + str(object.get('Size')) + 'B, Last Modified: ' + str(object.get('LastModified')) + ', Name: ' + str(key[index].split('/')[0]))
                    else:
                        toPrint.append(str(key[index].split('/')[0]))

            # For directories
            if objects.get('CommonPrefixes'):
                for object in objects.get('CommonPrefixes'):
                    prefix = str(object.get('Prefix')).split(str(prefix), 1)
                    index = 1 if not prefix[0] else 0
                    
                    if not prefix[index].split('/')[0]: continue

                    if long:
                        toPrint.append('Type: Directory, Size: {}B, Last Modified: {}, Name: {}'.format(sum([object.size for object in self.s3Res.Bucket(str(bucket)).objects.filter(Prefix=str(object.get('Prefix')))]), self.s3Client.head_object(Bucket=bucket, Key=str(object.get('Prefix'))).get('LastModified'), str(prefix[index].split('/')[0])))
                    else:
                        toPrint.append(str(prefix[index].split('/')[0]))

            # Print
            for info in toPrint:
                print(info)
        except Exception:
            raise Exception('Cannot list contents of this S3 location. Make sure it exists and the format is: list [-l] [/<bucket name>/<full pathname for directory or file>]')
