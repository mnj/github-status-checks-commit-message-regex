import re
import sys
import os
import json

re_match_title = None
re_match_body = None

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

                # Check if there is a title element (first line of the git commit message)
                if "title" in event_data['pull_request']:

                    # Check that it's not set to null/empty
                    if event_data['pull_request']['title'] is not None:
                    
                        # Get the match result, for the regex search, based on the pattern in argv[1]
                        re_match_title = re.search(sys.argv[1], event_data['pull_request']['title'])

                # Check if there is a body element (the rest of the commit message, excl the first line)
                if "body" in event_data['pull_request']:

                    # Check that it's not set to null/empty
                    if event_data['pull_request']['body'] is not None:

                        # Get the match result, for the regex search, based on the pattern in argv[1]
                        re_match_body = re.search(sys.argv[1], event_data['pull_request']['body'])
except:
    raise SystemExit('Unable to parse the pull request!')

# Return success if there was a regex match in either the title or body or both
if (re_match_title is not None) or (re_match_body is not None):
    sys.exit(0)
else:
    raise SystemExit('You did not specify a Jira ticket number in this pull request!')
