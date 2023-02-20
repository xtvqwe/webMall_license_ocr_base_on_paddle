import flask
import license
import file_operation
import socket
import jinja2
import json
from gevent import pywsgi
import os
import subprocess


path=os.path.dirname(os.path.abspath(__file__))
path_load=jinja2.FileSystemLoader(path)

realIP=[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
port=8000

app=flask.Flask(__name__,static_folder=path+'/static')
app.config['UPLOAD_FOLDER']='tmp_license/'

def nocache(response):
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
app.after_request(nocache)

@app.route('/upload')
def upload_file():
    print(path)
    print(path_load)
    t=jinja2.Environment(loader=path_load).get_template('upload.html')
    return t.render().encode('utf-8')

@app.route('/uploader',methods=['GET','POST'])
def uploader():
    if flask.request.method=='POST':
        f=flask.request.files['file']
        #fpath=path+'/static/tmp_license/'+secure_filename(f.filename)
        fpath=path+'/static/tmp_license/'+f.filename
        f.save(fpath)
        #print(f.filename,fpath)
        file_operation.file_rename(fpath)
        return json.dumps({'status':'success'})

@app.route('/del_pic',methods=['GET'])
def del_pic():
    del_obj=flask.request.args.get('value')
    os.remove(path+'/static/tmp_license/'+del_obj)
    return json.dumps({'status':'success'})

@app.route('/del_all')
def del_all():
    with open(path+'/static/data.json','w') as w:
        json.dump({
            'mdata':[],
            'unmatched':[],
            'unrecognized':[]
        },w)
    files=os.listdir(path+'/static/tmp_license/')
    for f in files:
        os.remove(path+'/static/tmp_license/'+f)
    return json.dumps({'status':'success'})
    
@app.route('/ip')
def fetch_ip():
    ip=flask.request.remote_addr
    return ip

@app.route('/refresh')
def refresh():
    files=[x.split('/')[-1] for x in license.get_names()]
    return json.dumps(files)

@app.route('/refresh_data')
def refresh_data():
    with open(path+'/static/data.json','r') as r:
        data=json.load(r)
    return json.dumps(data)

@app.route('/raw_data')
def raw_data():
    with open(path+'/static/basic_data.json','r') as r:
        data=json.load(r)
    return json.dumps(data)

@app.route('/multi_produce')
def multi_produce():
    child = subprocess.Popen(["pgrep","-f",'license.py'],stdout=subprocess.PIPE,shell=False)
    response = child.communicate()[0]
    if not response:
        os.system('sh ./ocr_start.sh')
        return json.dumps({'status':'success'})
    else:
        return json.dumps({'status':'processing'})

@app.route('/process_status')
def get_status():
    child = subprocess.Popen(["pgrep","-f",'license.py'],stdout=subprocess.PIPE,shell=False)
    response = child.communicate()[0]
    if not response:
        return json.dumps({'status':'success'})
    else:
        return json.dumps({'status':'processing'})

@app.route('/data_update',methods=['POST'])
def data_update():
    if flask.request.method=='POST':
        datas=flask.request.json
        with open(path+'/static/data.json','w') as w:
            json.dump(datas,w)
    return json.dumps({'status':'success'})

if __name__ == '__main__':
    print('=============域名:'+realIP+'=============')
    server = pywsgi.WSGIServer(('0.0.0.0', port), app)
    server.serve_forever()