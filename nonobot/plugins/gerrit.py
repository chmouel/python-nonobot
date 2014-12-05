# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import json
import logging
import os
import sqlite3

import requests

import nonobot.plugins

BASE_QUERY = 'status:open+limit:5&q=status:merged+limit:5'
BASE_URL = 'http://gerrit.sf.ring.enovance.com'

CREATE_TABLE_CHANGES = """
CREATE TABLE IF NOT EXISTS NONOGERRIT_CHANGES (
  REVIEW_ID char(50) not null,
  UPDATED char(50) not null
)
"""

CREATE_TABLE_CONFIG = """
CREATE TABLE IF NOT EXISTS NONOGERRIT_CONFIG (
  PROPERTY char(50) not null,
  VALUE char(50) not null
)
"""


class Plugin(nonobot.plugins.Base):
    parent_class = None
    intervals = 60

    def __init__(self, config):
        cache_path = "/tmp"
        self.db_path = os.path.join(cache_path, "nono_gerrit_changes.db")

        self.conn = None
        self.cur = None

        self.projects_to_watch = None

        self._open_db()
        self.cur.execute(CREATE_TABLE_CONFIG)
        self.cur.execute(CREATE_TABLE_CHANGES)
        self.conn.commit()
        self.conn.close()

    def _send_message(self, msg):
        self.parent_class.send_message(
            mbody=msg,
            mto=self.parent_class.room,
            mtype='groupchat')

    def _open_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

    def _check_is_in_database(self, review_id, updated):
        self.cur.execute("""
        SELECT * FROM nonogerrit_changes WHERE review_id=?
        and updated=?
        """, (review_id, updated,))
        if self.cur.fetchone():
            return "PRESENT"
        self.cur.execute("""
        SELECT * FROM nonogerrit_changes WHERE review_id=?""", (review_id,))
        if self.cur.fetchone():
            self.cur.execute("DELETE FROM nonogerrit_changes "
                             "WHERE review_id=?", (review_id,))
            self.conn.commit()
            return "UPDATED"
        return "NEW"

    def _list_project_in_databases(self):
        query = """SELECT value from nonogerrit_config where
        property='watched_projects'"""
        self.cur.execute(query)
        ret = self.cur.fetchmany()
        return [t[0] for t in ret]

    def _watch_project(self, project):
        query = """INSERT INTO nonogerrit_config
        VALUES('watched_projects', ?)"""
        self.cur.execute(query, (project,))
        self.conn.commit()

    def _delete_project_to_watch(self, project):
        query = ("DELETE FROM nonogerrit_config WHERE "
                 "property='watched_projects' AND value=?")
        self.cur.execute(query, (project,))
        self.conn.commit()

    def _insert_in_database(self, review_id, updated):
        self.cur.execute("INSERT INTO nonogerrit_changes VALUES(?, ?)",
                         (review_id, updated))
        self.conn.commit()

    def gerrit_config(self, msg, **kwargs):
        """add/del/list a project to watch."""
        _msg = msg['body'].split()
        if not _msg:
            return "OPTIONS are [add, list, del]"

        prop = _msg[0]
        if self.projects_to_watch is None:
            self._open_db()
            self.projects_to_watch = self._list_project_in_databases()
            self.conn.close()

        if prop == "add":
            project = _msg[1]
            if project in self.projects_to_watch:
                return "%s is already watched!" % project
            else:
                self._open_db()
                self.projects_to_watch.append(project)
                self._watch_project(project)
                self.conn.close()
                return "I will watch %s from now on" % project

        if prop == "list":
            if not self.projects_to_watch:
                return "No project watched :("
            return "I am watching: " + ", ".join(self.projects_to_watch)

        if prop == "del":
            project = _msg[1]
            if project not in self.projects_to_watch:
                return "%s is already watched!" % project
            else:
                self._open_db()
                self.projects_to_watch.remove(project)
                self._delete_project_to_watch(project)
                self.conn.close()
                return "%s is not watched anymore" % project

    def _refresh_gerrit(self):

        req = requests.get("%s/changes/?q=%s" % (BASE_URL, BASE_QUERY))
        text = req.text.replace(")]}'\n", '')
        jz = json.loads(text)
        if not jz:
            return

        if self.projects_to_watch is None:
            self._open_db()
            self.projects_to_watch = self._list_project_in_databases()
            self.conn.close()

        for row in jz[0] + jz[1]:
            self._open_db()
            status_check = self._check_is_in_database(row['id'],
                                                      row['updated'])
            self.conn.close()

            if row['project'] not in self.projects_to_watch:
                logging.debug("SKIPPING PROJECT: %s" % row['project'])
                continue

            if status_check == "PRESENT":
                # skipping it's already exist
                continue
            elif row['status'] == "MERGED":
                status = "MERGED"
            else:
                status = status_check

            row['status'] = status

            message = ("%(project)s: %(status)s %(subject)s "
                       "by %(owner)s: %(url)s")
            row['owner'] = row['owner']['name']
            url = "%s/r/#/c/%d" % (BASE_URL, row['_number'])
            row['url'] = url
            self._send_message(message % row)
            self._open_db()
            self._insert_in_database(row['id'], row['updated'])
            self.conn.close()

        self.conn.close()

    def _init_poll(self, parent_class):
        self.parent_class = parent_class
        return (self.intervals, self._refresh_gerrit)


if __name__ == '__main__':
    p = Plugin({})
    p._refresh_gerrit()
