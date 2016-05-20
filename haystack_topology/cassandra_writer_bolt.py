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
#
# Multipurpose Cassandra Writer bolt.
#

import logging

from pyleus.storm import SimpleBolt

log = logging.getLogger('cassandra_writer')

from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

from haystack_topology.parse_event_bolt import Record
from haystack_topology.query_language_analysis_bolt import QLang
from haystack_topology.query_length_bolt import QLRecord
from haystack_topology.query_shannon_entropy_bolt import QEntropy
from haystack_topology.query_rate_bolt import QueryRate

class CassandraWriter(SimpleBolt):

    OPTIONS = ["cassandra_ip"]

    def initialize(self):
        self.cluster = Cluster([self.options["cassandra_ip"]])
        self.session = self.cluster.connect()

    def write_event(self, line):
        prepared = self.session.prepare("""
         INSERT INTO haystack.events (eventid, timestamp, srcip, srcport, dstip, dstport, query, qtype, ttl)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""")
        self.session.execute(prepared, (line.eventid, line.timestamp, line.srcip, int(line.srcport), line.dstip, int(line.dstport), line.query, line.qtype, line.ttl))

    def write_qlang(self, line):
        prepared = self.session.prepare("""
         INSERT INTO haystack.qlang (eventid, query, qlangscore, plratio, wlratio, pwratio)
         VALUES (?, ?, ?, ?, ?, ?)""")
        self.session.execute(prepared, (line.eventid, line.query, int(line.qlangscore), float(line.plratio), float(line.wlratio), float(line.pwratio)))

    def write_qentropy(self, line):
        prepared = self.session.prepare("""
         INSERT INTO haystack.qentropy (eventid, query, qentropy)
         VALUES (?, ?, ?)""")
        self.session.execute(prepared, (line.eventid, line.query, float(line.qentropy)))

    def write_qlengths(self, line):
        prepared = self.session.prepare("""
         INSERT INTO haystack.qlengths(eventid, query, qlength)
         VALUES (?, ?, ?)""")
        self.session.execute(prepared, (line.eventid, line.query, int(line.qlength)))

    def write_qrate(self, line):
        prepared = self.session.prepare("""
         INSERT INTO haystack.qrate(timestamp, srcip, qrate)
         VALUES (?, ?, ?)""")
        self.session.execute(prepared, (line.timestamp, line.srcip, float(line.qrate)))

    def process_tuple(self, tup):
        if tup.comp == "parse_event_bolt":
            line = Record(*tup.values)
            self.write_event(line)
        elif tup.comp == "query_language_analysis_bolt":
            line = QLang(*tup.values)
            self.write_qlang(line)
        elif tup.comp == "query_length_bolt":
            line = QLRecord(*tup.values)
            self.write_qlengths(line)
        elif tup.comp == "query_rate_bolt":
            line = QueryRate(*tup.values)
            self.write_qrate(line)
        elif tup.comp == "query_shannon_entropy_bolt":
            line = QEntropy(*tup.values)
            self.write_qentropy(line)
        else:
            line = tup.values
            log.debug('cassandra_writer_bolt: no action for ' + repr(line) + repr(tup))
            
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/var/log/haystack/cassandra_writer.log',
        format="%(message)s",
        filemode='a',
    )
    CassandraWriter().run()
