# -*- coding: utf-8 -*-
# @Time    : 2017/2/18 下午2:51
# @Author  : Yuhsuan
# @File    : test.py
# @Software: PyCharm Community Edition

import os
import netifaces as ni
from flask import Flask, request, redirect, url_for, send_file

import socket

from gevent import monkey
from gevent.pywsgi import WSGIServer
monkey.patch_all()

# UPLOAD_FOLDER = os.getcwd()+"/upload"
UPLOAD_FOLDER = os.path.split(os.path.realpath(__file__))[0]+"/upload"
print("You can find the uploaded files from the path: %s" % UPLOAD_FOLDER)

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route("/<file_name>", methods=['GET'])
def download(file_name):
    return send_file(app.config['UPLOAD_FOLDER']+'/'+file_name)

@app.route("/", methods=['POST'])
def index_post():
    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)
    return redirect(url_for('index'))

def port_checker(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('0.0.0.0', port))
    if result == 0:
        print("Port %s is open" % port)
        return False
    else:
        print("Port %s is not open" % port)
        return True


if __name__ == "__main__":
    port = [12345,8080,1234,4321,12345,54321]
    run_port = 0
    for i in range(len(port)):
        if port_checker(port[i]):
            run_port = port[i]
            break

    ip = ni.ifaddresses('en0')[2][0]['addr']
    print("Please open the url to upload file. http://%s:%s" % (ip,run_port))
    http_server = WSGIServer(('', run_port), app)
    http_server.serve_forever()