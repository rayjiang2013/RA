# RallyAutomation2

You need:

1. create a file named as config.cfg with content below:
SERVER = rally1.rallydev.com
USER = your username
PASSWORD = your password
APIKEY = your apikey
WORKSPACE = your workspace name
PROJECT = your project name

2. create a file named as mysql.json:
{"sqldb": {"passwd": your password, "autocommit": "True", "host": your host, "db": your db, "user": your username}}

2. then put the files into your project folder RallyAutomation/src/test/run

3. run the command line option: --config=config.cfg extra.json logging.json
