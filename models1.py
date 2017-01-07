from peewee import *
from playhouse.postgres_ext import *

database = PostgresqlExtDatabase('voiceinn_prot', **{'user': 'postgres', 'password': '12345'})
# print database.connect()

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Organization(BaseModel):
    name = CharField(null=True)
    password = CharField(null=True)
    username = CharField(null=True)

    class Meta:
        db_table = 'organization'

class Moduletype(BaseModel):
    name = CharField(null=True)

    class Meta:
        db_table = 'moduletype'

class Modules(BaseModel):
    dialplan = JSONField(null=True)
    isactive = BooleanField(null=True)
    moduletype = ForeignKeyField(db_column='moduletype_id', null=True, rel_model=Moduletype, to_field='id')
    number = BigIntegerField(null=True)
    org = ForeignKeyField(db_column='org_id', null=True, rel_model=Organization, to_field='id')

    class Meta:
        db_table = 'modules'

class Moduledata(BaseModel):
    module = ForeignKeyField(db_column='module_id', null=True, rel_model=Modules, to_field='id')

    class Meta:
        db_table = 'moduledata'
