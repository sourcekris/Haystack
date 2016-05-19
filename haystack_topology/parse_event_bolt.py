import logging
from collections import namedtuple
from pyleus.storm import SimpleBolt

log = logging.getLogger('parse_event_bolt')

Record = namedtuple('Record', 'timestamp srcip srcport dstip dstport query qtype ttl')

class ParseEventBolt(SimpleBolt):

    OUTPUT_FIELDS = Record

    def process_tuple(self, tup):
        line, = tup.values
        eventdata = line.split('\t')
        try: 
            record = Record(
                    eventdata[0].split()[1], # timestamp
                    eventdata[2],            # srcip
                    eventdata[3],            # srcport
                    eventdata[4],            # dstip
                    eventdata[5],            # dstport
                    eventdata[8],            # query
                    eventdata[12],           # qtype
                    eventdata[20])           # ttl

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

