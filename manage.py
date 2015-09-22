from flask.ext.migrate import Migrate, MigrateCommand
from tuneful.database import Base
from tuneful import app
from flask.ext.script import Manager

class DB(object):
    def __init__(self, metadata):
        self.metadata = metadata

migrate = Migrate(app, DB(Base.metadata))
manager = Manager(app)
manager.add_command('db', MigrateCommand)

print manager
print app
print migrate