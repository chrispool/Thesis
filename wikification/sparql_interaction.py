#######################
# sparql_interaction.py
#######################
# This file handles DBpedia interaction.

from SPARQLWrapper import SPARQLWrapper, JSON


def processQuery(query): # process SPARQL query and return a list with answers
    sparql = SPARQLWrapper("http://nl.dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    answerlist = []

    if query.startswith("ask where"): # boolean value
        return results["boolean"]
    else: # regular answer
        sortedargs = []
        for result in results["results"]["bindings"]:
            if not sortedargs:
                # try to return results in the right order: it's a bit crude, just
                # sort the keys by name
                for arg in result:
                    sortedargs.append(arg)
                sortedargs = sorted(sortedargs)
            if len(sortedargs) == len(result):
                # if the length of sortedargs is not equal to the length of the
                # dictionary result, don't include the result. Because sortedargs
                # is set the first time we see a result, this can go wrong. I
                # can't really think of something better.
                for arg in sortedargs:
                    answerlist.append(result[arg]["value"])

    return answerlist