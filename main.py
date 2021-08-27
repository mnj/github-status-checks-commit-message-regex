##### Imports #####
import re
import sys
import os
import json
import requests
from distutils.util import strtobool
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Expected script args:
# sys.argv[1] - Pattern (string)
# sys.argv[2] - Check commit title (bool)
# sys.argv[3] - Check commit body (bool)
# sys.argv[5] - Check commit message (bool)
# sys.argv[6] - Check all commits (bool)
# sys.argv[7] - Github token (string)

# Check if the argument exists, (and convert them to Python booleans), 
# if they are not present, then set them to some sane defaults
pattern = sys.argv[1] if (len(sys.argv) >= 2) else None
check_commit_title = bool(strtobool(sys.argv[2])) if len(sys.argv) >= 3 else False
check_commit_body = bool(strtobool(sys.argv[3])) if len(sys.argv) >= 4 else False
check_commit_message = bool(strtobool(sys.argv[4])) if len(sys.argv) >= 5 else True
check_all_commits = bool(strtobool(sys.argv[5])) if len(sys.argv) >= 6 else False
github_token = sys.argv[6] if len(sys.argv) >= 7 else None

##### Functions #####
def check_valid_title(pull_request_json):
    if "title" in pull_request_json:
        # Check that it's not set to null/empty
        if pull_request_json['title'] is not None:
            return re.search(pattern, pull_request_json['title'])
        else:
            return False # Didn't contain anything/exist, so cant be valid
    else:
        raise SystemExit('Did not find the expected title elemment in the pull request event data!')

def check_valid_title_from_api(github_commits_from_api_json):
    if "commit" in github_commits_from_api_json:
        if "message" in github_commits_from_api_json['commit']:
            title = github_commits_from_api_json['commit']['message'].splitlines()[0]
            
            if title is not None:
                return re.search(pattern, title)
            else:
                return False # Didn't contain anything/exist, so cant be valid

def check_valid_body_from_api(github_commits_from_api_json):
    if "commit" in github_commits_from_api_json:
        if "message" in github_commits_from_api_json['commit']:
            body = '\n'.join(github_commits_from_api_json['commit']['message'].splitlines()[1:])
            
            if body is not None:
                return re.search(pattern, body)
            else:
                return False # Didn't contain anything/exist, so cant be valid

def check_valid_message_from_api(github_commits_from_api_json):
    if "commit" in github_commits_from_api_json:
        if "message" in github_commits_from_api_json['commit']:
            if github_commits_from_api_json['commit']['message'] is not None:
                return re.search(pattern, github_commits_from_api_json['commit']['message'])
            else:
                return False # Didn't contain anything/exist, so cant be valid

def check_valid_body(pull_request_json):
    if "body" in pull_request_json:
        # Check that it's not set to null/empty
        if pull_request_json['body'] is not None:
            return re.search(pattern, pull_request_json['body'])
            
        else:
            return False # Didn't contain anything/exist, so cant be valid
    else:
        raise SystemExit('Did not find the expected body elemment in the pull request event data!')

def check_valid_message(pull_request_json):
    full_message = ""
    
    if "title" in pull_request_json:
        if pull_request_json['title'] is not None:
            full_message += pull_request_json['title']
    if "body" in pull_request_json:
        if pull_request_json['body'] is not None:
            full_message += "\n" + pull_request_json['body']

    if full_message == "":
        raise SystemExit('Both the title and body of the commit message can not be empty!')
    else:
        return re.search(pattern, full_message)

def get_pull_request_json():
    try:
        # Try to open the event file (json) that is specified with the environment
        # varible: GITHUB_EVENT_PATH, this will contain the pull request details
        # but it will not list each individual commit message, for that we need to
        # use the python github client, with required the GITHUB_TOKEN to work.

        # Check if the GITHUB_EVENT_PATH environment variable has been set
        if "GITHUB_EVENT_PATH" in os.environ:

            # Open the event json file, and parse it with json
            with open(os.environ['GITHUB_EVENT_PATH'], 'r') as event_file:
                event_data = json.load(event_file)
                
                # Check that we are actually running on a pull request status check
                if "pull_request" in event_data:
                    return event_data['pull_request']
                else:
                    raise SystemExit('There was no pull request data in the triggered event!')
        else:
            raise SystemExit('Missing the GITHUB_EVENT_PATH environment variable!')
    except:
        raise SystemExit('Unable to parse the pull request!')

def get_github_commits_from_api(pull_request_json):
    if "commits_url" in pull_request_json:
        auth_headers = {"Authorization": f"token {github_token}"}

        try:
            session = requests.Session()
            retries = Retry(total=10, backoff_factor=1, status_forcelist=[ 404, 429, 500, 502, 503, 504 ])
            session.mount('https://', HTTPAdapter(max_retries=retries))

            resp = session.get(pull_request_json['commits_url'], headers=auth_headers)
            if resp.status_code == 200:
                return resp.json()
            else:
                raise SystemExit('Recieved unknown response code from the Github REST API!')
        except:
            raise SystemExit('Could not talk to the Github API, gave up after 10 retries!')
    else:
        raise SystemExit('The event file did not contain a commits_url element!')

##### Main #####
if __name__ == '__main__':
    valid_pull_request = True # Assume true, unless checks fail

    pull_request_json = get_pull_request_json()
    
    if check_all_commits:
        # Get a json list of commmits, they dont contain title/body, so we need to parse that ourself
        github_api_commits = get_github_commits_from_api(pull_request_json)

        # Go through each commit and see if they are valid
        for commit in github_api_commits:
            if check_commit_title:
                if not check_valid_title_from_api(commit):
                    valid_pull_request = False
            
            if check_commit_body:
                if not check_valid_body_from_api(commit):
                    valid_pull_request = False   
            
            if check_commit_message:
                if not check_valid_message_from_api(commit):
                    valid_pull_request = False
    else:
        # We can rely on just the pull request json without having to use PyGithub
        if check_commit_title:
            if not check_valid_title(pull_request_json):
                valid_pull_request = False

        if check_commit_body:
            if not check_valid_body(pull_request_json):
                valid_pull_request = False

        if check_commit_message:
            if not check_valid_message(pull_request_json):
                valid_pull_request = False

    if valid_pull_request:
        sys.exit(0)
    else:
        raise SystemExit('You did not specify a Jira ticket number in this pull request!')
