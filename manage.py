#!/usr/bin/env python
from migrate.versioning.shell import main
from migrate.versioning import api
import os

basedir = os.path.dirname(__file__)

REPO_SQLALCHEMY_MIGRATE = os.path.abspath(os.path.join(basedir, 'database/migrations'))

if __name__ == '__main__':
    if not os.path.exists(REPO_SQLALCHEMY_MIGRATE):
        api.create(REPO_SQLALCHEMY_MIGRATE, 'migrations')
    main(repository=REPO_SQLALCHEMY_MIGRATE, url='sqlite:///database/db.sqlite', debug='True')