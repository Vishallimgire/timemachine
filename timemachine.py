import argparse
import datetime
from os import listdir, path, mkdir, popen
import re
import logging
from logging.handlers import RotatingFileHandler

parser = argparse.ArgumentParser(description='Time Machine')

parser.add_argument('-c', '--configfile', default = 'config.dat',
                    help ='file to read the config from')

parser.add_argument('-b', '--backup', default = '/home/user/Documents/backup',
                    help ='Backup directory path')

parser.add_argument('-a', '--add', nargs = '*',
                    help ='Add file into config.dat')

parser.add_argument('-r', '--remove', nargs = '*',
                    help = 'remove file from config.dat list')

parser.add_argument('-l','--list', nargs = '*',
                    help = 'list all files from config.dat')

parser.add_argument('file', nargs = '*', default = False)

# Log configuration                   
LOG_FILENAME = 'timemachine.log'
rotating_handler = RotatingFileHandler(LOG_FILENAME,
				    maxBytes=10000000,
				    backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
rotating_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_handler)

"""
   read configuration
"""
def read_config(data):
    # import pdb;pdb.set_trace()
    try:
        logger.debug("Reading config from {0}".format(data))
        file = open(data)
        file_path = file.readlines()
        file.close()
        # print(file_path)
        return(file_path)
    except Exception as e:
        logger.error('Exception in read_config {}'.format(e))
        print('Exception in read_config', e)

"""
     Add files into config.dat
"""
def add_files(files, config):
    try:
        logger.debug("add files {} {}".format(files, config))
        filter_files = list()
        with open(config, 'r') as f:
            lines = f.readlines()
        lines = [re.sub(r'\s+', '', line) for line in lines]
        for each in files:
            if each not in lines:
                filter_files.append(each)
            else:
                print('This {} file already exist into {}'.format(each, config))
        if filter_files:
            with open(config, mode='a', encoding='utf-8') as config_file:
                config_file.write('\n'+'\n'.join(filter_files))
            print('\nList of file following below into {1} added successfully\n{0}'.format('\n'.join(filter_files), config))
        else:
            print('Already added all files')
    except Exception as e:
        print('Exception in add_files function {}'.format(e))
        logger.error('Exception in add_files function {}'.format(e))


"""
   remove file from config.dat
"""
def remove_files(files, config):
    try:
        logger.debug("remove files {} {}".format(files, config))
        with open(config, 'r') as f:
            lines = f.readlines()
        with open(config, 'w') as f:
            for count, line in enumerate(lines):
                if re.sub(r'\s+', '', line) not in files:
                    f.write(line)
                    if len(lines)-1 == count:
                        print('No any data remaining for remove')
                else:
                   print('{} this file removed successfully from {}'.format(re.sub(r'\s+', '', line), config))
    except Exception as e:
        print('Exception in add_files function {}'.format(e))
        logger.error('Exception in add_files function {}'.format(e))

"""
   list all files from config.dat
"""
def list_files(config):
    try:
        logger.debug("add files {}".format(config))
        with open(config, 'r') as f:
            lines = f.readlines()
        if lines:
            print('All list of files from {}\n'.format(config))
            print(''.join(lines))
        else:
            print('No any data found into {}'.format(config))
    except Exception as e:
        print('Exception in list_files function {}'.format(e))
        logger.error('Exception in list_files function {}'.format(e))

"""
   filter particular file
"""

def filter_file(name, directory):
    try:
        list_all_file = listdir(directory)
        filter_list = [each for each in list_all_file if each.split('_v')[0] == name]#filter list of given file
        return filter_list
    except Exception as e:
        print('Exception in filter_file function {}'.format(e))
        logger.error('Exception in filter_file function {}'.format(e))

"""
   file modificaation check
"""
def file_modification_check(file_path, directory):
    try:
        name, ext = file_path.split('/')[-1].split('.')
        # if directory not exist it will automatically create
        if not path.exists(directory):
            mkdir(directory)
            logger.debug('Creating directory {0}'.format(directory))
        #Taking first time backup
        if not filter_file(name, directory):
            popen('cp {} {}'.format(file_path, '{}/{}_v_1.{}'.format(directory, name, ext)))
            print('First time backup {}/{}_v_1.{}'.format(directory, name, ext))
            logger.debug('First time backup {}/{}_v_1.{}'.format(directory, name, ext))
            return None
        list_files = filter_file(name, directory)
        list_files.sort()
        backup_file = path.getmtime('{}/{}'.format(directory, list_files[-1])) < path.getmtime(file_path) # check file modified time with backuped file
        if backup_file:
            next_ver = len(list_files) + 1
            popen('cp {} {}'.format(file_path, '{}/{}_v_{}.{}'.format(directory, name, next_ver, ext))) #copy new version of file
            print('Backup file {}/{}_v_{}.{}'.format(directory, name, next_ver, ext))
            logger.debug('Backup file {}/{}_v_{}.{}'.format(directory, name, next_ver, ext))
        else:
            print('{} not updated'.format(file_path)) # if condition not match it will not update
            logger.debug('{} not updated'.format(file_path))
    except Exception as e:
        logger.error('Exception in file_modification_check {}'.format(e))
        print('Exception in file_modification_check', e)

"""
     Check multiple file changes and backup
"""
def handle_multiple_file(config_file, backup):
    try:
        config_file_list = read_config(config_file)
        for each in config_file_list:
            each_file = re.sub(r'\s+', '', each) # remove unwanted char like \n \t etc
            if each_file:
                file_modification_check(each_file, backup) 
    except Exception as e:
        logger.error('Exception in handle_multiple_file {}'.format(e))
        print('Exception in handle_multiple_file', e)

args = vars(parser.parse_args())  # convert args to dict
print(args)
# file_name = read_config(args['configfile'])
# file_modification_check(file_name)
args = {k: v for k, v in args.items() if v is not None} # filter args dict from None
# print(args)

"""
  All args condition module
"""
if 'add' in args:
    if args['add']:
        add_files(args['add'], args['configfile']) # add files from config
    else:
        print('Please add single file to update into config.dat')
elif 'remove' in args:
    if args['remove']:
        remove_files(args['remove'], args['configfile']) # remove files from config
    else:
        print('Please add single file to remove from config.dat')
elif 'list' in args:
    if not args['list']:
        list_files(args['configfile']) # show file list from config
    else:
        print("Please don't add argument after -l or --list")
elif 'file' in args and args['file']:
    handle_multiple_file(args['file'][0], args['backup']) # direct config file pass argument   
else:
    handle_multiple_file(args['configfile'], args['backup']) # default behavier and user define behaviour of config and backup folder   