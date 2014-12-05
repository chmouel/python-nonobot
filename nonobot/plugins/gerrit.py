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
import sqlite3

import requests

import nonobot.plugins

BASE_QUERY = 'status:open+limit:5&q=status:merged+limit:5'
BASE_URL = 'http://gerrit.sf.ring.enovance.com'

TABLE_CREATE = """
CREATE TABLE IF NOT EXISTS NONOGERRIT (
  REVIEW_ID char(50) not null,
  UPDATED char(50) not null
)
"""


class Plugin(nonobot.plugins.Base):
    parent_class = None
    intervals = 3

    def __init__(self, config):
        self.conn = sqlite3.connect('/tmp/test.db')
        self.cur = self.conn.cursor()
        self.cur.execute(TABLE_CREATE)

    def _send_message(self, msg):
        self.parent_class.send_message(
            mbody=msg,
            mto=self.parent_class.room,
            mtype='groupchat')

    def _check_is_in_database(self, review_id, updated):
        self.cur.execute("""
        SELECT * FROM nonogerrit WHERE review_id=?
        and updated=?
        """, (review_id, updated,))
        if self.cur.fetchone():
            return "PRESENT"
        self.cur.execute("""
        SELECT * FROM nonogerrit WHERE review_id=?""", (review_id,))
        if self.cur.fetchone():
            self.cur.execute("DELETE FROM nonogerrit WHERE review_id=?",
                             (review_id,))
            self.conn.commit()
            return "UPDATE"
        return "NEW"

    def add(self, msg, **kwargs):
        """add a project to watch."""
        pass

    def _insert_in_database(self, review_id, updated):
        self.cur.execute("INSERT INTO nonogerrit VALUES(?, ?)",
                         (review_id, updated))
        self.conn.commit()

    def _refresh_gerrit(self):
        req = requests.get("%s/changes/?q=%s" % (BASE_URL, BASE_QUERY))
        text = req.text.replace(")]}'\n", '')
        jz = json.loads(text)
        if not jz:
            return

        for row in jz[0] + jz[1]:
            status_check = self._check_is_in_database(row['id'],
                                                      row['updated'])
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
            print(message % row)
            self._insert_in_database(row['id'], row['updated'])

    def _init_poll(self, parent_class):
        self.parent_class = parent_class
        return (self.intervals, self._refresh_gerrit)


if __name__ == '__main__':
    p = Plugin({})
    p._refresh_gerrit()
