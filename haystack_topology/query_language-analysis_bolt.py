#
# QueryLanguageAnalysisBolt -
# 
# Uses some insights on natural language to analyse queries
# to detect possible machine generated 
#
# Features:
#   Implemented - boolean_features: STARTS_WITH_NUMERIC
#   Implemented - boolean_features: ENDS_WITH_NUMERIC
#   Implemented - boolean_features: CONTAINS_00
#   Implemented - boolean_features: CONTAINS_VV
#   Implemented - boolean_features: CONTAINS_4
#   Implemented - boolean_features: CONTAINS_1
#   Implemented - boolean_features: CONTAINS_0
#   scalar_features: DIGIT_RATIO
#   scalar_features: HYPHEN_COUNT
#   Implemented - scalar_features: LENGTH
#   Implemented - scalar_features: WC
#   Implemented - scalar_features: PHONEME_COUNT
#   Implemented - scalar_features: PHONEME_LENGTH_RATIO
#   Implemented - scalar_features: PHONEME_WC_RATIO
#   Implemented - scalar_features: WC_LENGTH_RATIO

from collections import namedtuple
from itertools import groupby
import logging
import math
import re

from pyleus.storm import SimpleBolt

from haystack_topology.parse_event_bolt import Record

log = logging.getLogger('query_language-analysis_bolt')

QLang = namedtuple("QLang", "query qlangscore plratio wlratio pwratio")

class QueryLanguageAnalysisBolt(SimpleBolt):

    OUTPUT_FIELDS = QLang

    OPTIONS = ["public_suffix_list", "phoneme_dictionary", "english_corpus"]

    def initialize(self):
        self.pub_sufs = [x.strip() for x in open(self.options["public_suffix_list"],"r").readlines() if not x.startswith('//') and not x.startswith('\n')]

        rawphonemes = [x.strip().lower() for x in open(self.options["phoneme_dictionary"],"r").readlines() if not x.startswith(';;;') and not x.startswith('\n')]
        self.phonemes = {}
        for r in rawphonemes:
            t = r.split()
            self.phonemes[t[0]] = len(t[1:])

        self.dictionary = dict((w, len(list(ws))) for w, ws in groupby(sorted(self.words(open(self.options["english_corpus"]).read()))))
        self.max_word_length = max(map(len, self.dictionary))
        self.total = float(sum(self.dictionary.values()))

    def viterbi(self, text):
        probs, lasts = [1.0], [0] 
        for i in range(1, len(text) + 1): 
            prob_k, k = max((probs[j] * self.word_prob(text[j:i]), j) for j in range(max(0, i - self.max_word_length), i)) 
            probs.append(prob_k)
            lasts.append(k)
        words = []
        i = len(text)
        while 0 < i:
            words.append(text[lasts[i]:i])
            i = lasts[i]
        words.reverse()
        return words   

    def word_prob(self, word): 
        return self.dictionary.get(word, 0) / self.total

    def words(self, text): 
        return re.findall('[a-z]+', text.lower()) 

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

    # searches query for words and returns
    # the number of words and phonemes found
    def word_phoneme_count(self, query):
        phonemecount = 0
        wordcount    = 0 

        for q in query.split('.'): 
            if '-' in q:
                searchspace = q.split('-')
                wordcount += len(searchspace)

                for p in searchspace:
                    if p in self.phonemes:
                        phonemecount += self.phonemes[p]
                    else:
                        vitwords = self.viterbi(p)
                        wordcount += len(vitwords)
                        for v in vitwords:
                            if v in self.phonemes:
                                phonemecount += self.phonemes[v]
                            else:
                                phonemecount += len(v)


            else:   
                if q in self.phonemes:
                    phonemecount += self.phonemes[q]
                    wordcount += 1
                else:
                    vitwords = self.viterbi(q)
                    wordcount += len(vitwords)
                    for v in vitwords:
                        if v in self.phonemes:
                            phonemecount += self.phonemes[v]
                        else:
                            phonemecount += len(v)

        log.debug('[*] Query: {0} WC {1} PC {2}'.format(query, wordcount, phonemecount))
        return wordcount, phonemecount

    def process_tuple(self, tup):
        qdata = Record(*tup.values)
        nosuf = self.remove_suffix(qdata.query)
        wc,pc = self.word_phoneme_count(nosuf)
    
        # Calculate the metrics
        qlangscore = wc + pc
        plratio = float(pc)/float(len(qdata))
        wlratio = float(wc)/float(len(qdata))
        pwratio = float(pc)/float(wc)

        # Boolean conditions that inflate the qlangscore
        for q in nosuf.split('.'):
            if q[0].isdigit():
                qlangscore += 5
            if q[-1].isdigit():
                qlangscore += 5
            if 'vv' in q:
                qlangscore += 5
            if '00' in q:
                qlangscore += 5
            if '4' in q:
                qlangscore += 3
            if '1' in q:
                qlangscore += 3
            if '0' in q:
                qlangscore += 3

            nums = sum(c.isdigit() for c in q)
            ltrs = sum(c.isalpha() for c in q)
            dash = sum(c is '-' for c in q)

            if ltrs > 0:
                digitratio = float(nums) / float(ltrs)
            else:
                digitratio = 1

            hyphenratio = float(dash) / float(len(q))

            if digitratio > 0.3:
                qlangscore += 5
            if hyphenratio > 0.2:
                qlangscore += 5

            log.debug(repr([q,nums,ltrs,dash,digitratio, hyphenratio]))

        ql = QLang(
            qdata.query, 
            wc+pc,
            plratio,
            wlratio,
            pwratio)
        log.debug(repr(ql))
        self.emit(ql, anchors=[tup])

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='/var/log/haystack/query_language-analysis_bolt.log',
        format="%(message)s",
        filemode='a',
    )

    QueryLanguageAnalysisBolt().run()

