import re
import sys

LANGUAGE_CODE = 'en'
TRANSLATE_MAP = {'en': {}}


def set_language(code):
    global LANGUAGE_CODE
    LANGUAGE_CODE = code
    if LANGUAGE_CODE not in TRANSLATE_MAP:
        print(f'WARNING: the language {code} can not be translated!')


def get_language():
    return LANGUAGE_CODE


def translate(text):
    if not isinstance(text, str):
        return text
    if LANGUAGE_CODE not in TRANSLATE_MAP:
        return text
    t = TRANSLATE_MAP[LANGUAGE_CODE]
    isinstance(t, dict)
    return t.get(text, text)


def text_finder(filename, translate_function_name='translate'):
    lines = open(filename).readlines()
    for line in lines:
        rs = re.findall(rf'{translate_function_name}\((.+?)\)', line)
        for r in rs:
            print(r)


TRANSLATE_MAP['zh'] = {
    'Please set a token when your first time.': '第一次运行时请设置一个属于你的 token',
    'If you run dome anywhere else, please set the same token, then clipboards will synchronize.': '如果你已经在其他地方运行了 dome，那么请输入与之前相同的 token，这样你的剪切板就可以实时同步啦！',
    'the host is unavailable, please set the correct host in domeconf.json': '服务器不可用，请检查 domeconf.json 中的 host 配置项',
    'Press enter to exit': '按下回车退出',
}

if __name__ == '__main__':
    """ usage: python trans.py [translate]
    """

    args = sys.argv[1:]

    if len(args) > 0:
        filename = args[0]
    else:
        print('miss target filename')
        sys.exit(1)

    if len(args) > 1:
        translate_function_name = args[1]
    else:
        translate_function_name = 'translate'

    text_finder(filename, translate_function_name)

