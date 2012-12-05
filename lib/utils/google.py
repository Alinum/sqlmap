#!/usr/bin/env python

"""
Copyright (c) 2006-2012 sqlmap developers (http://sqlmap.org/)
See the file 'doc/COPYING' for copying permission
"""

import cookielib
import httplib
import re
import socket
import urllib
import urllib2

from lib.core.common import getUnicode, urlencode
from lib.core.data import conf, logger
from lib.core.exception import sqlmapConnectionException, sqlmapGenericException
from lib.core.settings import GOOGLE_REGEX, UNICODE_ENCODING, decodePage

class Google(object):
    """
    This class defines methods used to perform Google dorking (command
    line option '-g <google dork>'
    """

    def __init__(self, handlers):
        self._cj = cookielib.CookieJar()

        handlers.append(urllib2.HTTPCookieProcessor(self._cj))

        self.opener = urllib2.build_opener(*handlers)
        self.opener.addheaders = conf.httpHeaders

        try:
            conn = self.opener.open("http://www.google.com/ncr")
            _ = conn.info()  # retrieve session cookie
        except urllib2.HTTPError, e:
            _ = e.info()
        except urllib2.URLError:
            errMsg = "unable to connect to Google"
            raise sqlmapConnectionException, errMsg

    def search(self, dork):
        """
        This method performs the effective search on Google providing
        the google dork and the Google session cookie
        """

        gpage = conf.googlePage if conf.googlePage > 1 else 1
        logger.info("using Google result page #%d" % gpage)

        if not dork:
            return None

        url = "http://www.google.com/search?"
        url += "q=%s&" % urlencode(dork, convall=True)
        url += "num=100&hl=en&complete=0&safe=off&filter=0&btnG=Search"
        url += "&start=%d" % ((gpage-1) * 100)

        try:
            conn = self.opener.open(url)

            requestMsg = "HTTP request:\nGET %s" % url
            requestMsg += " %s" % httplib.HTTPConnection._http_vsn_str
            logger.log(8, requestMsg)

            page = conn.read()
            code = conn.code
            status = conn.msg
            responseHeaders = conn.info()
            page = decodePage(page, responseHeaders.get("Content-Encoding"), responseHeaders.get("Content-Type"))

            responseMsg = "HTTP response (%s - %d):\n" % (status, code)

            if conf.verbose <= 4:
                responseMsg += getUnicode(responseHeaders, UNICODE_ENCODING)
            elif conf.verbose > 4:
                responseMsg += "%s\n%s\n" % (responseHeaders, page)

            logger.log(7, responseMsg)
        except urllib2.HTTPError, e:
            try:
                page = e.read()
            except socket.timeout:
                warnMsg = "connection timed out while trying "
                warnMsg += "to get error page information (%d)" % e.code
                logger.critical(warnMsg)
                return None
        except (urllib2.URLError, socket.error, socket.timeout):
            errMsg = "unable to connect to Google"
            raise sqlmapConnectionException, errMsg

        retVal = [urllib.unquote(match.group(1)) for match in re.finditer(GOOGLE_REGEX, page, re.I | re.S)]

        if not retVal and "detected unusual traffic" in page:
            warnMsg = "Google has detected 'unusual' traffic from "
            warnMsg += "this computer disabling further searches"
            raise sqlmapGenericException, warnMsg

        return retVal
