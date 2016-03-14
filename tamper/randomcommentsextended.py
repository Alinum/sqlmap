#!/usr/bin/env python

"""
Copyright (c) 2006-2016 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import re

from lib.core.common import randomRange, randomStr
from lib.core.data import kb
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOW

def tamper(payload, **kwargs):
    """
    Add random comments to SQL keywords

    >>> import random
    >>> random.seed(0)
    >>> tamper('INSERT')
    'IN/*rUurBCvJ*/SERT'
    """

    retVal = payload

    if payload:
        for match in re.finditer(r"\b[A-Za-z_]+\b", payload):
            word = match.group()

            if len(word) < 2:
                continue

            if word.upper() in kb.keywords:
                _ = word[0]

                for i in xrange(1, len(word) - 1):
                    _ += "%s%s" % ("/*" + randomStr(randomRange(3, 8)) + "*/" if randomRange(0, 1) else "", word[i])

                _ += word[-1]

                if "/*" not in _:
                    index = randomRange(1, len(word) - 1)
                    _ = word[:index] + "/*" + randomStr(randomRange(3, 8)) + "*/" + word[index:]

                retVal = retVal.replace(word, _)

    return retVal
