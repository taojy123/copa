import datetime
import hashlib
import json
import os
import sys
import time
import traceback

import requests
import pyperclip


from trans import set_language, translate as _


def md5(content):
    if not content:
        return ''
    return hashlib.md5(content.encode()).hexdigest()


def api_request(conf, method, uri, data=None):
    host = conf['host']
    http_proxy = conf['http_proxy']
    https_proxy = conf['https_proxy']
    if http_proxy:
        proxies = {'http': http_proxy, 'https': https_proxy or http_proxy}
    else:
        proxies = None
    url = host + uri
    r = requests.request(method, url, data=data, proxies=proxies, verify=False)
    if r.status_code is not 200:
        print('WARNING:', r.text)
        return None
    return r.text


def get_config():
    conf = {
        'host': 'http://copa.tslow.cn',
        'token': 'public_test',
        'interval': 5,
        'language': 'en',
        'http_proxy': '',
        'https_proxy': '',
    }
    try:
        custom_conf = open('copaconf.json').read().lower()
        custom_conf = json.loads(custom_conf)
        conf.update(custom_conf)
    except:
        pass
    set_language(conf['language'])
    conf['interval'] = int(conf['interval'])
    if not conf['token']:
        print(_('Please set a token when your first time.'))
        print(_('If you run copa anywhere else, please set the same token, then clipboards will synchronize.'))
        conf['token'] = input(_('token:')).lower()
    return conf


def set_config(conf):
    conf = json.dumps(conf, ensure_ascii=False, indent=2)
    open('copaconf.json', 'w').write(conf)


# init
conf = get_config()

print('=================== copa v2 ====================')
print('HOST:', conf['host'])
print('TOKEN:', conf['token'])
print('INTERVAL:', conf['interval'])
print('LANGUAGE:', conf['language'])
print('HTTP_PROXY:', conf['http_proxy'])
print('HTTPS_PROXY:', conf['https_proxy'])
print('CURRENT DIR:', os.getcwd())
print('================================================')

set_config(conf)
last_hash = ''

try:
    api_request(conf, 'get', '/')
except Exception as e:
    print(e)
    print('ERROR:', _('the host is unavailable, please set the correct host in copaconf.json'))
    input()
    sys.exit(1)


while True:

    try:
        print('==========', datetime.datetime.now(), '==========')
        
        uri = f'/mirror/clipboards/{conf["token"]}/'

        curr_clip = pyperclip.paste()
        curr_hash = md5(curr_clip)
        print('last hash:', last_hash)
        print('curr hash:', curr_hash)
        
        if curr_hash and curr_hash != last_hash:
            data = {
                'content': curr_clip,
                'hash': curr_hash,
            }
            res = api_request(conf, 'post', uri, data)
            if res:
                print(_('set clipboard successful'))
                last_hash = curr_hash
        
        remote_hash = api_request(conf, 'get', uri + '?target=hash')
        print('remote hash:', remote_hash)
        
        if remote_hash and remote_hash != last_hash:
            content = api_request(conf, 'get', uri)
            pyperclip.copy(content)
            last_hash = remote_hash
            print(_('get newest clipboard from remote'))
        
    except:
        print('================== error ==================')
        traceback.print_exc()
        # input(_('Press enter to exit'))
        
    finally:
        time.sleep(conf['interval'])



