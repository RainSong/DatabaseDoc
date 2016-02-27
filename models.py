# -*- coding: utf-8 -*-

class DBObject:
    """数据库对象积累性"""
    CreateDate = None
    ModifyDate = None
    Name = ''
    ID = 0
    Description = ''
    Properties = None

class DataBase(DBObject):
    Tables = None
    Views = None
    Functions = None
    StoredProcedure = None


class Table(DBObject):
    Schema = ''
    Columns = None
    Script = ''
    RowCount = 0

class Function(DBObject):
    Parameters = None
    Script = ''

class StoredProcedure(DBObject):
    Parameters = None
    Script = ''

class View(DBObject):
    Columns = None
    Script = ''

class Column:
    ID = 0
    Name = ''
    DataType = ''
    AllowNull = True
    MaxLength = 0
    IdentityInfo = ''
    DefaultValue = ''
    Description = ''
    IsPrimary = False
    IsIndex = False

class Index:
    ID = 0,
    Name = ''
    IsPrimaryKey = ''
    IsUnique = ''
    ColumnNames = ''
    Description = ''





