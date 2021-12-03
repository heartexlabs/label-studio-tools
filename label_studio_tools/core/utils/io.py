import logging
import io
import urllib
import hashlib
import requests
import os

from appdirs import user_cache_dir, user_data_dir
from urllib.parse import urlparse

_DIR_APP_NAME = 'label-studio'

logger = logging.getLogger(__name__)


def get_data_dir():
    data_dir = user_data_dir(appname=_DIR_APP_NAME)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_cache_dir():
    cache_dir = user_cache_dir(appname=_DIR_APP_NAME)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_local_path(url, cache_dir=None, project_dir=None, hostname=None, image_dir=None, access_token=None):
    is_local_file = url.startswith('/data/') and '?d=' in url
    is_uploaded_file = url.startswith('/data/upload')
    if image_dir is None:
        upload_dir = os.path.join(get_data_dir(), 'media', 'upload')
        image_dir = project_dir and os.path.join(project_dir, 'upload') or upload_dir

    # File reference created with --allow-serving-local-files option
    if is_local_file:
        filename, dir_path = url.split('/data/')[1].split('?d=')
        dir_path = str(urllib.parse.unquote(dir_path))
        filepath = os.path.join(dir_path, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)
        return filepath

    # File uploaded via import UI
    elif is_uploaded_file and os.path.exists(image_dir):
        project_id = url.split("/")[-2]  # To retrieve project_id
        image_dir = os.path.join(image_dir, project_id)
        filepath = os.path.join(image_dir, os.path.basename(url))
        return filepath

    elif is_uploaded_file and hostname:
        url = hostname + url
        logger.info('Resolving url using hostname [' + hostname + '] from LSB: ' + url)

    elif is_uploaded_file:
        raise FileNotFoundError("Can't resolve url, neither hostname or project_dir passed: " + url)

    if is_uploaded_file and not access_token:
        raise FileNotFoundError("Can't access file, no access_token provided for Label Studio Backend")

    # File specified by remote URL - download and cache it
    cache_dir = cache_dir or get_cache_dir()
    parsed_url = urlparse(url)
    url_filename = os.path.basename(parsed_url.path)
    url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    filepath = os.path.join(cache_dir, url_hash + '__' + url_filename)
    if not os.path.exists(filepath):
        logger.info('Download {url} to {filepath}'.format(url=url, filepath=filepath))
        headers = {'Authorization': 'Token ' + access_token} if access_token else {}
        r = requests.get(url, stream=True, headers=headers)
        r.raise_for_status()
        with io.open(filepath, mode='wb') as fout:
            fout.write(r.content)
    return filepath