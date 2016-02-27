# -*- coding: utf-8 -*-

from models import *
import pyodbc
import datetime

defaultDbName = 'AdventureWorks'
connectionString = 'DRIVER={SQL Server};SERVER=localhost;UID=sa;PWD=ygj000;DATABASE='

def getDBObjects(dbName='master'):
    """  获取数据库空的对象信息
    :parameter
    :return:
    """
    conn = pyodbc.connect(connectionString+dbName)
    curx = conn.cursor()
    curx.execute("""select type
                       ,name
                       ,object_id
                       ,create_date
                       ,modify_date
                 from sys.objects
                 where type in ('U','V')""")

    tables = []
    views = []
    for row in curx:
        type = row[0].strip(' ')
        if  type == 'U':
            table = Table()
            table.ModifyDate = row[4]
            table.CreateDate = row[3]
            table.Name = row[1]
            table.ID = row[2]
            tables.append(table)
        elif type == 'V':
            view = View()
            view.ModifyDate = row[4]
            view.CreateDate = row[3]
            view.Name = row[1]
            view.ID = row[2]
            views.append(view)
    result = dict()

    curx.close()
    conn.close()

    if len(tables)>0:
        result['tables']=tables
    if len(views)>0:
        result['views']=views
    return result

def getDBs():
    """ 获取数据库信息
    :return:
    """
    conn = pyodbc.connect(connectionString+'master')
    curx = conn.cursor()
    curx.execute("""select database_id
                        ,name
                        ,create_date
                from sys.databases
                where database_id > 6""")
    dbs = list()
    for row in curx:
        db = DataBase()
        db.ID = row[0]
        db.Name = row[1]
        db.CreateDate = row[2]
        dbs.append(db)

    curx.close()
    conn.close()

    return dbs

def getObjectInfo(objId):
    """
    获取数据库对象的基本信息
    :param objId:
    :return:
    """
    sql = """select object_id,
                   sys.objects.name,
                   CONVERT(varchar(20),create_date,120) as create_date,
                   CONVERT(varchar(20),modify_date,120) as modify_date,
                   sys.schemas.name as [schema]
            from sys.objects
            left join sys.schemas on sys.objects.schema_id = sys.schemas.schema_id
            where object_id = {0}""".format(objId)
    conn = pyodbc.connect(connectionString+defaultDbName)
    curx = conn.cursor()
    curx.execute(sql)
    row = curx.fetchone()
    table = Table()
    if row:
        table.ID = row[0]
        table.Name = row[1]
        table.CreateDate = row[2]
        table.ModifyDate = row[3]
        table.Schema = row[4]

    curx.close()
    conn.close()

    return table

def getObjectColumns(objectId):
    """
    获取数据库对象的列信息
    :param objectId:
    :return:
    """
    sql = """select sys.columns.column_id,
                   sys.columns.name,
                   sys.types.name as datatype,
                   sys.columns.is_nullable,
                   sys.columns.max_length,
            ISNULL(CONVERT(varchar(10),sys.identity_columns.seed_value) +
                  '-' + CONVERT(varchar(10),sys.identity_columns.seed_value),'') as identity_info,
            ISNULL(sys.default_constraints.definition,'') as default_value,
            CONVERT(varchar(max),sys.extended_properties.value) as [Description],
            case when isnull(sys.indexes.index_id,0)>0 and ISNULL(sys.indexes.is_primary_key,0)=1 then 1
                else 0 end as is_primary_key,
            case when isnull(sys.indexes.index_id,0)>0 and ISNULL(sys.indexes.is_primary_key,0)=0 then 1
                else 0 end as is_index
            from sys.columns
            left join sys.types on sys.columns.user_type_id = sys.types.user_type_id
            left join sys.index_columns on sys.columns.object_id = sys.index_columns.object_id
                and sys.columns.column_id = sys.index_columns.column_id
            left join sys.indexes on sys.index_columns.index_id = sys.indexes.index_id
                and sys.index_columns.object_id = sys.indexes.object_id
            left join sys.identity_columns
                on sys.columns.object_id = sys.identity_columns.object_id
                and sys.columns.column_id = sys.identity_columns.column_id
            left join sys.default_constraints
                on sys.columns.object_id = sys.default_constraints.parent_object_id
                and sys.columns.column_id = sys.default_constraints.parent_column_id
            left join sys.extended_properties
                on sys.columns.object_id = sys.extended_properties.major_id
                and sys.columns.column_id = sys.extended_properties.minor_id
                and sys.extended_properties.name = 'MS_Description'
                and sys.extended_properties.class = 1
            where sys.columns.object_id = {0}""".format(objectId)

    conn = pyodbc.connect(connectionString+defaultDbName)
    curx = conn.cursor()
    curx.execute(sql)
    columns = list()
    for row in curx:
        column = Column()
        column.ID = row[0]
        column.Name = row[1]
        column.DataType = row[2]
        column.AllowNull = row[3]
        column.MaxLength = row[4]
        column.IdentityInfo = row[5]
        column.DefaultValue = row[6]
        column.Description = row[7]
        column.IsPrimary = row[8]
        column.IsIndex = row[9]
        columns.append(column)
    curx.close()
    conn.close()

    return columns

def getRowCount(tableName):
    """
    获取表或者视图的总行数
    :param tableName:
    :return:
    """

    conn = pyodbc.connect(connectionString+defaultDbName)
    curx = conn.cursor()
    sql = """select count(1) from {0}""".format(tableName)
    count = 0
    try :
        curx.execute(sql)
        row = curx.fetchone()
        if row:
            count = row[0]
    except pyodbc.DatabaseError as e:
        print e

    curx.close()
    conn.close()
    return  count

def getDescription(majorId,minorId):
    """
    获取对象的备注和描述
    :param majorId:
    :param minorId:
    :return:
    """
    sql = """select CONVERT(varchar(max), value ) as [desc]
            from sys.extended_properties
            where name = 'MS_Description'
            and major_id = {0}
            and minor_id = {1}""".format(majorId,minorId)

    conn = pyodbc.connect(connectionString+defaultDbName)
    curx = conn.cursor()
    curx.execute(sql)

    row = curx.fetchone()
    desc = ''
    if row:
        desc = row[0]
    return desc

def getIndexes(objectId):
    """

    :param objectId:
    :return:
    """

    sql = """select sys.indexes.index_id,
                   sys.indexes.name,
                   sys.indexes.is_primary_key,
                   sys.indexes.is_unique,
                   CONVERT(varchar(max),sys.extended_properties.value) as [desc]
            from sys.indexes
            left join sys.extended_properties
                on sys.indexes.object_id = sys.extended_properties.major_id
                    and sys.indexes.index_id = sys.extended_properties.minor_id
                    and sys.extended_properties.name = 'MS_Description'
                    and sys.extended_properties.class = 7
            where sys.indexes.object_id = {0}""".format(objectId)

    conn = pyodbc.connect(connectionString+defaultDbName)
    curx = conn.cursor()
    curx.execute(sql)
    indexes = list()
    for row in curx:
        index = Index()
        index.ID = row[0]
        index.Name = row[1]
        index.IsPrimaryKey = row[2]
        index.IsUnique = row[3]
        index.Description = row[4]
        indexes.append(index)

    sql = """select sys.index_columns.index_id,
               sys.columns.name
        from sys.index_columns
        left join sys.columns
        on sys.index_columns.object_id = sys.columns.object_id
            and sys.index_columns.column_id = sys.columns.column_id
        where sys.index_columns.object_id = {0}""".format(objectId)

    curx.execute(sql)

    for row in curx:
        tempIndexes = [index for index in indexes if index.ID == row[0]]
        if len(index) > 0:
            if len(tempIndexes[0].ColumnNames)>0:
                tempIndexes[0].ColumnNames += ','

    return indexes