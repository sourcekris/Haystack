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
# ParseEventBolt
#

import logging
import hashlib
import random
from collections import namedtuple
from pyleus.storm import SimpleBolt

log = logging.getLogger('parse_event_bolt')

Record = namedtuple('Record', 'eventid timestamp srcip srcport dstip dstport query qtype ttl')

class ParseEventBolt(SimpleBolt):

    OUTPUT_FIELDS = Record

    def process_tuple(self, tup):
        line, = tup.values
        eventdata = line.split('\t')
        timestamp = eventdata[0].split()[1]
        broid     = eventdata[1]
        ha = hashlib.md5()
        ha.update(timestamp+broid+str(tup.id))
        eventid = ha.hexdigest()
        try: 
            record = Record(
                    eventid,        # eventid md5(timestamp+broid+tup.id)
                    timestamp,      # timestamp
                    eventdata[2],   # srcip
                    eventdata[3],   # srcport
                    eventdata[4],   # dstip
                    eventdata[5],   # dstport
                    eventdata[8],   # query
                    eventdata[12],  # qtype
                    eventdata[20])  # ttl

            log.debug(repr(record))
            self.emit(record, anchors=[tup])
        except IndexError:
            log.debug('[*] IndexError. No emit this tuple.')
            pass

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/var/log/haystack/parse_event_bolt.log',
        format="%(message)s",
        filemode='a',
    )
    ParseEventBolt().run()

