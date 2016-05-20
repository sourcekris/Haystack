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

from collections import defaultdict
from collections import namedtuple
import logging
import time

from haystack_topology.parse_event_bolt import Record

from pyleus.storm import SimpleBolt

log = logging.getLogger('counter')

QueryRate = namedtuple("QueryRate", "timestamp srcip qrate")

class QueryRateBolt(SimpleBolt):

    OUTPUT_FIELDS = QueryRate

    def initialize(self):
        self.sources = defaultdict(int)

    def process_tick(self):
        timestamp = int(time.strftime("%s",time.gmtime())) * 1000
        for srcip,qnum in self.sources.iteritems():
            qrate = float(qnum) / float(self.conf.tick_tuple_freq)
            qr = QueryRate(timestamp, srcip, qrate)
            self.emit(qr)
            log.debug(repr(qr))
        self.sources.clear()
            
    def process_tuple(self, tup):
        record = Record(*tup.values)
        self.sources[record.srcip] += 1 

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/var/log/haystack/query_rate_bolt.log',
        format="%(message)s",
        filemode='a',
    )

    QueryRateBolt().run()

