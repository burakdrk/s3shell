import s3Func
import configparser
import subprocess
import sys
import os
import readline

def main():
    print('Welcome to the AWS S3 Storage Shell')
    
    config = configparser.ConfigParser()
    
    # Read the config file
    try:
        with open('S5-S3.conf') as f:
            config.read_file(f)
    except Exception as e:
        print('Could not read the config file, make sure it exists and formatted correctly. {}'.format(e))
        sys.exit(1)

    # Authenticate with the config
    try:
        # Create an s3 functionality object
        s3 = s3Func.S3Func(config['default']['aws_access_key_id'], config['default']['aws_secret_access_key'])
    except Exception as e:
        print(e)
        sys.exit(1)

    print('You are now connected to your S3 storage')

    while True:
        command = input('S5> ')
        split_command = command.split()

        if not split_command: continue

        if command == 'exit' or command == 'quit':
            break

        # For built in function for system directory change. Calls underlying bash.
        elif split_command[0] == 'cd':
            if len(split_command) == 2:
                try:
                    os.chdir(os.path.abspath(split_command[1]))
                except Exception:
                    print('cd: {}: No such file or directory'.format(split_command[1]))
            else:
                print('cd: incorrect number of arguments')

        ##########  FOR S3 FUNCTIONS ##########
        ########## PRINTS EXCEPTIONS ##########
        elif split_command[0] == 'create_bucket':
            if len(split_command) == 2:
                try:
                    s3.createBucket(split_command[1])
                except Exception as e:
                    print(e)
            else:
                print('{}: incorrect number of arguments'.format(split_command[0]))

        elif split_command[0] == 'delete_bucket':
            if len(split_command) == 2:
                try:
                    s3.deleteBucket(split_command[1])
                except Exception as e:
                    print(e)
            else:
                print('{}: incorrect number of arguments'.format(split_command[0]))

        elif split_command[0] == 's3delete':
            if len(split_command) == 2:
                try:
                    s3.deleteObject(split_command[1])
                except Exception as e:
                    print(e)
            else:
                print('{}: incorrect number of arguments'.format(split_command[0]))

        elif split_command[0] == 'create_folder':
            if len(split_command) == 2:
                try:
                    s3.createDirectory(split_command[1])
                except Exception as e:
                    print(e)
            else:
                print('{}: incorrect number of arguments'.format(split_command[0]))

        elif split_command[0] == 's3copy':
            if len(split_command) == 3:
                try:
                    s3.copyObject(split_command[1], split_command[2])
                except Exception as e:
                    print(e)
            else:
                print('{}: incorrect number of arguments'.format(split_command[0]))

        elif split_command[0] == 'locs3cp':
            if len(split_command) == 3:
                try:
                    s3.localToCloud(os.path.abspath(split_command[1]), split_command[2])
                except Exception as e:
                    print(e)
            else:
                print('{}: incorrect number of arguments.'.format(split_command[0]))

        elif split_command[0] == 's3loccp':
            if len(split_command) == 3:
                try:
                    s3.cloudToLocal(split_command[1], os.path.abspath(split_command[2]))
                except Exception as e:
                    print(e)
            else:
                print('{}: incorrect number of arguments.'.format(split_command[0]))

        elif split_command[0] == 'cwlocn':
            if len(split_command) == 1:
                print(s3.workingDir)
            else:
                print('{}: incorrect number of arguments'.format(split_command[0]))

        elif split_command[0] == 'chlocn':
            if len(split_command) == 2:
                try:
                    s3.changeDirectory(split_command[1])
                except Exception as e:
                    print(e)
            else:
                print('{}: incorrect number of arguments'.format(split_command[0]))

        elif split_command[0] == 'list':
            if len(split_command) > 1 and len(split_command) < 4:
                try:
                    # Check if it has verbose flag
                    if '-l' in split_command:
                        if len(split_command) == 2:
                            s3.listDirectory(long=True)
                        elif len(split_command) == 3 and split_command[1] == '-l':
                            s3.listDirectory(split_command[2], True)
                        elif len(split_command) == 3 and split_command[2] == '-l':
                            s3.listDirectory(split_command[1], True)
                    else:
                        if len(split_command) == 2:
                            s3.listDirectory(split_command[1])
                        else:
                            print('list: Incorrect arguments. Make sure the format is: list [-l] [/<bucket name>/<full pathname for directory or file>]')
                except Exception as e:
                    print(e)
            elif len(split_command) == 1:
                try:
                    s3.listDirectory()
                except Exception as e:
                    print(e)
            else:
                print('{}: incorrect number of arguments'.format(split_command[0]))

        # For any other command, pass it to bash
        else:
            try:
                subprocess.run(split_command)
            except FileNotFoundError:
                print('Command or file "{}" not found, please try again.'.format(command.split()[0]))
            except Exception as e:
                print(e)
                
if __name__ == '__main__':
    main()
