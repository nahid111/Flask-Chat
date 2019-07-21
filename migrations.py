from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from App import app, db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

from Models.models import *

if __name__ == '__main__':
    manager.run()



## creating/updating tables with flask migrate
##=======================================================================================

## run the following command to create the migration folder (for the 1st time only)
# $ python3 migrations.py db init

## run the following command to create the migration file
# $ python3 migrations.py db migrate

##run the following command to apply the migrations
# $ python3 migrations.py db upgrade