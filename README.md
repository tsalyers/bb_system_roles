# bb_system_roles
## A quick and easy way to add secondary system roles in Blackboard Learn via the REST API. 
### Installation
- Optionally create and activate a Python virtual environment (via venv or similar tools). 
- Install the required libraries with `pip install -r requirements.txt`. 
- Copy the `.env-dist` file to `.env` and fill out the placeholder entries with your Learn hostname, key, and secret. 
### Usage
From the built-in documentation: 
```
usage: bb_system_roles.py [-h] [-f FILE | -u USER] -r ROLE

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Filename containing a list of user IDs to assign roles (one ID per line)
  -u USER, --user USER  User ID to assign a role
  -r ROLE, --role ROLE  New secondary system role ID
  ```
### Caveats
- You'll need to make sure the user you're using for REST has permissions to view and update users' system roles. 
- The script doesn't currently check whether a user already has a secondary system role, and will add it again even if it's already attached to the user. (This doesn't really affect anything; it's just untidy.)
