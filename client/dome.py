import hashlib
import json
import os
import io
import shutil
import time
import traceback
import zipfile

import requests


def package_files(target=''):
    target = target or PACKAGE_DIR

    abs_file_list = []
    rel_file_list = []
    for path, dirnames, filenames in os.walk(target):
        rpath = path.replace(target, '').strip().strip('/').strip('\\')
        for filename in filenames:
            abs_file = os.path.join(path, filename)
            rel_file = os.path.join(rpath, filename)
            rel_file = rel_file.replace('\\', '/')
            abs_file_list.append(abs_file)
            rel_file_list.append(rel_file)
    abs_file_list.sort()
    rel_file_list.sort()

    assert len(abs_file_list) == len(rel_file_list)

    return abs_file_list, rel_file_list


def package_hash(target=''):
    target = target or PACKAGE_DIR

    abs_file_list, rel_file_list = package_files(target)

    if not rel_file_list:
        return ''

    filenames = '|'.join(rel_file_list)
    hash = hashlib.md5(filenames.encode()).hexdigest()
    for filename in abs_file_list:
        content = open(filename, 'rb').read()
        hash += hashlib.md5(content).hexdigest()
    hash = hashlib.md5(hash.encode()).hexdigest()

    return hash


def get_last_hash():
    open('domehash.txt', 'a')
    lasthash = open('domehash.txt').read().strip()
    print('local last hash:', lasthash)
    return lasthash


def set_last_hash(hash=''):
    hash = hash or package_hash()
    open('domehash.txt', 'w').write(hash)
    print('set last hash:', hash)
    return hash


def status(savepoint=False, conflict=False, latest=False):
    url = HOST + '/mirror/status/'
    data = {
        'name': NAME,
        'savepoint': savepoint or '',
        'conflict': conflict or '',
        'latest': latest or '',
    }
    r = requests.post(url, data)
    # print(r.text)
    r = r.json()
    packages = r['packages']
    # print(json.dumps(packages, indent=2, ensure_ascii=False))
    if latest:
        return packages[0] if packages else None
    return packages


def push(savepoint=False):
    print('=== Push ===')

    package = io.BytesIO()
    zipf = zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED)
    abs_file_list, rel_file_list = package_files()
    for abs_file, rel_file in zip(abs_file_list, rel_file_list):
        print('pack:', abs_file, '->', rel_file)
        zipf.write(abs_file, rel_file)
    zipf.close()
    package.seek(0)
    hash = package_hash()

    print('push current hash:', hash)

    url = HOST + '/mirror/push/'
    data = {
        'name': NAME,
        'hash': hash,
        'savepoint': savepoint or '',
    }
    files = {'package': package}
    r = requests.post(url, data, files=files)
    if r.status_code is not 200:
        print('ERROR:', r.text)
        return

    print('push success')
    return set_last_hash(hash)


def pull(hash='', target=''):
    print('=== PULL ===')

    url = HOST + '/mirror/pull/'
    data = {
        'name': NAME,
        'hash': hash
    }
    r = requests.post(url, data)
    if r.status_code is not 200:
        print('ERROR:', r.text)
        return

    package = io.BytesIO(r.content)

    if target:
        if os.path.exists(target):
            print('Can not pull to a exists dir!')
            return
    else:
        target = PACKAGE_DIR

    print(f'load {hash or "latest"} to {target}')
    zipf = zipfile.ZipFile(package, 'r')
    file_list = zipf.namelist()
    for file in file_list:
        print('extract:', file)
        zipf.extract(file, target)
    zipf.close()

    abs_file_list, rel_file_list = package_files()
    for abs_file, rel_file in zip(abs_file_list, rel_file_list):
        if rel_file not in file_list:
            print('remove:', rel_file, '<-->', abs_file)
            try:
                os.remove(abs_file)
            except Exception as e:
                print('remove file failed:', e)

    return set_last_hash(hash)


def get_config():
    try:
        conf = open('domeconf.json').read().lower()
        conf = json.loads(conf)
    except:
        conf = {}
    return conf


def set_config(conf):
    conf = json.dumps(conf, ensure_ascii=False, indent=2)
    open('domeconf.json', 'w').write(conf)


def entry_project_name():
    while True:
        name = input('Project Name: ')
        if '/' in name or '\\' in name:
            continue
        if not name:
            continue
        return name


try:

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    conf = get_config()
    HOST = conf.get('host') or 'http://127.0.0.1:8000'
    NAME = conf.get('name') or input('Project Name: ')
    PACKAGE_DIR = os.path.join(BASE_DIR, NAME)


    print('============== dome v1 ===============')
    print('HOST:', HOST)
    print('NAME:', NAME)
    print('BASE_DIR:', BASE_DIR)
    print('PACKAGE_DIR:', PACKAGE_DIR)
    print('======================================')

    conf['host'] = HOST
    conf['name'] = NAME
    set_config(conf)


    if not os.path.exists(PACKAGE_DIR):
        os.mkdir(PACKAGE_DIR)
        print('init pull')
        pull()
        print('======================================')



    if conf.get('manual', False):
        print('Manual Mode')
        status()
        # pull('2adb233171254de1d624065c43c212ac', 'ttt2')
        pass

    else:
        print('Auto Run Mode')
        while True:

            time.sleep(5)

            lasthash = get_last_hash()
            currhash = package_hash()
            print('local current hash:', currhash)

            if currhash and currhash != lasthash:
                lasthash = push()

            r = status(latest=True)
            remote_lasthash = r and r['hash']
            print('remote last hash:', remote_lasthash)
            if remote_lasthash != lasthash:
                lasthash = pull()
                if remote_lasthash != lasthash:
                    print('WARNING: pulling hash not matched:', lasthash)

            print('======================================')

except:
    print('================== error ==================')
    traceback.print_exc()
    input()





