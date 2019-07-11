import hashlib
import json
import os
import io
import time
import zipfile

import requests


HOST = 'http://127.0.0.1:8000'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NAME = os.path.basename(BASE_DIR)
IGNORE = ['dome', 'requirements.txt']

open('domeconf.json', 'a')
s = open('domeconf.json').read().strip()
if s:
    conf = json.loads(s)
    for key, value in conf.items():
        if not value:
            continue
        locals()[key.upper()] = value


print('============== dome v1 ===============')
print('HOST:', HOST)
print('BASE_DIR:', BASE_DIR)
print('NAME:', NAME)
print('IGNORE:', IGNORE)
print('======================================')


def file_finder(silent=True):
    for path, dirnames, filenames in os.walk(BASE_DIR):
        rpath = path.replace(BASE_DIR, '').strip().strip('/').strip('\\')
        for filename in filenames:
            skip = False
            for item in IGNORE:
                if item in filename:
                    skip = True
                    break
            if skip:
                continue
            abs_file = os.path.join(path, filename)
            rel_file = os.path.join(rpath, filename)
            if not silent:
                print(rel_file)
            yield abs_file, rel_file


def current_package(silent=True):
    package = io.BytesIO()
    zip = zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED)
    for abs_file, rel_file in file_finder(silent):
        zip.write(abs_file, rel_file)
    zip.close()
    hash = get_package_hash(package)
    return package, hash


def get_package_hash(package):
    package.seek(0)
    content = package.read()
    hash = hashlib.md5(content).hexdigest()
    package.seek(0)
    return hash


def get_last_hash():
    lasthash = open('domehash.txt').read().strip()
    print('get hash:', lasthash)
    return lasthash


def set_last_hash():
    package, lasthash = current_package()
    open('domehash.txt', 'w').write(lasthash)
    print('set hash:', lasthash)
    return lasthash


def status(savepoint='', conflict='', latest=''):
    print('status')
    url = HOST + '/mirror/status/'
    data = {
        'name': NAME,
        'savepoint': savepoint,
        'conflict': conflict,
        'latest': latest,
    }
    r = requests.post(url, data)
    # print(r.text)
    r = r.json()
    packages = r['packages']
    print(json.dumps(packages, indent=2, ensure_ascii=False))
    if latest:
        return packages[0] if packages else None
    return packages


def push(savepoint=False):
    print('push')
    package, hash = current_package(False)
    url = HOST + '/mirror/push/'
    data = {
        'name': NAME,
        'hash': hash,
        'savepoint': savepoint,
    }
    files = {'package': package}
    r = requests.post(url, data, files=files)
    print(r.status_code, r.text)
    if 'size must less than' in r.text:
        raise AssertionError(r.text)
    return set_last_hash()


def pull(hash=''):
    print('pull')
    url = HOST + '/mirror/pull/'
    data = {
        'name': NAME,
        'hash': hash
    }
    r = requests.post(url, data)
    package = io.BytesIO(r.content)

    print('---------- removing ----------')
    for abs_file, rel_file in file_finder(False):
        os.remove(abs_file)
    print('------------------------------')

    zip = zipfile.ZipFile(package, 'r')
    for file in zip.namelist():
        zip.extract(file, BASE_DIR)
    zip.close()
    return set_last_hash()


while True:

    time.sleep(5)
    lasthash = get_last_hash()
    package, currhash = current_package()

    if currhash != lasthash:
        lasthash = push()

    r = status(latest='1')
    if r and r['hash'] != lasthash:
        lasthash = pull()

    print('======================================')











