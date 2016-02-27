# -*- coding: utf-8 -*-

from flask import Flask,render_template,jsonify
import datahelper
import json
from models import  *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gettree',methods=['GET','POST'])
def gettree():
    dbs = datahelper.getDBs()
    tree = list()

    for db in dbs:
        dic = dict()
        dic['name']=db.Name
        dic['id']=db.ID
        dic['icon']='/static/imgs/database.png'

        objects = datahelper.getDBObjects(db.Name)

        tables =   {'name':'表','icon':'/static/imgs/folder.png','children':[]}
        views = {'name':'视图','icon':'/static/imgs/folder.png','children':[]}
        funcs = {'name':'函数','icon':'/static/imgs/folder.png','children':[]}
        sps = {'name':'存储过程','icon':'/static/imgs/folder.png','children':[]}

        for t in objects['tables']:
                table = {'name':t.Name,'url':'/table/'+str(t.ID),'icon':'/static/imgs/table.png'}
                tables['children'].append(table)
        for v in objects['views']:
            view = {'name':v.Name,'url':'/view/'+str(v.ID),'icon':'/static/imgs/table.png'}
            views['children'].append(view)

        dic['children']=[tables,views,funcs,sps]
        tree.append(dic)
    strJson = json.dumps(tree)

    return strJson

@app.route('/dblist')
def getdbs():
    dbs = DataBase()
    dbs.Name = 'db1'
    return render_template('dblist.html',dbs)

@app.route('/table/<int:table_id>')
def getTableInfo(table_id):
    tableInfo = datahelper.getObjectInfo(table_id)
    tableInfo.Columns = datahelper.getObjectColumns(table_id)
    tableInfo.RowCount = datahelper.getRowCount(tableInfo.Name)
    tableInfo.Description = datahelper.getDescription(table_id,0)
    return render_template('table.html',tableInfo=tableInfo)

if __name__=='__main__':
    app.run(debug=True)