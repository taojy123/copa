import hashlib
import os
import io
import zipfile

import requests


HOST = 'http://127.0.0.1:8000'


def push(savepoint=False):
    package = io.BytesIO()
    zip = zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk('..'):
        if '.dome' in path:
            continue
        fpath = path.replace('..', '').strip().strip('/').strip('\\')
        print(fpath, filenames)
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.close()

    package.seek(0)
    content = package.read()
    package.seek(0)

    files = {'package': package}
    name = os.path.basename(os.path.abspath('..'))
    hash = hashlib.md5(content).hexdigest()
    data = {
        'name': name,
        'hash': hash,
        'savepoint': savepoint,
    }
    url = f'{HOST}/mirror/push/'
    r = requests.post(url, json=data, files=files)
    print(r.status_code, r.text)

    if 'size must less than' in r.text:
        raise AssertionError(r.text)


# push()

while True:
    pass




