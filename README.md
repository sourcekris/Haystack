# Project: Haystack
```
    ____            _           _   
   |  _ \ _ __ ___ (_) ___  ___| |_ 
   | |_) | '__/ _ \| |/ _ \/ __| __|
   |  __/| | | (_) | |  __/ (__| |_ 
   |_|  _|_|  \___// |\___|\___|\__|
   | | | | __ _ _|__/ ___| |_ __ _  ___| | __
   | |_| |/ _` | | | / __| __/ _` |/ __| |/ /
   |  _  | (_| | |_| \__ \ || (_| | (__|   < 
   |_| |_|\__,_|\__, |___/\__\__,_|\___|_|\_\
                |___/                        

```
### Introduction
A storm topology for detection of DNS tunnels. Written for ITC571 Emerging Technologies and Innovation, Charles Sturt University. 

### Version
0.8 beta build 20160520002

### Author
Kris Hunt

### License
This is released under the BSD license. See LICENSE.md for more information.

### Abstract
DNS exfiltration via covert channels has become a very real threat to corporations and consumers as the toolsets available to threat actors have matured. Lost or stolen data about individuals can cause irreparable harm to those individual’s livelihood or financial circumstances. Ongoing research shows that the amount of data stolen during data breach incidents are growing and that the larger the haul of stolen data records the larger the payout for organised cyber criminals. Additionally, data breaches are occurring more often and as more industries adopt mandatory reporting regulations the very real chance of any one business suffering damage publicly from a data breach is climbing rapidly. The detection of this type of data loss is an emerging field of cyber security and the detection of exfiltration and infiltration via DNS covert channels is a sub category of this field which so far has focussed on limited methods of detection. Primarily the current work in this field leverages historical records or packet capture and analysis based passive detection methods. Promising research into more real-time statistical analysis algorithms have so far not yielded practical real-time implementations. This project seeks to design a system which addresses these two primary concerns by delivering real-time detection of covert channels that use DNS without historial information. Further, it intends to address the non-practical nature of previous findings by selecting and applying modern, open-source, networking, network security and data science frameworks to the problem.

### Implementation
Initial implementation intended for academic use only 

### Requirements
- Apache Storm
- Pyleus
- Python 2.7
- JRE/JDK 1.7 or greater
- Cassandra driver for Python

### Necessary 3rd Party Files
- Download copy of CMU phoneme dictionary from here: http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b
- Download a large English language corpus, I tested with this one: https://www.keithv.com/software/wlist/ (1.69 million words)
- List of public domain suffixes from: https://publicsuffix.org/list/public_suffix_list.dat

### Installation
Install Pyleus and Cassandra driver via Pip
```
apt-get install pip git
pip install pyleus
pip install cassandra-driver
```
Download and unpack Apache Storm, I used 0.9.4 in the development of the topology:
```
wget -O /usr/local/storm.tgz http://apache.mirror.digitalpacific.com.au/storm/apache-storm-0.9.6/apache-storm-0.9.6.tar.gz
cd /usr/local
tar xvf storm.tgz
```
Clone my Haystack repo:
```
git clone https://github.com/sourcekris/Haystack
```

Modify the Pyleus Topology (Haystack/haystacktopology/pyleus_topology.yaml) per your own DNS Bro Log Spout, use Kafka if convenient.

Build the topology JAR:
```
pyleus build Haystack/haystack_topology/pyleus_topology.yaml
```
Test it in local mode:
```
pyleus local haystack_topology.jar -d
```
