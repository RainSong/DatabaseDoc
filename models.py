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
    Indexes = None
    ForeignKeys = None
    DefaultConstraints = None
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
    IsIdentity = False
    IdentitySeed = 0
    IdentityIncrement = 0
    Description = ''
    IsPrimary = False
    IsIndex = False
    Collation = ''

class Index:
    ID = 0,
    Name = ''
    IsPrimaryKey = ''
    IsUnique = ''
    IsPadded = False
    IgnoreDupKey = False
    AllowRowLocks = True
    AllowPageLocks = True
    Description = ''
    IndexColumns = None
    IndexColumnNames = ''
class IndexColumn:
    ID = 0
    IndexID = 0
    IsDescendingKey = False
    ColumnName = ''

class ForeignKey:
    ID = 0
    Name = ''
    ColumnName = ''
    RefrencedObjectID = 0
    RefrencedObjectSchema = ''
    ReferenceObjectName = ''
    RefrencedColumn = ''
    Description = ''

class DefaultConstraint:
    ID = 0
    Name = ''
    Definition = ''
    ColumnID = 0
    ColumnName = ''
    Description = ''






