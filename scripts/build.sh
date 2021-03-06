# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Hudson build script for running tests
#
# peterbe@mozilla.com
#
# Inspired by Zamboni
# https://github.com/mozilla/zamboni/blob/master/scripts/build.sh


find . -name '*.pyc' -delete;

virtualenv --no-site-packages env
source env/bin/activate

git submodule update --init --recursive
echo "
from base import *
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'elmo',
        'USER': 'hudson',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'init_command': 'SET storage_engine=InnoDB',
            'charset' : 'utf8',
            'use_unicode' : True,
        },
        'TEST_CHARSET': 'utf8',
        'TEST_COLLATION': 'utf8_general_ci',
    },
}
SECRET_KEY = 'anything'
" > settings/local.py

# the file settings/ldap_settings.py must exist
cp settings/ldap_settings.py-dist settings/ldap_settings.py

## install dependencies
# first, the commented pieces of compiled.txt
pip install MySQL-python==1.2.3c1
pip install python-ldap==2.3.13

## rebuild vendor with peep
rm -rf vendor
./vendor-local/lib/python/peep.py install -r requirements/compiled.txt -r requirements/dev.txt --target=vendor

FORCE_DB=true python manage.py test --noinput
