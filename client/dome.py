import json
import os
import sys
import time
import traceback

import requests
import pyperclip


from trans import set_language, translate as _


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
        'host': 'http://dome.k8s.tslow.cn',
        'token': '',
        'interval': 5,
        'language': 'en',
        'http_proxy': '',
        'https_proxy': '',
    }
    try:
        custom_conf = open('domeconf.json').read().lower()
        custom_conf = json.loads(custom_conf)
        conf.update(custom_conf)
    except:
        pass
    conf['interval'] = int(conf['interval'])
    if not conf['token']:
        print(_('Please set a token when your first time.'))
        print(_('If you run dome anywhere else, please set the same token, then clipboards will synchronize.'))
        conf['token'] = input(_('token:')).lower()
    return conf


def set_config(conf):
    conf = json.dumps(conf, ensure_ascii=False, indent=2)
    open('domeconf.json', 'w').write(conf)


# init
conf = get_config()

print('=================== dome v2 ====================')
print('HOST:', conf['host'])
print('TOKEN:', conf['token'])
print('INTERVAL:', conf['interval'])
print('LANGUAGE:', conf['language'])
print('HTTP_PROXY:', conf['http_proxy'])
print('HTTPS_PROXY:', conf['https_proxy'])
print('CURRENT DIR:', os.getcwd())
print('================================================')

set_config(conf)
set_language(conf['language'])
lastclip = ''


try:
    api_request(conf, 'get', '/')
except Exception as e:
    print(e)
    print('ERROR:', _('the host is unavailable, please set the correct host in domeconf.json'))
    input()
    sys.exit(1)


while True:

    try:

        time.sleep(conf['interval'])
        uri = f'/mirror/clipboards/{conf["token"]}/'

        currclip = pyperclip.paste()
        if currclip and currclip != lastclip:
            data = {
                'content': currclip,
            }
            res = api_request(conf, 'post', uri, data)
            if res:
                print(_('set clipboard successful'))
                lastclip = currclip

        content = api_request(conf, 'get', uri)
        if content and content != lastclip:
            lastclip = content
            pyperclip.copy(lastclip)
            print(_('get newest clipboard from remote'))

        print('======================================')

    except:
        print('================== error ==================')
        traceback.print_exc()
        # input(_('Press enter to exit'))



