import hashlib
import json
import os
import io
import shutil
import sys
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


def status(savepoint=False, conflict=False, latest=False, limit=5):
    url = HOST + '/mirror/status/'
    data = {
        'name': NAME,
        'savepoint': savepoint or '',
        'conflict': conflict or '',
        'latest': latest or '',
        'limit': limit,
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

    if savepoint:
        print('as savepoint')

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


def show(content):
    if content == 'config':
        conf = get_config()
        print(json.dumps(conf, ensure_ascii=False, indent=2))
    elif content == 'hash':
        get_last_hash()


def dome_command():
    print('\n------------------------------------------')
    print('1. show info [default]')
    print('2. show remote commits')
    print('3. pull remote commit to local')
    print('4. push local to remote commit')
    print('5. quit')

    choice = input('chose a number: ').strip() or '1'

    if choice == '1':
        print('HOST:', HOST)
        print('NAME:', NAME)
        print('BASE_DIR:', BASE_DIR)
        print('PACKAGE_DIR:', PACKAGE_DIR)
        get_last_hash()

    elif choice == '2':
        print('1. only savepoint commits')
        print('2. only conflict commits')
        print('3. all kind of commits [default]')

        choice = input('chose a number: ').strip() or '3'

        savepoint = choice == '1'
        conflict = choice == '2'
        limit = input('how many commits need to show? [default: 5]: ') or 5

        packages = status(savepoint, conflict, limit=limit)
        latest = True
        for package in packages:
            print('--------------------------------')
            print('commit time:', package['created_at'])
            print('hash:', package['hash'])
            print('package size:', package['content_length'])
            if package['savepoint']:
                print('*savepoint')
            if package['conflict']:
                print('*conflict')
            if latest:
                print('*latest')
            latest = False

    elif choice == '3':

        hash = input('hash of commit to pulled [default: last commit]: ')
        target = input('pull to path [default: current project]: ')
        pull(hash, target)

    elif choice == '4':

        savepoint = input('as a savepoint? (yes / no[default]): ').strip()
        savepoint = savepoint == 'yes' or savepoint == 'y'
        push(savepoint)

    elif choice == '5':
        print('bye!')
        return False

    else:
        print('please enter a number of 1,2,3,4,5')

    return True


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
conf = get_config()
HOST = conf.get('host') or 'http://dome.k8s.tslow.cn'
NAME = conf.get('name') or input('Project Name: ')
INTERVAL = conf.get('interval') or 5
MANUAL = conf.get('manual', 0)
PACKAGE_DIR = os.path.join(BASE_DIR, NAME)


print('============== dome v1 ===============')
print('HOST:', HOST)
print('NAME:', NAME)
print('INTERVAL:', INTERVAL)
print('MANUAL:', MANUAL)
print('BASE_DIR:', BASE_DIR)
print('PACKAGE_DIR:', PACKAGE_DIR)
print('======================================')


conf['host'] = HOST
conf['name'] = NAME
conf['interval'] = INTERVAL
conf['manual'] = MANUAL
set_config(conf)


try:
    requests.get(HOST)
except Exception as e:
    print('the host is unavailable!')
    print(e)
    sys.exit(0)


try:
    INTERVAL = int(INTERVAL)
    if not os.path.exists(PACKAGE_DIR):
        os.mkdir(PACKAGE_DIR)
        print('init pull')
        pull()
        print('======================================')
except Exception as e:
    print('the init failed!')
    print(e)
    sys.exit(0)


try:
    if MANUAL:
        print('------ Manual Mode ------')
        while True:
            try:
                if not dome_command():
                    break
            except:
                traceback.print_exc()

    else:
        print('------ Auto Run Mode ------')
        while True:

            time.sleep(INTERVAL)

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
    input('Press enter to exit')





