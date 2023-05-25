import requests
from base64 import b64encode
from dotenv import load_dotenv
import json
import os 
import argparse

# Parse our command line arguments. 
# Make the file and userId arguments mutually exclusive--it doesn't make sense to have both.
ap = argparse.ArgumentParser()
arg_group = ap.add_mutually_exclusive_group()
arg_group.add_argument("-f", "--file", help="Filename containing a list of user IDs to assign roles")
arg_group.add_argument("-u", "--user", help="User ID to assign a role")
ap.add_argument("-r", "--role", required=True,
   help="New secondary system role ID")
args = vars(ap.parse_args())

# We need either a file of usernames or a single user.
# If we don't have either, error out.
if args['file'] is None and args['user'] is None:
    ap.error('Either -f/--file or -u/--user is required.')
	
# Get our user(s) and new role.
users = []
if args['user']:
    users.append(args['user'])
if args['file']:
    users = [line.rstrip('\n') for line in open(args['file'])]
new_role = args['role']
	

# Get some REST-related values from our .env config.
from dotenv import load_dotenv
load_dotenv()
REST_HOSTNAME = os.getenv("REST_HOSTNAME")
REST_CLIENT_ID = os.getenv("REST_CLIENT_ID")
REST_SECRET = os.getenv("REST_SECRET")
OAUTH_URL = os.getenv("OAUTH_URL")
USER_ENDPOINT = os.getenv("USER_ENDPOINT")
ROLE_QUERY = os.getenv("ROLE_QUERY")

# Helper function to put together the proper headers for requests to Blackboard. 
def get_auth_headers():
    auth_token = get_auth_token()
    return {'Authorization': 'Bearer ' + get_auth_token(), 'Content-Type': 'application/json'}

# Get an OAuth token from Blackboard. 
def get_auth_token():
    try:
        # First encode our credentials. The standard expects a base64-encoded string of the 
        # key and secret separated by a colon--'key:secret'. The encode and decode calls 
        # are because we need to send a string, but b64encode works on bytes. Irritating.
        encoded_credentials = b64encode( (REST_CLIENT_ID + ':' + REST_SECRET).encode() ).decode()
            
        # Add 'Basic' on to form the rest of our header content, then post our request to the 
        # auth URL. Note the grant_type body field--this has to be set or the request won't work.
        authorization = 'Basic ' + encoded_credentials
        resp = requests.post(REST_HOSTNAME + OAUTH_URL, headers={'Authorization':authorization}, data={'grant_type':'client_credentials'})
            
        #Finally, grab the access token from the returned JSON and cache it, 
        # then return the new token. 
        auth_token = json.loads(resp.text)['access_token']
        return auth_token
    except Exception as e:
        # Uh-oh. Something's gone wrong. Re-raise our exception.
        # NB: Throwing around generic Exceptions is kind of terrible, 
        # but the exception hierarchy of everything above is tangled and
        # also terrible. Let's just catch everything. 
        raise Exception(str(e))

# Get user data here.
PLACEHOLDER_USER = 'cs1tds'


# Get an auth token for the REST API and put it into our request headers...
auth_headers = get_auth_headers()

# Helper functions for finding and updating a user's roles. 
def get_user_roles(user):
    endpoint = USER_ENDPOINT.format(userId=user)
    resp = requests.get(REST_HOSTNAME + endpoint + ROLE_QUERY, headers = auth_headers)
    return resp.json()['systemRoleIds']
	
def update_user_roles(user, roles, new_role):
    endpoint = USER_ENDPOINT.format(userId=user)
    roles.append(new_role)
    json_body = json.dumps({'systemRoleIds': roles})
    resp = requests.patch(REST_HOSTNAME + endpoint, headers = auth_headers, data = json_body)
    if resp.status_code != 200:
	    print('Adding new role to {user} failed. Code: {status_code} Response: {text}'.format(user = user, status_code = resp.status_code, text = resp.text))
    else:
	    print('New system roles: ' + str(get_user_roles(PLACEHOLDER_USER)))

# Where the magic happens. Go through our user list and update with the given role.
for user in users:
    roles = get_user_roles(user)
    print('System roles for: ' + user)
    print(roles)
    print('Updating {user} with new role...'.format(user = user))
    update_user_roles(user, roles, new_role)

