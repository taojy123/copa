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
        # print(rf'{translate_function_name}\((.+?)\)')
        for r in rs:
            print(r)


TRANSLATE_MAP['zh'] = {
    'Can not pull to a exists dir!': '无法拉取云端数据到一个已存在的目录',
    '1. show project info [default]': '1. 显示项目信息 [默认]',
    '2. show remote commits': '2. 显示云端的推送记录列表',
    '3. pull remote commit to local': '3. 拉取云端的数据到本地',
    '4. push local to remote commit': '4. 推送本地当前的数据至云端',
    '5. quit': '5. 退出',
    'chose a number:': '数字选项:',
    '1. only savepoint commits': '1. 只显示保存点',
    '2. only conflict commits': '2. 只显示冲突点',
    '3. all kind of commits [default]': '3. 不作限制 [默认]',
    'how many commits need to show? [default: 5]:': '最多显示多少条记录? [默认为最近的5条]:',
    'commit time:': '推送时间:',
    'hash:': 'hash 值:',
    'package size:': '数据包大小:',
    '*savepoint': '*保存点',
    '*conflict': '*冲突点',
    '*latest': '*最新记录点',
    'hash of commit to pulled [default: last commit]:': '要拉取的云端记录 hash 值 [默认为最新记录点]:',
    'pull to path [default: current project]:': '拉取到本地哪个目录 [默认为当前项目目录]:',
    'as a savepoint? yes / no[default]:': '是否作为 “保存点” 推送? 请输入 yes 或 no [默认为 no]:',
    'bye!': '再见!',
    'please enter a number of 1,2,3,4,5': '请选择 1,2,3,4,5 中的一个数字',
    'to avoid data loss, do not set an existing directory to the project name for the first time!': '为避免数据丢失，首次使用时，请不要将一个已存在的目录设置为项目目录!',
    'Project Name:': '项目目录名:',
    'the host is unavailable, please set the correct host in domeconf.json': '云端服务器不可用，请在 domeconf.json 中设置正确的 host',
    'init pull': '项目初始化，拉取云端数据',
    'the init failed!': '项目初始化失败',
    '------ Manual Mode ------': '------ 手动模式 ------',
    '------ Auto Run Mode ------': '------ 自动模式 ------',
    'Press enter to exit': '按下回车键退出',
    'project name is invalid, please change it in domeconf.json': '项目名称不合法，请在 domeconf.json 更改设置',
}


if __name__ == '__main__':
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
