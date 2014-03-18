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
import logging
import random
import requests

import nonobot.plugins

BASE_URL = 'http://api.urbandictionary.com/v0'


class Plugin(nonobot.plugins.Base):
    def urban(self, msg, **kwargs):
        """get a definition from urban dictionary (eg: urban foo 3)."""
        split = msg['body'].split()
        index = 1
        method = 'define'
        query = msg['body']

        if not split or split[-1].isdigit() and len(split) == 1:
            method = 'random'
        elif split[-1].isdigit():
            index = int(split[-1])
            query = " ".join(split[0:-1])
        logging.debug("urban %s: index: %d", query, index)

        index = index - 1
        if method == 'define':
            url = "%s/define?term=%s" % (BASE_URL, query)
        elif method == 'random':
            url = "%s/random" % (BASE_URL)

        logging.debug('urban: url: %s', url)
        req = requests.get(url)

        json = req.json()

        # Probably need to do better than that
        amount = len(json['list'])
        if amount == 0:
            return "Don't make up crap please. That thing don't even " \
                "exist in the urban dictionary"
        if index > amount:
            return "That's way too much we have only %s items" % amount

        if method == 'define':
            item = json['list'][index]
            index_label = '[%d/%d] ' % (index + 1, amount)
        elif method == 'random':
            rnd = random.randint(0, amount - 1)
            item = json['list'][rnd]
            index_label = '[%s]' % (item['word'])

        definition = item['definition'].replace('\r\n', " ")
        example = item['example'].replace('\r\n', " ")
        ret = "%s %s example: %s / %s" % (index_label,
                                          definition,
                                          example,
                                          item['permalink'])
        return ret
