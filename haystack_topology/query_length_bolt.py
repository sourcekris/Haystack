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
# QueryLengthBolt

from collections import namedtuple
import logging

from pyleus.storm import SimpleBolt

from haystack_topology.parse_event_bolt import Record

log = logging.getLogger('query_lenght_bolt')

QLRecord = namedtuple("QLRecord", "eventid query qlength")

class QueryLengthBolt(SimpleBolt):

    OUTPUT_FIELDS = QLRecord

    def process_tuple(self, tup):
        qdata = Record(*tup.values)
        qlength = len(qdata.query)
        ql = QLRecord(qdata.eventid, qdata.query, qlength)
        log.debug(repr(ql))
        self.emit(ql, anchors=[tup])

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/var/log/haystack/query_length_bolt.log',
        format="%(message)s",
        filemode='a',
    )

    QueryLengthBolt().run()

