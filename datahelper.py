# -*- coding: utf-8 -*-

from models import *
import pyodbc

def getConnString(server,uname,upwd,dbName):
    """

    :param server:
    :param uname:
    :param upwd:
    :param dbName:
    :return:
    """
    return 'DRIVER={SQL Server};SERVER=%s;UID=%s;PWD=%s;DATABASE=%s' % (server,uname,upwd,dbName)

def getDBObjects(server,uname,upwd, dbName='master'):
    """  获取数据库空的对象信息
    :param server:
    :param uname:
    :param upwd:
    :param dbName：
    :return:
    """
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
    curx = conn.cursor()
    curx.execute("""select type
                       ,sys.objects.name as name
                       ,object_id
                       ,create_date
                       ,modify_date
                       ,sys.schemas.name as [schema]
                 from sys.objects
                 left join sys.schemas
                    on sys.objects.schema_id = sys.schemas.schema_id
                 where type in ('U','V')
                 order by sys.schemas.name""")

    tables = []
    views = []
    for row in curx:
        type = row[0].strip(' ')
        if  type == 'U':
            table = Table()
            table.ModifyDate = row.modify_date
            table.CreateDate = row.create_date
            table.Name = row.name
            table.ID = row.object_id
            table.Schema = row.schema
            tables.append(table)
        elif type == 'V':
            view = View()
            view.ModifyDate = row.modify_date
            view.CreateDate = row.create_date
            view.Name = row.name
            view.ID = row.object_id
            view.Schema = row.schema
            views.append(view)
    result = dict()

    curx.close()
    conn.close()

    if len(tables)>0:
        result['tables']=tables
    if len(views)>0:
        result['views']=views
    return result

def getDBs(server,uname,upwd,dbName='master'):
    """ 获取数据库信息
    :return:
    """
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
    curx = conn.cursor()
    curx.execute("""select database_id
                        ,name
                        ,create_date
                from sys.databases
                where database_id > 6""")
    dbs = list()
    for row in curx:
        db = DataBase()
        db.ID = row.database_id
        db.Name = row.name
        db.CreateDate = row.create_date
        dbs.append(db)

    curx.close()
    conn.close()

    return dbs

def getObjectInfo(objId,server,uname,upwd,dbName):
    """
    获取数据库对象的基本信息
    :param objId:
    :return:
    """
    sql = """select object_id,
                   sys.objects.name,
                   CONVERT(varchar(20),create_date,120) as create_date,
                   CONVERT(varchar(20),modify_date,120) as modify_date,
                   sys.schemas.name as [schema],
                   sys.objects.type
            from sys.objects
            left join sys.schemas on sys.objects.schema_id = sys.schemas.schema_id
            where object_id = {0}""".format(objId)
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
    curx = conn.cursor()
    curx.execute(sql)
    row = curx.fetchone()
    obj = None
    objType = str.strip(str.lower(row.type))
    if row:
        if objType == 'u':
            obj = Table()
            obj.ID = row.object_id
            obj.Name = row.name
            obj.CreateDate = row.create_date
            obj.ModifyDate = row.modify_date
            obj.Schema = row.schema
        elif objType == 'v':
            obj = View()
            obj.ID = row.object_id
            obj.Name = row.name
            obj.CreateDate = row.create_date
            obj.ModifyDate = row.modify_date
            obj.Schema = row.schema
    curx.close()
    conn.close()

    return obj

def getObjectColumns(objectId,server,uname,upwd,dbName):
    """
    获取数据库对象的列信息
    :param objectId:
    :return:
    """
    sql = """select sys.columns.column_id,
                   sys.columns.name as column_name,
                   sys.types.name as datatype,
                   sys.columns.is_nullable,
                   sys.columns.max_length,
                   sys.columns.collation_name,
                   case when ISNULL(sys.identity_columns.column_id,0) > 0 then 1 else 0 end as is_identity,
                   convert(int,sys.identity_columns.seed_value) as inentity_seed,
                   convert(int,sys.identity_columns.increment_value) as identity_nncrement,
                   CONVERT(varchar(max),sys.extended_properties.value) as [description],
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
            left join sys.extended_properties
                on sys.columns.object_id = sys.extended_properties.major_id
                and sys.columns.column_id = sys.extended_properties.minor_id
                and sys.extended_properties.name = 'MS_Description'
                and sys.extended_properties.class = 1
            where sys.columns.object_id = {0}""".format(objectId)
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
    curx = conn.cursor()
    curx.execute(sql)
    columns = list()
    for row in curx:
        column = Column()
        column.ID = row.column_id
        column.Name = row.column_name
        column.DataType = row.datatype
        column.AllowNull = row.is_nullable
        column.MaxLength = row.max_length
        column.IsIdentity = row.is_identity
        column.IdentitySeed = row.inentity_seed
        column.IdentityIncrement = row.identity_nncrement
        column.Description = row.description
        column.IsPrimary = row.is_primary_key
        column.IsIndex = row.is_index
        column.Collation = row.collation_name
        columns.append(column)
    curx.close()
    conn.close()

    return columns

def getRowCount(tableName,server,uname,upwd,dbName):
    """
    获取表或者视图的总行数
    :param tableName:
    :return:
    """
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
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

def getDescription(majorId,minorId,server,uname,upwd,dbName):
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
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
    curx = conn.cursor()
    curx.execute(sql)

    row = curx.fetchone()
    desc = ''
    if row:
        desc = row[0]
    return desc

def getIndexes(objectId,server,uname,upwd,dbName):
    """
    获取索引信息
    :param objectId:
    :return:
    """
    print 'get indexes'
    indexColumns = getIndexColumns(objectId,server,uname,upwd,dbName)
    sql = """select index_id,
                   sys.indexes.name as index_name,
                   is_primary_key,
                   is_unique,
                   is_padded,
                   ignore_dup_key,
                   allow_row_locks,
                   allow_page_locks,
                   CONVERT(varchar(max),sys.extended_properties.value) as [desc]
            from sys.indexes
            left join sys.extended_properties
                on sys.indexes.object_id = sys.extended_properties.major_id
                    and sys.indexes.index_id = sys.extended_properties.minor_id
                    and sys.extended_properties.name = 'MS_Description'
                    and sys.extended_properties.class = 7
            where sys.indexes.object_id = {0}""".format(objectId)
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
    curx = conn.cursor()
    curx.execute(sql)
    indexes = list()
    for row in curx:
        index = Index()
        index.ID = row.index_id
        index.Name = row.index_name
        index.IsPrimaryKey = row.is_primary_key
        index.IsUnique = row.is_unique
        index.IsPadded = row.is_padded
        index.IgnoreDupKey = row.ignore_dup_key
        index.AllowPageLocks = row.allow_row_locks
        index.allow_page_locks = row.allow_page_locks
        index.Description = row.desc

        index.IndexColumns = [ic for ic in indexColumns if ic.IndexID == index.ID]

        if index.IndexColumns!=None and len(index.IndexColumns)>0:
            for ic in index.IndexColumns:
                if len(index.IndexColumnNames) > 0:
                    index.IndexColumnNames += ', '
                index.IndexColumnNames += ic.ColumnName

        indexes.append(index)

    curx.close()
    conn.close()

    return indexes

def getForeignKeys(objId,server,uname,upwd,dbName):
    """

    :param objId:
    :return:
    """

    sql = """select sys.foreign_keys.object_id,
               sys.foreign_keys.name,
               constraint_columns.name as constraint_column_name,
               sys.objects.object_id as referenced_table_id,
               sys.schemas.name as [referenced_schema_name],
               sys.objects.name as referenced_table_name,
               referenced_columns.name referenced_column_name,
               CONVERT(varchar(max), sys.extended_properties.value) as Description
        from sys.foreign_keys
        left join sys.extended_properties
            on sys.foreign_keys.object_id = sys.extended_properties.major_id
            and sys.extended_properties.minor_id = 0
            and sys.extended_properties.name = 'MS_Description'
        left join sys.foreign_key_columns
            on sys.foreign_keys.parent_object_id = sys.foreign_key_columns.parent_object_id
            and sys.foreign_keys.object_id = sys.foreign_key_columns.constraint_object_id
        left join sys.columns as constraint_columns
            on sys.foreign_key_columns.parent_object_id = constraint_columns.object_id
            and sys.foreign_key_columns.referenced_column_id = constraint_columns.column_id
        left join sys.objects
            on sys.foreign_key_columns.referenced_object_id = sys.objects.object_id
        left join sys.schemas on sys.objects.schema_id = sys.schemas.schema_id
        left join sys.columns as referenced_columns
            on sys.objects.object_id = referenced_columns.object_id
            and sys.foreign_key_columns.referenced_column_id = referenced_columns.column_id
        where sys.foreign_keys.parent_object_id = {0}""".format(objId)
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
    curx = conn.cursor()
    curx.execute(sql)

    foreignKeys = list()
    for row in curx:
        foreignKey = ForeignKey()
        foreignKey.ID = row.object_id
        foreignKey.Name = row.name
        foreignKey.ColumnName = row.constraint_column_name
        foreignKey.RefrencedObjectID = row.referenced_table_id
        foreignKey.RefrencedObjectSchema = row.referenced_schema_name
        foreignKey.RefrencedObjectName = row.referenced_table_name
        foreignKey.RefrencedColumn = row.referenced_column_name
        foreignKey.Description = row.Description

        foreignKeys.append(foreignKey)

    curx.close()
    conn.close()
    return foreignKeys

def getIndexColumns(objeId,server,uname,upwd,dbName):
    """

    :param objeId:
    :return:
    """
    sql = """select index_column_id,
                   index_id,
                   is_descending_key,
                   sys.columns.column_id,
                   sys.columns.name as column_name
            from sys.index_columns
            left join sys.columns
                on sys.index_columns.object_id = sys.columns.object_id
                and sys.index_columns.column_id = sys.columns.column_id
            where sys.index_columns.object_id = {0}""".format(objeId)
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
    curx = conn.cursor()
    curx.execute(sql)

    indexColumns = list()
    for row in curx:
        indexColumn = IndexColumn()
        indexColumn.ID = row.index_column_id
        indexColumn.IndexID = row.index_id
        indexColumn.IsDescendingKey = row.is_descending_key
        indexColumn.ColumnName = row.column_name
        indexColumns.append(indexColumn)

    curx.close()
    conn.close()

    return indexColumns

def getDefaultConstraints(objId,server,uname,upwd,dbName):
    """

    :param objId:
    :return:
    """
    sql = """select sys.default_constraints.object_id,
                   sys.default_constraints.name,
                   sys.default_constraints.definition,
                   sys.columns.column_id,
                   sys.columns.name as column_name,
                  CONVERT(varchar(max), sys.extended_properties.value) as [desc]
            from sys.default_constraints
            left join sys.extended_properties
                on sys.default_constraints.object_id = sys.extended_properties.major_id
                and sys.extended_properties.minor_id = 0
            left join sys.columns
                on sys.default_constraints.parent_object_id = sys.columns.object_id
                and sys.default_constraints.parent_column_id = sys.columns.column_id
            where parent_object_id = {0}""".format(objId)
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
    curx = conn.cursor()
    curx.execute(sql)

    constraints = list()
    for row in curx:
        constraint = DefaultConstraint()
        constraint.ID = row.object_id
        constraint.Name = row.name
        constraint.Definition = row.definition
        constraint.ColumnID = row.column_id
        constraint.ColumnName = row.column_name
        constraint.Description = row.desc

        constraints.append(constraint)

    curx.close()
    conn.close()

    return constraints

def testLogin(server,uname,upwd):
    connString = getConnString(server,uname,upwd,'master')
    conn = pyodbc.connect(connString)
    curx = conn.cursor()

    sql = 'select COUNT(1) from sys.databases'
    curx.execute(sql)
    row = curx.fetchone()
    count = 0
    if row:
        count = row[0]
    return count

def getDefinition(objId,server,uname,upwd,dbName):
    """

    :param objId:
    :param server:
    :param uname:
    :param upwd:
    :param dbName:
    :return:
    """
    sql = "select [definition] from sys.sql_modules where object_id = {0}".format(objId)
    connString = getConnString(server,uname,upwd,dbName)
    conn = pyodbc.connect(connString)
    curx = conn.cursor()
    curx.execute(sql)
    row = curx.fetchone()
    sql = ""
    if row:
        sql = row.definition

    curx.close()
    conn.close()

    return sql
