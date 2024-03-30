from .s3Func import S3Func
import configparser
import subprocess
import sys
import os
import readline
import rlcompleter

def options():
    print('Options:')
    print('\tcreate_bucket <bucket_name>\n\t\tCreates a new bucket with the given name.')
    print('\tdelete_bucket <bucket_name>\n\t\tDeletes the bucket with the given name.')
    print('\tcreate_folder <folder_name>\n\t\tCreates a new folder in the current directory.')
    print('\ts3delete <s3_object_name>\n\t\tDeletes the object with the given name.')
    print('\ts3copy <source> <destination>\n\t\tCopies the object from source to destination.')
    print('\tlocs3cp <local_file> <s3_destination>\n\t\tCopies the local file to the s3 destination.')
    print('\ts3loccp <s3_object> <local_destination>\n\t\tCopies the s3 object to the local destination.')
    print('\tcwlocn\n\t\tPrints the current working cloud directory.')
    print('\tchlocn <new_directory>\n\t\tChanges the current working cloud directory.')
    print('\tlist [-l] [/<bucket name>/<full pathname for directory or file>]\n\t\tLists the contents of the given directory or bucket. Use -l for verbose.')
    print('\texit')

def completer(text, state):
    commands = ['create_bucket', 'delete_bucket', 'create_folder', 's3delete', 's3copy', 'locs3cp', 's3loccp', 'cwlocn', 'chlocn', 'list', 'exit']
    options = [i for i in commands if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

def main():
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    readline.set_completer(completer)

    if os.name == 'nt':
        print('This program is not supported on Windows.')
        sys.exit(1)

    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            print('s3shell: A shell program for interacting with AWS S3 storage.')
            print('Usage: s3shell')
            options()
            sys.exit(0)
        elif sys.argv[1] == '--reset':
            try:
                os.remove(os.path.expanduser('~')+'/.s3shell.conf')
            except Exception as e:
                print('Could not remove the config file. {}'.format(e))
                sys.exit(1)

            print('Config file removed.')
            sys.exit(0)
        else:
            print('s3shell: This program only accepts --help and --reset as arguments.')
            sys.exit(1)

    config = configparser.ConfigParser()
    
    # Read the config file
    while True:
        try:
            with open(os.path.expanduser('~')+'/.s3shell.conf') as f:
                config.read_file(f)
            
            break
        except Exception as e:
            if e.errno == 2:
                print('Could not find the config file, creating a new one.')
            else:
                print('Could not read the config file, make sure it exists and formatted correctly. {}'.format(e))
                sys.exit(1)

        access_key = input('Enter your AWS access key: ')
        secret_key = input('Enter your AWS secret key: ')
        region = input('Enter your AWS region for new bucket creation: ')

        config['default'] = {
            'aws_access_key_id': access_key,
            'aws_secret_access_key': secret_key,
            'region': region
        }

        with open(os.path.expanduser('~')+'/.s3shell.conf', 'w') as f:
            config.write(f)


    # Authenticate with the config
    try:
        # Create an s3 functionality object
        s3 = S3Func(config['default']['aws_access_key_id'], config['default']['aws_secret_access_key'], config['default']['region'])
    except Exception as e:
        print(e)
        print('Could not authenticate with the provided credentials. Make sure IAM user has the right permissions or use --reset to reset the config file.')
        sys.exit(1)

    print('You are now connected to your S3 storage')

    while True:
        command = input(s3.user+'@'+s3.region_name+':'+s3.workingDir+'$ ')
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

        elif split_command[0] == 'help':
            options()

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
