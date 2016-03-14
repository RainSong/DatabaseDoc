# -*- coding: utf-8 -*-

needShowMaxLenghtDataTypes = ['CHAR','NCHAR','VARCHAR','NVARCHAR','TEXT']

def genTableScript(tableInfo):
    """

    :param tableInfo:
    :return:
    """
    primaryKeys = [index for index in tableInfo.Indexes if index.IsPrimaryKey]
    script = 'CREATE TABLE [{0}].[{1}]' .format(tableInfo.Schema,tableInfo.Name)
    script+='\r('
    script += genTableColumnScript(tableInfo,primaryKeys)
    script += genTablePrimaryKeyScript(tableInfo,primaryKeys)
    script+='\r)'
    if len(primaryKeys) > 0:
        script += 'ON [PRIMARY]\rGO\r'
    script += getTablePrimaryKeyDescriptScript(tableInfo,primaryKeys)
    script += genTableColumnDescriptScript(tableInfo)
    script += genTabelForeignKeyScript(tableInfo)
    script += genTableDefintionScript(tableInfo)
    script += genTabelForeignKeyScript(tableInfo)

    return script

def genTablePrimaryKeyScript(tableInfo,primaryKeys):
    """

    :param tableInfo:
    :return:
    """
    script = ''
    if len(primaryKeys) > 0:
        script += '\r\tCONSTRAINT [{0}] PRIMARY KEY CLUSTERED\r\t('.format(primaryKeys[0].Name)
        num = 0
        for ic in primaryKeys[0].IndexColumns:
            script += '\r\t\t'+ic.ColumnName
            if ic.IsDescendingKey:
                script += ' DESC'
            else:
                script += ' ASC'
            if num < len(primaryKeys[0].IndexColumns)-1:
                script += ','
            num += 1
        script += '\r\t) WITH (STATISTICS_NORECOMPUTE  = OFF,'
        if primaryKeys[0].IsPadded:
            script += ' PAD_INDEX  = ON,'
        else:
            script += ' PAD_INDEX  = OFF,'
        if primaryKeys[0].IgnoreDupKey:
            script += ' IGNORE_DUP_KEY = ON,'
        else:
            script += ' IGNORE_DUP_KEY = OFF,'
        if primaryKeys[0].AllowRowLocks:
            script += ' ALLOW_ROW_LOCKS  = ON,'
        else:
            script += ' ALLOW_ROW_LOCKS  = OFF,'
        if primaryKeys[0].AllowPageLocks:
            script += ' ALLOW_PAGE_LOCKS  = ON'
        else:
            script += ' ALLOW_PAGE_LOCKS  = OFF'
        script += ') ON [PRIMARY]'
    return  script

def getTablePrimaryKeyDescriptScript(tableInfo,primaryKeys):
    """
    主键的描述
    :param tableInfo:
    :param primaryKeys:
    :return:
    """
    if primaryKeys is not None and len(primaryKeys) > 0:
        return  "\rEXEC sys.sp_addextendedproperty " \
                     "@name=N'MS_Description', " \
                     "@value=N'{0}' , " \
                     "@level0type=N'SCHEMA'," \
                     "@level0name=N'{1}', " \
                     "@level1type=N'TABLE'," \
                     "@level1name=N'{2}'" \
                     "\rGO\r".format(primaryKeys[0].Description,tableInfo.Schema,tableInfo.Name)
    return ''

def genTableColumnScript(tableInfo,primaryKeys):
    script = ''
    desScript = ''
    num = 0
    for col in tableInfo.Columns:
        script +=  '\r\t[{0}] '.format(col.Name)     #列名称
        script +=  ' [{0}]'.format(col.DataType)     #数据类型
        if col.DataType.upper() in needShowMaxLenghtDataTypes: #最大长度
            script +=  '({0})'.format(col.MaxLength)
        if not col.AllowNull:#是否允许空
            script +=  ' NOT NULL'
        if col.IsIdentity: #自增信息
            script += ' IDENTITY({0},{1})'.format(col.IdentitySeed,col.IdentityIncrement)
        # if col.Collation != None:   #字符集
        #     script += ' COLLATE {0}'.format(col.Collation)
        if num < len(tableInfo.Columns) - 1 and len(primaryKeys) > 0:
            script += ','
        num += 1
    return script

def genTableColumnDescriptScript(tableInfo):
    script = ''
    for col in tableInfo.Columns:
        if col.Description is not None and len(col.Description) > 0: #列描述相关脚本
                script += "\rEXEC sys.sp_addextendedproperty " \
                          "@name=N'MS_Description',@value=N'{0}', " \
                          "@level0type=N'SCHEMA',@level0name=N'{1}', " \
                          "@level1type=N'TABLE',@level1name=N'{2}', " \
                          "@level2type=N'COLUMN',@level2name=N'{3}'\rGO\r".format(col.Description,tableInfo.Schema,tableInfo.Name,col.Name)
    return script

def genTabelForeignKeyScript(tableInfo):
    """
    生成外键相关脚本
    :param tableInfo:
    :return:
    """

    script = ''
    if tableInfo.ForeignKeys != None and len(tableInfo.ForeignKeys) > 0:
        for fk in tableInfo.ForeignKeys:
            script += "\rALTER TABLE [{0}].[{1}] " \
                        "WITH CHECK ADD  CONSTRAINT [{2}] " \
                        "FOREIGN KEY([{3}]) " \
                        "REFERENCES [{4}].[{5}] ([{6}])" \
                        "\r" .format(tableInfo.Schema,tableInfo.Name,
                                   fk.Name,
                                   fk.ColumnName,
                                   fk.RefrencedObjectSchema,fk.RefrencedObjectName,fk.RefrencedColumn,)
            script += "\rGO\r" \
                        "ALTER TABLE [{0}].[{1}] CHECK CONSTRAINT [{2}]" \
                        "\rGO\r".format(tableInfo.Schema,tableInfo.Name,fk.Name)
            if len(fk.Description) > 0:
                script+="\rEXEC sys.sp_addextendedproperty " \
                          "@name=N'MS_Description', " \
                          "@value=N'{0}' , " \
                          "@level0type=N'SCHEMA'," \
                          "@level0name=N'{1}', " \
                          "@level1type=N'TABLE'," \
                          "@level1name=N'{2}', " \
                          "@level2type=N'CONSTRAINT'," \
                          "@level2name=N'{3}'" \
                        "\rGO\r".format(fk.Description,tableInfo.Schema,tableInfo.Name,fk.Name)
    return script

def genTableDefintionScript(tableInfo):
    script = ''
    #生成默认约束相关脚本
    if tableInfo.DefaultConstraints != None and len(tableInfo.DefaultConstraints) > 0:
        for dc in tableInfo.DefaultConstraints:
            script += "\rALTER TABLE [{0}].[{1}] " \
                        "ADD  CONSTRAINT [{2}]  DEFAULT {3} " \
                        "FOR [{4}]" \
                        "\rGO\r".format(tableInfo.Schema,tableInfo.Name,
                                        dc.Name,dc.Definition,
                                        dc.ColumnName)
            if dc.Description is not None and len(dc.Description):
                script += "\rEXEC sys.sp_addextendedproperty " \
                          "@name=N'MS_Description', " \
                          "@value=N'{0}' , " \
                          "@level0type=N'SCHEMA',@level0name=N'{1}', " \
                          "@level1type=N'TABLE',@level1name=N'{2}', " \
                          "@level2type=N'CONSTRAINT',@level2name=N'{3}'" \
                          "\rGO\r".format(dc.Description,tableInfo.Schema,tableInfo.Name,dc.Name)
    return script
