#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_url_parse(self, url):
        return urlparse(url)

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        request_lines = []
        for line in data.splitlines():
            request_lines.append(line)
        code = request_lines[0].split()[1]    
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        body_start = data.index("\r\n\r\n")
        body = data[body_start:]

        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        # buffer = sock.recv(1024)
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        parsed_url = self.get_url_parse(url)
        port = parsed_url.port
        if port == None:
            port = 80

        self.connect(parsed_url.hostname, port)

        path = parsed_url.path if parsed_url.path != "" else "/"
        # build and send request
        first_line = "GET %s HTTP/1.1" % (path)
        host_header = "Host: %s" % (parsed_url.hostname + ":" + str(port))
        connection_header = "Connection: close"
        request = "\r\n".join([first_line, host_header, connection_header])
        request += "\r\n\r\n"
        self.sendall(request)

        # wait for response
        response = self.recvall(self.socket)
        print(response)

        # get code
        code = int(self.get_code(response))
        body = self.get_body(response)

        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        parsed_url = self.get_url_parse(url)
        port = parsed_url.port
        if port == None:
            port = 80

        self.connect(parsed_url.hostname, port)

        # build body
        args_list = []
        if args != None:
            for key in args:
                key_value_pair = "%s=%s" % (key, args[key])
                args_list.append(key_value_pair)
        body = "&".join(args_list)


        # build and send request
        path = parsed_url.path if parsed_url.path != "" else "/"
        first_line = "POST %s HTTP/1.1" % (path)
        host_header = "Host: %s" % (parsed_url.hostname + ":" + str(port))
        content_length_header = "Content-Length: %i" % (len(body))
        request = "\r\n".join([first_line, host_header, content_length_header])
        request += "\r\n\r\n"
        request += body
        self.sendall(request)

        # wait for response
        response = self.recvall(self.socket)
        print(response)

        # get code
        code = int(self.get_code(response))
        body = self.get_body(response)
        
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
