# -*- coding: utf-8 -*-
# Copyright 2010 British Broadcasting Corporation and Kamaelia Contributors(1)
#
# (1) Kamaelia Contributors are listed in the AUTHORS file and at
#     http://www.kamaelia.org/AUTHORS - please extend this file,
#     not this notice.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import socket
import pprint
import string
import sys
import os
import re
import cStringIO
from datetime import datetime
from wsgiref.validate import validator
import LogWritable
import urls
import Axon
from Axon.ThreadedComponent import threadedcomponent
#from Axon.Component import component
import Kamaelia.Util.Log as Log


from Kamaelia.Chassis.ConnectedServer import MoreComplexServer

from Kamaelia.Protocol.HTTP.HTTPServer import HTTPServer

Axon.Box.ShowAllTransits = False
# ----------------------------------------------------------------------------------------------------
#
# Simple WSGI Handler
#

def HTML_WRAP(app):
    """
    Wraps the Application object's results in HTML
    """
    def gen(environ, start_response):
        """The standard WSGI interface"""
        iterator = app(environ, start_response)
        first_yield = iterator.next()
        yield "<html>\n"
        yield "<body>\n"
        yield first_yield
        for i in iterator:
            yield i
        yield "</body>\n"
        yield "</html>\n"
    return gen

def getServerInfo(uri_server):
    split_server = uri_server.split(":")
    return (split_server[0], split_server[1])

def normalizeEnviron(environ):
    """
    Converts environ variables to strings for wsgi compliance and deletes extraneous
    fields.
    """
    header_list = []
    header_dict = environ['headers']

    for key in header_dict:
        line = "%s: %s\n" % (key, header_dict[key])
        header_list.append(line)

    environ['headers'] = ''.join(header_list)
    environ['peerport'] = str(environ['peerport'])
    environ['localport'] = str(environ['localport'])
    del environ['bad']


class _WsgiHandler(threadedcomponent):
    """Choosing to run the WSGI app in a thread rather than the same
       context, this means we don't have to worry what they get up
       to really"""
    Inboxes = {
        'inbox' : 'NOT USED',
        'control' : 'NOT USED',
    }
    Outboxes = {
        'outbox' : 'used to send page fragments',
        'signal' : 'send producerFinished messages',
        '_signal-lw' : 'shut down the log writable',
    }

    def __init__(self, app_name, app, request, log_writable, WsgiConfig):
        super(_WsgiHandler, self).__init__()
        self.app_name = app_name
        self.request = request
        self.environ = request
        self.app = app
        #self.log_writable = log_writable
        self.log_writable = LogWritable.GetLogWritable('wsgi.log', self, '_signal-lw')
        self.status = self.response_headers = False
        self.wsgi_config = WsgiConfig

    def main(self):
        self.log_writable.activate()

        self.headers = self.environ["headers"]
        self.server_name, self.server_port = getServerInfo(self.request["uri-server"])

        self.initRequiredVars(self.wsgi_config)
        self.initOptVars(self.wsgi_config)

        self.munge_headers()

        #stringify all variables for wsgi compliance
        normalizeEnviron(self.environ)

        #PEP 333 specifies that we're not supposed to buffer output here,
        #so pulling the iterator out of the app object
        app_iter = self.app(self.environ, self.start_response)

        first_response = app_iter.next()
        if self.response_headers:
            self.write(first_response)
        else:
            raise WsgiError()

        for fragment in app_iter:
            page = {
                'data' : fragment,
            }
            self.send(page, 'outbox')

        app_iter.close()

        self.send(Axon.Ipc.producerFinished(self), "signal")
        self.send(Axon.Ipc.shutdownMicroprocess(self), '_signal-lw')

    def start_response(self, status, response_headers, exc_info=None):
        """
        Method to be passed to WSGI application object
        """
        #TODO:  Add more exc_info support
        if exc_info:
            raise exc_info[0], exc_info[1], exc_info[2]

        self.status = status
        self.response_headers = response_headers

        return self.write

    def write(self, body_data):
        page = {
            'data' : body_data,
        }
        self.send(page, 'outbox')

    def munge_headers(self):
        for header in self.environ["headers"]:
            cgi_varname = "HTTP_"+header.replace("-","_").upper()
            self.environ[cgi_varname] = self.environ["headers"][header]

        pprint.pprint(self.environ)
        pprint.pprint(self.environ["headers"])

    def generateRequestMemFile(self):
        """
        Creates a memfile to be stored in wsgi.input
        """
        CRLF = '\r\n'

        full_request = "%s %s %s/%s%s" % \
            (self.environ['method'], self.environ['raw-uri'], self.environ['protocol'], self.environ['version'], CRLF)

        header_list = []
        for key in self.environ['headers']:
            header_list.append("%s: %s%s" % (key, self.environ['headers'][key], CRLF))

        full_request = full_request + string.join(header_list) + '\n' + self.environ['body']
        print "full_request: \n" + full_request

        return cStringIO.StringIO(full_request)

    def initRequiredVars(self, wsgi_config):
        """
        This method initializes all variables that are required to be present
        (including ones that could possibly be empty.
        """
        self.environ["REQUEST_METHOD"] = self.request["method"]

        # Portion of URL that relates to the application object.
        self.environ["SCRIPT_NAME"] = self.app_name

        # Remainder of request path after "SCRIPT_NAME"
        self.environ["PATH_INFO"] = self.environ["uri-suffix"]

        # Server name published to the outside world
        self.environ["SERVER_NAME"] = self.server_name

        # Server port published to the outside world
        self.environ["SERVER_PORT"] =  self.server_port

        #Protocol to respond to
        self.environ["SERVER_PROTOCOL"] = self.request["protocol"]

        #==================================
        #WSGI variables
        #==================================
        self.environ["wsgi.version"] = wsgi_config['WSGI_VER']
        self.environ["wsgi.url_scheme"] = self.request["protocol"].lower()
        self.environ["wsgi.errors"] = self.log_writable

        self.environ["wsgi.multithread"] = False
        self.environ["wsgi.multiprocess"] = False
        self.environ["wsgi.run_once"] = True
        self.environ["wsgi.input"] = self.generateRequestMemFile()

    def initOptVars(self, wsgi_config):
        """This method initializes all variables that are optional"""
        # Portion of request URL that follows the ? - may be empty or absent
        if self.environ["uri-suffix"].find("?") != -1:
            self.environ["QUERY_STRING"] = \
                self.environ["uri-suffix"][self.environ["uri-suffix"].find("?")+1:]
        else:
            self.environ["QUERY_STRING"] = ""

        # Contents of an HTTP_CONTENT_TYPE field
        self.environ["CONTENT_TYPE"] = self.headers.get("content-type","")

        # Contents of an HTTP_CONTENT_LENGTH field
        self.environ["CONTENT_LENGTH"] = self.headers.get("content-length","")
        #self.environ["DOCUMENT_ROOT"] = self.homedirectory
        self.environ["PATH"] = os.environ['PATH']
        self.environ["DATE"] = datetime.now().isoformat()
        self.environ["SERVER_ADMIN"] = wsgi_config['SERVER_ADMIN']
        self.environ["SERVER_SOFTWARE"] = wsgi_config['SERVER_SOFTWARE']
        self.environ["SERVER_SIGNATURE"] = "%s Server at %s port %s" % \
                    (wsgi_config['SERVER_SOFTWARE'], self.server_name, self.server_port)

    def unsupportedVars(self):
        """
        Probably won't be used.  This is just a list of environment variables that
        aren't implemented as of yet.
        """
        consider = " **CONSIDER ADDING THIS -- eg: "
        self.environ["HTTP_REFERER"] = consider + "-"
        self.environ["SERVER_SIGNATURE"] = consider + "...."
        self.environ["SCRIPT_FILENAME"] = consider + \
            "/usr/local/httpd/sites/com.thwackety/cgi/test.pl"
        self.environ["REQUEST_URI"] = consider + "/cgi-bin/test.pl"
        self.environ["SCRIPT_URL"] = consider + "/cgi-bin/test.pl"
        self.environ["SCRIPT_URI"] = consider + "http://thwackety.com/cgi-bin/test.pl"
        self.environ["REMOTE_ADDR"] = consider + "192.168.2.5"
        self.environ["REMOTE_PORT"] = consider + "56669"
        self.environ["GATEWAY_INTERFACE"] = consider + "CGI/1.1"

def Handler(log_writable, WsgiConfig, substituted_path):
    def _getWsgiHandler(request):
        requested_uri = sanitizePath(request['raw-uri'], substituted_path)
        print requested_uri
        for url_item in urls.UrlList:
            print 'trying ' + url_item[0]
            if re.search(url_item[0], requested_uri):
                print url_item[0] + 'succesful!'
                u, mod, app_attr, app_name = url_item
                break
        module = _importWsgiModule(mod)
        app = getattr(module, app_attr)
        return _WsgiHandler(app_name, app, request, log_writable, WsgiConfig)
    return _getWsgiHandler

def HTTPProtocol():
    def foo(self,**argd):
        print self.routing
        return HTTPServer(requestHandlers(self.routing),**argd)
    return foo

class WsgiError(Exception):
    def __init__(self):
        super(WsgiError, self).__init__()

def _importWsgiModule(name):
    """
    Just a copy/paste of the example my_import function from here:
    http://docs.python.org/lib/built-in-funcs.html
    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def sanitizePath(uri, substituted_path):
    uri = uri.replace(substituted_path, '', 1)
    uri = uri.strip('/')

    outputpath = []
    splitpath = string.split(uri, "/")
    for directory in splitpath:
        if directory == ".":
            pass
        elif directory == "..":
            if len(outputpath) > 0: outputpath.pop()
        else:
            outputpath.append(directory)
    outputpath = '/'.join(outputpath)
    return outputpath
