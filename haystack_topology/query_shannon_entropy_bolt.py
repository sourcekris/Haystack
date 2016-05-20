#    ____            _           _   
#   |  _ \ _ __ ___ (_) ___  ___| |_ 
#   | |_) | '__/ _ \| |/ _ \/ __| __|
#   |  __/| | | (_) | |  __/ (__| |_ 
#   |_|  _|_|  \___// |\___|\___|\__|
#   | | | | __ _ _|__/ ___| |_ __ _  ___| | __
#   | |_| |/ _` | | | / __| __/ _` |/ __| |/ /
#   |  _  | (_| | |_| \__ \ || (_| | (__|   < 
#   |_| |_|\__,_|\__, |___/\__\__,_|\___|_|\_\
#                |___/                        
#
# QueryShannonEntropyBolt -
# 
# Calculates the shannon entropy of the query minus any known
# domain suffix and emits a tuple of the query + shannon entropy 
# value to the topology as a floating point number.
#
#

from collections import namedtuple
import logging
import math

from pyleus.storm import SimpleBolt

from haystack_topology.parse_event_bolt import Record

log = logging.getLogger('query_shannon-entropy_bolt')

QEntropy = namedtuple("QEntropy", "eventid query qentropy")

class QueryShannonEntropyBolt(SimpleBolt):

    OUTPUT_FIELDS = QEntropy

    OPTIONS = ["public_suffix_list"]

    def initialize(self):
        self.pub_sufs = [x.strip() for x in open(self.options["public_suffix_list"],"r").readlines() if not x.startswith('//') and not x.startswith('\n')]

    def remove_suffix(self, query):
        possible_suffixes = []
        for suf in self.pub_sufs:
            if len(suf) < len(query):
                if query.endswith('.'+suf):
                    possible_suffixes.append(suf)
        if len(possible_suffixes) > 0:
            return query.replace('.'+max(possible_suffixes,key=len),'')
        else:
            return query

    def shannon(self, query):
        entropy = 0.0
        length = len(query)
        occ = {}
        for c in query:
            if not c in occ:
                occ[c] = 0
            occ[c] += 1
        for (k,v) in occ.iteritems():
            p = float( v ) / float(length)
            entropy -= p * math.log(p, 2)
        return entropy

    def process_tuple(self, tup):
        qdata = Record(*tup.values)
        qse = self.shannon(self.remove_suffix(qdata.query))
        qe = QEntropy(qdata.eventid, qdata.query, qse)
        log.debug(repr(qe))
        self.emit(qe, anchors=[tup])


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/var/log/haystack/query_shannon-entropy_bolt.log',
        format="%(message)s",
        filemode='a',
    )

    QueryShannonEntropyBolt().run()

