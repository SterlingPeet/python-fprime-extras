from appdirs import AppDirs
from datetime import datetime
from datetime import timedelta
import json
import requests
import os

repository = 'https://api.github.com/repos/SterlingPeet/python-fprime-extras'
params = 'Accept: application/vnd.github.v3+json'
cache_dir = AppDirs('fprime-extras', 'SterlingPeet').user_cache_dir

def get_github_version(repository=repository, params=params, branch='main'):
    """Get the SHA of the latest commit in the specified branch on GH."""
    cache_expired = False
    gh_sha = None
    version_cache_file = cache_dir + os.sep + 'version.json'
    # print('version cache file: {}'.format(version_cache_file))
    try:
        with open(version_cache_file, 'r') as cache:
            version_dict = json.load(cache)
            # print("cached...")
            # print(version_dict)
            t_delta = datetime.now() - datetime.fromisoformat(version_dict['timestamp'])
            # print(t_delta)
            gh_sha = version_dict['sha']
            if t_delta > timedelta(hours=1):
                # print("cache is expired, updating...")
                cache_expired = True
    except:
        cache_expired = True

    if cache_expired:
        # print(" ** ** Updating the Cache File")
        resp = requests.get(url='{}/branches/{}'.format(repository, branch), params=params)
        gh_sha = resp.json()['commit']['sha']
        version_dict = {'sha': gh_sha,
                        'timestamp': datetime.now().isoformat()}
        # print(version_dict)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        with open(version_cache_file, 'w') as cache:
            json.dump(version_dict, cache)
    return gh_sha

def check_version(sha, branch='main'):
    """Return False if the given SHA matches the latest commit on GH."""
    gh_sha = get_github_version(branch=branch)
    # print(gh_sha)
    # print(gh_sha[0:len(sha)])
    return sha != gh_sha[0:len(sha)]

def nag(version, branch):
    """Ask to update, if this commit doesn't match github."""
    try:
        if check_version(version.split('-')[2][1:], branch):
            print('***')
            print('*** Your version of this program is: {}'.format(version))
            print('*** This does not match the latest commit in the upstream')
            print('*** GitHub repository.  To update:')
            print('***')
            print('***    cd /path/to/python-fprime-extras')
            print('***    git pull')
            print('***    pip install .')
            print('***')
    except Exception as e:
        print('***')
        print('*** There was an error checking the upstream repository for updates,')
        print('*** please double check that you have the latest version of')
        print('*** fprime-extras installed.')
        print('***')
