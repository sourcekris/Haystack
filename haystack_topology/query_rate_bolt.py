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
        timestamp = time.strftime("%s",time.gmtime())
        log.debug('[*] QRTick -- {0} --------'.format(timestamp))
        log.debug('[*] QRTick freq: {0} '.format(self.conf.tick_tuple_freq))
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

