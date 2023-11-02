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




