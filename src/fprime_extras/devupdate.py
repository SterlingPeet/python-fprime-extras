import json
import logging
import os
from datetime import datetime
from datetime import timedelta

import requests

from .core.conf import cache_dir

repository = 'https://api.github.com/repos/SterlingPeet/python-fprime-extras'
params = 'Accept: application/vnd.github.v3+json'
version_cache_file = cache_dir + os.sep + 'version.json'
log = logging.getLogger(__name__)
cache_expiry_delta = timedelta(hours=1)


def get_github_version(repository=repository, params=params, branch='main'):
    """Get the SHA of the latest commit in the specified branch on GH."""
    cache_expired = False
    gh_sha = None
    log.debug('version cache file: {}'.format(version_cache_file))
    try:
        with open(version_cache_file, 'r') as cache:
            version_dict = json.load(cache)
            log.debug('cached version dict: {}'.format(version_dict))
            t_delta = datetime.now() - \
                datetime.fromisoformat(version_dict['timestamp'])
            log.debug('time delta from last HTTP request: {}'.format(t_delta))
            gh_sha = version_dict['sha']
            if t_delta > cache_expiry_delta:
                log.debug("cache is expired, {} is greater than {}, updating...".format(t_delta, cache_expiry_delta))
                cache_expired = True
    except Exception as e:  # TODO: MORE SPECIFIC!!!
        log.warning("get_github_version exception: %s", e)
        cache_expired = True

    if cache_expired:
        version_dict = {'timestamp': datetime.now().isoformat()}
        version_dict['repository'] = repository
        version_dict['branch'] = branch
        version_dict['params'] = params
        resp = requests.get(
            url='{}/branches/{}'.format(repository, branch), params=params)
        try:
            gh_sha = resp.json()['commit']['sha']
            version_dict['sha'] = gh_sha
            version_dict['status'] = 'Check Successful'
        except Exception as e:  # TODO: MORE SPECIFIC!!!
            log.warning('get_github_version json exception: %s', e)
            log.warning('request response: {}'.format(resp))
            version_dict['sha'] = gh_sha
            version_dict['status'] = 'Bad HTTP Response: {}'.format(str(resp))
        # log.debug(version_dict)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        with open(version_cache_file, 'w') as cache:
            json.dump(version_dict, cache)
    return gh_sha


def check_version(sha, branch='main'):
    """Return False if the given SHA matches the latest commit on GH."""
    gh_sha = get_github_version(branch=branch)
    if gh_sha is None:
        log.error('***')
        log.error('*** The git branch of your installation may not exist in the')
        log.error('*** upstream repository, or your internet connection may have')
        log.error('*** been down at the last check.')
    _ret = sha != gh_sha[0:len(sha)]
    if _ret:
        log.info('github sha: {}'.format(gh_sha))
    return _ret


def nag(version, branch):
    """Ask to update, if this commit doesn't match github."""
    try:
        if check_version(version.split('-')[1][1:], branch):
            log.error('***')
            log.error('*** Your version of this program is: {}'.format(version))
            log.error('*** This does not match the latest commit in the upstream')
            log.error('*** GitHub repository.  To update:')
            log.error('***')
            log.error('***    cd /path/to/python-fprime-extras')
            log.error('***    git pull')
            log.error('***    pip install .')
            log.error('***')
    except Exception as e:  # TODO: MORE SPECIFIC!!!
        log.error('***')
        log.error('*** There was an error checking the upstream repository for updates,')
        log.error('*** please double check that you have the latest version of')
        log.error('*** fprime-extras installed.')
        log.error('***')
        raise e
