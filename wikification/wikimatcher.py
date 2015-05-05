#!/usr/bin/python3

################
# wikimatcher.py
################
# This file handles (fuzzy) word - Wikipedia article/category title matching.

import os, sys
from Levenshtein import ratio
from sparql_interaction import *
import subprocess
from lxml import html


# class WikiMatcher: encapsulates all word - Wikipedia article/category title matching
class WikiMatcher:

    def __init__(self, wikfname):
        # fetch filtered article names (namelist) & "formal" article names (urilist)
        names = self.__getResourceNames(wikfname)
        self.urilist = names[0]
        self.namelist = names[1]


    # try to match a wikipedia article title to a word
    def match(self, word):
        artname = self.__naiveMatching(word)
        if not(artname):
            artname = self.__fuzzyNameMatching(word)[0]

        # first uri try
        uri = "<http://nl.dbpedia.org/resource/" + artname + ">"

        # fix redirection/ambiguous pages
        uri2 = self.ambigRedir(artname)
        # non-empty uri
        if uri2 != "<>":
            uri = uri2

        return uri


    # fix ambiguous/redirection pages
    def ambigRedir(self, artname):
        ambiguous = True
        redir = True
        uri = ""
        redircount = 0
        # keep a backup of the artname in case of infinite loops
        old_artname = artname

        # continue until there are no more ambiguous/redirect pages
        while(ambiguous or redir):
            ### Is http://dbpedia.org/ontology/wikiPageDisambiguates not empty?
            ### Let DBpedia Spotlight do the disambiguation.
            disambig = processQuery("select ?propval where { <http://nl.dbpedia.org/resource/" + \
                                    artname + "> <http://dbpedia.org/ontology/wikiPageDisambiguates> ?propval }")

            if disambig != []:
                curlname = artname.replace("_", " ")#.lower()
                curl_query = 'curl http://spotlight.sztaki.hu:2232/rest/annotate' \
                             ' --data-urlencode "text=' + curlname + '" --data "confidence=0.3"'
                # get the html from the spotlight service
                spotlighthtml = subprocess.Popen(curl_query,stdout=subprocess.PIPE, shell = True,
                                                 stderr=subprocess.DEVNULL).communicate()[0].decode("utf-8")
                # use the lxml package to create a tree from the generated html
                spotlighttree = html.fromstring(spotlighthtml)
                # get the first link
                try:
                    uri = spotlighttree.xpath("//a/@href")[0]
                except IndexError:
                    uri = disambig[0]

                # did the service tag only a part of the text? Use just the first result.
                if spotlighttree.xpath("//div/text()")[0] != '\n':
                    uri = disambig[0]
                artname = uri.replace("http://nl.dbpedia.org/resource/", "")
            else:
                ambiguous = False

            ##### Is http://dbpedia.org/ontology/wikiPageRedirects not empty?
            ##### Find the URI of the redirect.
            redirect = processQuery("select ?propval where { <http://nl.dbpedia.org/resource/" + \
                                    artname + "> <http://dbpedia.org/ontology/wikiPageRedirects> ?propval }")

            if redirect != []:
                uri = redirect[0]
                artname = uri.replace("http://nl.dbpedia.org/resource/", "")
            else:
                redir = False

            redircount += 1

            if redircount == 10:
                # Seems we are stuck in a redirection loop... Let's just return the
                # article uri and hope we can find something.
                uri = "http://nl.dbpedia.org/resource/" + old_artname
                break

        # ook al is de uri leeg, gewoon de oude naam returnen
        if uri == "":
            uri = "http://nl.dbpedia.org/resource/" + old_artname

        return "<" + uri + ">"


    # called when initializing the WikiMatcher, to read in the file containing
    # wikipedia article and category names
    def __getResourceNames(self, wikfname):

        wikfile = open(wikfname, "r")

        namelist = [] # filtered article names
        urilist = [] # original article names
        unwanted = ["in","voor","van","naar","aan","op","voor","en","met","of"]
        # append wikipedia article titles to namelist and uris to urilist
        for uri in wikfile:
            uri_filter = uri.strip()
            # simple tokenizing
            uri_name = uri_filter.replace("_", " ").replace(":", " ").replace(",", " ")\
                                 .replace("-", " ").replace("(", "").replace(")", "").lower()

            wordlist = uri_name.split()
            # remove unwanted words from article names
            for word in wordlist[:]:
                if word in unwanted:
                    wordlist.remove(word)
            namelist.append(" ".join(wordlist))
            urilist.append(uri_filter)

        wikfile.close()

        return (urilist, namelist)


    # just check whether namelist contains word
    def __naiveMatching(self, word):
        # simple word tokenizing
        word = word.replace("_", " ").replace(":", " ").replace(",", " ")\
                   .replace("-", " ").replace("(", "").replace(")", "").lower().strip()

        guesslist = word.split()
        unwanted = ["in","voor","van","naar","aan","op","voor","en","met","of"]

        # remove unwanted words from guesslist
        for guesswords in guesslist[:]:
            if guesswords in unwanted:
                guesslist.remove(guesswords)

        word = " ".join(guesslist)

        if word in self.namelist:
            match_idx = self.namelist.index(word)
            return self.urilist[match_idx]
        else:
            return False

    # Levenshtein matching: least string distance for parts of article names/word
    def __fuzzyNameMatching(self, word):
        # simple word tokenizing
        word = word.replace("_", " ").replace(":", " ").replace(",", " ")\
                   .replace("-", " ").replace("(", "").replace(")", "")\
                   .lower().strip()

        guesslist = word.split()
        unwanted = ["in","voor","van","uit","naar","aan","op","voor","en","met","of"]
        guesslen = len(guesslist)

        # remove unwanted words from guesslist
        for guesswords in guesslist[:]:
            if guesswords in unwanted:
                guesslist.remove(guesswords)

        # determine article titles that approximately match word
        approx_match_list = []
        for artnames in self.namelist:
            rat =  ratio(word,artnames)
            if rat >= 0.4:
                approx_match_list.append(artnames)
        # ensure that approx_match_list contains only unique values
        approx_match_list = list(set(approx_match_list))

        matchlist = []
        for artnames in approx_match_list:
            artnamelist = artnames.split()

            rank = 0
            already_seen = False

            for artwords in artnamelist:
                for guesswords in guesslist:
                    rat = ratio(artwords,guesswords)
                    if rat > 0.8:
                        # check if a word in artnamelist occurs more than asked for in guesslist
                        if already_seen:
                            continue
                        # count the amount of similar words of the current guessword and artword
                        similarcount = 0
                        for artword in artnamelist:
                            if ratio(artword,guesswords) > 0.8:
                                similarcount += 1
                        # count the amount of occurences of guessword in guesslist
                        guess_similarcount = 0
                        for word in guesslist:
                            if ratio(word,guesswords) > 0.8:
                                guess_similarcount += 1

                        if (similarcount > guess_similarcount):
                            already_seen = True

                    rank += pow(4,(rat*10))

            # bonus for overall matching with article name
            rat = ratio(artnames,word)
            rank += pow(3,(rat*10))

            # penalty for strings that are (way) longer or shorter than input string
            diff = abs(len(artnamelist) - len(guesslist))
            rank -= rank * (0.075 * diff)

            matchlist.append((artnames,rank))

        sorted_match = sorted(matchlist, key=lambda tup: tup[1], reverse = True)
        best_match = sorted_match[0][0]
        match_idx = self.namelist.index(best_match)

        #print(sorted_match[:100]) # debug
        return (self.urilist[match_idx], sorted_match[:100])

#################### DEMO

if __name__ == "__main__":

    matcher = WikiMatcher("wikinames/wikinames")

    while True:
        word = input("Please enter a word for me to match (or Enter to quit): ")

        if(word == ""):
            break
        else:
            print(matcher.match(word))