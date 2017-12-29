# -*- coding: utf-8 -*-
# @Time    : 2017/2/18 下午2:51
# @Author  : moveurbody
# @File    : mini_server.py
# @Software: PyCharm Community Edition

import os
import sys
import time
import subprocess

import socket
import requests
import netifaces as ni
from flask import Flask, request, redirect, url_for, send_file

# async
from gevent import monkey
from gevent.pywsgi import WSGIServer

monkey.patch_all()

UPLOAD_FOLDER = os.path.split(os.path.realpath(__file__))[0]+"/upload"
WORKING_FOLDR = os.path.split(os.path.realpath(__file__))[0]
print("You can find the uploaded files from the path: %s" % UPLOAD_FOLDER)

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# index
@app.route("/", methods=['GET'])
def index():
    file_list = []
    for i in os.listdir(app.config['UPLOAD_FOLDER'],):
        link = "<a href = '/" + i + "'>"+i+"</a><br>"
        file_list.append(link)

    return """
    <!doctype html>
    <title>Mini Server</title>
    <h1>Please select the file you want to be uploaded!</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file multiple>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "".join(file_list)

# prevent the server can't get favicon.ico and show error in the console
@app.route("/favicon.ico",methods=['GET'])
def favicon():
    return ''

# let user to get the file
@app.route("/<file_name>", methods=['GET'])
def download(file_name):
    return send_file(app.config['UPLOAD_FOLDER']+'/'+file_name)

# let user upload file
@app.route("/", methods=['POST'])
def index_post():
    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)
    return redirect(url_for('index'))

# check which port can be used
def port_checker(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('0.0.0.0', port))
    if result == 0:
        # print("Port %s is open" % port)
        return False
    else:
        # print("Port %s is not open" % port)
        return True

# check the default ports
def get_port():
    port = [8080, 1234, 12345, 4321, 54321]
    run_port = 0
    for i in range(len(port)):
        if port_checker(port[i]):
            run_port = port[i]
            break
    return run_port

def download_ngrolk():
    # if there is no ngrok, download the file
    if not os.path.exists(os.path.join(WORKING_FOLDR,'ngrok')):
        print('ngrok is downloading...')
        import re
        import time
        from io import BytesIO
        from urllib.request import urlopen
        from urllib.parse import urlparse
        from zipfile import ZipFile
        from bs4 import BeautifulSoup as bs

        # check the zip file path from ngrok
        url = 'https://ngrok.com/download'
        html = requests.get(url=url)
        soup = bs(html.text, "html.parser")
        os_name = sys.platform
        os_bit = 'amd64' if sys.maxsize == (2 ** 63 - 1) else '386'
        download_url = soup.find('a', href=re.compile(os_name + '.*' + os_bit))['href']

        # unzip without download
        print('unzip file path: %s' % WORKING_FOLDR)
        with urlopen(download_url) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as zfile:
                zfile.extractall(WORKING_FOLDR)

        time.sleep(20)
        while(not os.path.exists(os.path.join(WORKING_FOLDR,'ngrok'))):
            print('sleep')
            time.sleep(10)

        # to add permission for ngrok
        process = subprocess.Popen('chmod 0777 %s' % os.path.join(WORKING_FOLDR,'ngrok'),shell=True)
        process.wait()
    else:
        print('pass')
        pass

# check ngork and run
def enable_ngork(port):
    config_path = os.path.join(WORKING_FOLDR,'ngrok')
    print(config_path)
    if os.path.isfile(config_path):
        cmd = '%s http %s' % (config_path,port)
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

        time.sleep(3)

        url = 'http://127.0.0.1:4040/api/tunnels'
        res = requests.get(url=url)
        link = res.json()['tunnels'][0]['public_url']
        return link
    else:
        print("Can't find ngork service, you can access the file by intranet only.")
        return False

if __name__ == "__main__":
    run_port = get_port()
    download_ngrolk()
    ngork_status = enable_ngork(run_port)
    if ngork_status!=False:
        print('Please open the url to upload file from %s' % ngork_status)
    try:
        if sys.platform =='linux':
            ip = ni.ifaddresses('eth0')[2][0]['addr']
        elif sys.platform == 'darwin':
            ip = ni.ifaddresses('en0')[2][0]['addr']
    except Exception as e:
        print(e)
    # if ngork_status == False:
    print("Please open the url to upload file. http://%s:%s" % (ip,run_port))
    http_server = WSGIServer(('', run_port), app)
    http_server.serve_forever()
