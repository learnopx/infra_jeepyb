#! /usr/bin/env python
# Copyright (C) 2011 OpenStack, LLC.
# Copyright (c) 2012 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import ConfigParser
import os
import StringIO


GERRIT_CONFIG = os.environ.get(
    'GERRIT_CONFIG',
    '/home/gerrit2/review_site/etc/gerrit.config')
GERRIT_SECURE_CONFIG = os.environ.get(
    'GERRIT_SECURE_CONFIG',
    '/home/gerrit2/review_site/etc/secure.config')
db_connection = None


def get_broken_config(filename):
    """gerrit config ini files are broken and have leading tabs."""
    text = ""
    for line in open(filename, "r"):
        text += line.lstrip()

    fp = StringIO.StringIO(text)
    c = ConfigParser.ConfigParser()
    c.readfp(fp)
    return c


def connect():
    global db_connection
    if not db_connection:
        gerrit_config = get_broken_config(GERRIT_CONFIG)
        secure_config = get_broken_config(GERRIT_SECURE_CONFIG)

        DB_TYPE = gerrit_config.get("database", "type")
        DB_HOST = gerrit_config.get("database", "hostname")
        DB_USER = gerrit_config.get("database", "username")
        DB_PASS = secure_config.get("database", "password")
        DB_DB = gerrit_config.get("database", "database")

        if DB_TYPE.upper() == "MYSQL":
            import pymysql
            db_connection = pymysql.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASS, db=DB_DB)
        else:
            import psycopg2
            db_connection = psycopg2.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_DB)
    else:
        try:
            # Make sure the database is responding and reconnect if not
            db_connection.ping(True)
        except AttributeError:
            # This database driver lacks a ping implementation
            pass
    return db_connection
