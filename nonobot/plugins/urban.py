import logging
import random
import requests

import nonobot.plugins

BASE_URL = 'http://api.urbandictionary.com/v0'


class Plugin(nonobot.plugins.Base):
    def urban(self, query):
        """get a definition from urban dictionary (eg: urban foo 3)."""
        split = query.split()
        index = 1
        method = 'define'

        if not split or split[-1].isdigit() and len(split) == 1:
            method = 'random'
        elif split[-1].isdigit():
            index = int(split[-1])
            query = " ".join(split[0:-1])
        else:
            query = " ".join(query)
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
            return "That's way too much we have only %s items" % index

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
