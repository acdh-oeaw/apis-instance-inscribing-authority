from apis_core.utils.rdf import Attribute, Filter


class MonumentFromWikidata:
    filter_monument = Filter([("wdt:P31", "wd:Q162875")])
    name = Attribute(
        [
            "rdfs:label,de",
            "rdfs:label,en",
            "wdt:P1448/rdfs:label",
            "rdfs:label",
        ]
    )

    same_as = Attribute(
        ["owl:sameAs", "wdtn:P227", "wdtn:P1566", "wdtn:P214", "wdtn:P244"]
    )
