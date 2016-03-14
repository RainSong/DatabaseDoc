# -*- coding: utf-8 -*-

from flask import *
import datahelper
import json
from models import  *
import scripter
from pyodbc import Error
import os

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():

    server =  session['server'] if session.has_key('server') else None
    uname = session['uname'] if session.has_key('uname') else None
    upwd = session['upwd'] if session.has_key('upwd') else None
    # dbName = request.cookies.get('dbName')
    # if dbName is None or len(dbName):
    #     dbName = 'master'
    if server is None or uname is None or upwd is None or len(server) == 0 or len(uname) == 0 or len(upwd) == 0:
        return redirect('login')

    return render_template('index.html')

@app.route('/gettree',methods=['GET','POST'])
def gettree():

    server =  session['server'] if session.has_key('server') else None
    uname = session['uname'] if session.has_key('uname') else None
    upwd = session['upwd'] if session.has_key('upwd') else None
    # dbName = request.cookies.get('dbName')
    # if dbName is None or len(dbName):
    #     dbName = 'master'
    if server is None or uname is None or upwd is None or len(server) == 0 or len(uname) == 0 or len(upwd) == 0:
        return redirect('login')

    dbs = datahelper.getDBs(server,uname,upwd)
    tree = list()

    for db in dbs:
        dic = dict()
        dic['name']=db.Name
        dic['id']=db.ID
        dic['icon']='/static/imgs/database.png'
        dic['type']='db'

        objects = datahelper.getDBObjects(server,uname,upwd,db.Name)

        tables =   {'name':'表','type':'tables','icon':'/static/imgs/folder.png','children':[]}
        views = {'name':'视图','type':'views','icon':'/static/imgs/folder.png','children':[]}
        funcs = {'name':'函数','type':'ufs','icon':'/static/imgs/folder.png','children':[]}
        sps = {'name':'存储过程','type':'sps','icon':'/static/imgs/folder.png','children':[]}

        for t in objects['tables']:
            table = {'id':t.ID, 'name':'[{0}].[{1}]'.format(t.Schema,t.Name),'type':'table','icon':'/static/imgs/table.png'}
            tables['children'].append(table)
        for v in objects['views']:
            view = {'id':v.ID,'name':'[{0}].[{1}]'.format(v.Schema,v.Name),'type':'view','icon':'/static/imgs/table.png'}
            views['children'].append(view)

        dic['children']=[tables,views,funcs,sps]
        tree.append(dic)
    strJson = json.dumps(tree)

    return strJson

@app.route('/dblist')
def getdbs():

    server =  session['server'] if session.has_key('server') else None
    uname = session['uname'] if session.has_key('uname') else None
    upwd = session['upwd'] if session.has_key('upwd') else None
    # dbName = request.cookies.get('dbName')
    # if dbName is None or len(dbName):
    #     dbName = 'master'
    if server is None or uname is None or upwd is None or len(server) == 0 or len(uname) == 0 or len(upwd) == 0:
        return redirect('login')

    dbs = DataBase()
    dbs.Name = 'db1'
    return render_template('dblist.html',dbs)

@app.route('/table/<int:table_id>')
def getTableInfo(table_id):
    server =  session['server'] if session.has_key('server') else None
    uname = session['uname'] if session.has_key('uname') else None
    upwd = session['upwd'] if session.has_key('upwd') else None
    dbName = request.cookies.get('current_database_name')
    if dbName is None or len(dbName) == 0:
        dbName = 'master'
    if server is None or uname is None or upwd is None or len(server) == 0 or len(uname) == 0 or len(upwd) == 0:
        return redirect('login')
    tableInfo = Table()
    try:
        tableInfo = datahelper.getObjectInfo(table_id,server,uname,upwd,dbName)
        tableInfo.Columns = datahelper.getObjectColumns(table_id,server,uname,upwd,dbName)
        tableInfo.Indexes = datahelper.getIndexes(table_id,server,uname,upwd,dbName)
        tableInfo.RowCount = datahelper.getRowCount(tableInfo.Name,server,uname,upwd,dbName)
        tableInfo.Description = datahelper.getDescription(table_id,0,server,uname,upwd,dbName)
        tableInfo.DefaultConstraints = datahelper.getDefaultConstraints(table_id,server,uname,upwd,dbName)
        tableInfo.ForeignKeys = datahelper.getForeignKeys(table_id,server,uname,upwd,dbName)
        tableInfo.Script = scripter.genTableScript(tableInfo)
    except Error as e:
        app.logger.error('get tableinfo failed,table_id:{0}'.format(table_id),e)
    return render_template('table.html',tableInfo=tableInfo)

@app.route('/view/<int:view_id>')
def getViewInfo(view_id):
    server =  session['server'] if session.has_key('server') else None
    uname = session['uname'] if session.has_key('uname') else None
    upwd = session['upwd'] if session.has_key('upwd') else None
    dbName = request.cookies.get('current_database_name')
    if dbName is None or len(dbName) == 0:
        dbName = 'master'
    if server is None or uname is None or upwd is None or len(server) == 0 or len(uname) == 0 or len(upwd) == 0:
        #return '<script type="text/javascrpt">window.parent.location.href="/login";</script>';
        return render_template('jump.html',url='/login')

    viewInfo = datahelper.getObjectInfo(view_id,server,uname,upwd,dbName)
    viewInfo.Columns = datahelper.getObjectColumns(view_id,server,uname,upwd,dbName)
    viewInfo.Indexes = datahelper.getIndexes(view_id,server,uname,upwd,dbName)
    viewInfo.Description = datahelper.getDescription(view_id,0,server,uname,upwd,dbName)
    viewInfo.Script = datahelper.getDefinition(view_id,server,uname,upwd,dbName)
    return render_template('view.html',viewInfo=viewInfo)

@app.route('/login',methods=['POST',"GET"])
def login():

    result = dict()
    if request.method=='POST':
        server =  request.form['server']
        uname = request.form['uname']
        upwd = request.form['upwd']

        if server is None or len(server) == 0 :
            result['hasError'] = True
            result['errorMsg'] = "please input server."
            return render_template('login.html',result = result)
        elif uname is None or len(uname) == 0:
            result['hasError'] = True
            result['errorMsg'] = "please input user name."
            return render_template('login.html',result = result)
        elif upwd is None or len(upwd) == 0:
            result['hasError'] = True
            result['errorMsg'] = "please input password."
            return render_template('login.html',result = result)
        else:
            try:
                count = datahelper.testLogin(server,uname,upwd)
                session['server']= server
                session['uname'] = uname
                session['upwd'] = upwd
                return redirect(url_for('index'))
            except Error as e:
                app.logger.error(e)
                result['hasError'] = True
                result['errorMsg'] = "log in faild."
                return render_template('login.html',result = result)
    else:
        return render_template('login.html',result = result)

@app.route('/tree')
def tree():
    return render_template('tree.html')

if __name__=='__main__':
    app.secret_key = os.urandom(24)
    app.run(debug=True)