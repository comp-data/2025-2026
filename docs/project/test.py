# -*- coding: utf-8 -*-
# Copyright (c) 2026, Ivan Heibi <ivan.heibi2@unibo.it>
#
# Permission to use, copy, modify, and/or distribute this software for any purpose
# with or without fee is hereby granted, provided that the above copyright notice
# and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
# DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

import unittest
from os import sep
from pandas import DataFrame
from impl import CitationUploadHandler, BibliographicEntityUploadHandler
from impl import CitationQueryHandler, BibliographicEntityQueryHandler
from impl import FullQueryEngine
from impl import Citation, BibliographicEntity, AuthorSelfCitation, JournalSelfCitation

# REMEMBER: before launching the tests, please run the Blazegraph instance!

class TestProjectBasic(unittest.TestCase):

    # The paths of the files used in the test should change depending on what you want to use
    # and the folder where they are. Instead, for the graph database, the URL to talk with
    # the SPARQL endpoint must be updated depending on how you launch it - currently, it is
    # specified the URL introduced during the course, which is the one used for a standard
    # launch of the database.
    citation = "data" + sep + "dh_citations.csv"
    bib_entity = "data" + sep + "dh_metadata.json"
    relational = "." + sep + "relational.db"
    graph = "http://127.0.0.1:9999/blazegraph/sparql"

    def test_01_CitationUploadHandler(self):
        u = CitationUploadHandler()
        self.assertTrue(u.setDbPathOrUrl(self.graph))
        self.assertEqual(u.getDbPathOrUrl(), self.graph)
        self.assertTrue(u.pushDataToDb(self.citation))

    def test_02_BibliographicEntityUploadHandler(self):
        u = BibliographicEntityUploadHandler()
        self.assertTrue(u.setDbPathOrUrl(self.relational))
        self.assertEqual(u.getDbPathOrUrl(), self.relational)
        self.assertTrue(u.pushDataToDb(self.bib_entity))

    def test_03_CitationQueryHandler(self):
        q = CitationQueryHandler()
        self.assertTrue(q.setDbPathOrUrl(self.graph))
        self.assertEqual(q.getDbPathOrUrl(), self.graph)

        self.assertIsInstance(q.getById("just_a_test"), DataFrame)

        self.assertIsInstance(q.getAllCitations(), DataFrame)
        self.assertIsInstance(q.getAllAuthorSelfCitations(), DataFrame)
        self.assertIsInstance(q.getAllJournalSelfCitations(), DataFrame)
        self.assertIsInstance(q.getCitationsWithinTimespan("P2Y","P18Y"), DataFrame)
        self.assertIsInstance(q.getCitationsWithinDate("2010-03","2020"), DataFrame)

    def test_04_ProcessDataQueryHandler(self):
        q = BibliographicEntityQueryHandler()
        self.assertTrue(q.setDbPathOrUrl(self.relational))
        self.assertEqual(q.getDbPathOrUrl(), self.relational)

        self.assertIsInstance(q.getById("just_a_test"), DataFrame)

        self.assertIsInstance(q.getAllBibliographicEntities(), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithTitle("Machine learning"), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithAuthor("Rossi"), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithinPublicationDate("2022","2024"), DataFrame)
        self.assertIsInstance(q.getBibliographicEntitiesWithVenue("Digital Scholarship In The Humanities"), DataFrame)

    def test_05_FullQueryEngine(self):
        jq = CitationQueryHandler()
        jq.setDbPathOrUrl(self.graph)
        cq = BibliographicEntityQueryHandler()
        cq.setDbPathOrUrl(self.relational)

        fq = FullQueryEngine()
        self.assertIsInstance(fq.cleanCitationHandlers(), bool)
        self.assertIsInstance(fq.cleanBibliographicEntityHandlers(), bool)
        self.assertTrue(fq.addCitationHandler(jq))
        self.assertTrue(fq.addBibliographicEntityHandler(cq))

        self.assertEqual(fq.getEntityById("just_a_test"), None)

        r = fq.getAllCitations()
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, Citation)

        r = fq.getAllAuthorSelfCitations()
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, AuthorSelfCitation)

        r = fq.getAllJournalSelfCitations()
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, JournalSelfCitation)

        r = fq.getCitationsWithinTimespan("P2Y","P18Y")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, Citation)

        r = fq.getCitationsWithinDate("2010-03","2020")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, Citation)

        r = fq.getAllBibliographicEntities()
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, BibliographicEntity)

        r = fq.getBibliographicEntitiesWithTitle("Machine learning")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, BibliographicEntity)

        r = fq.getBibliographicEntitiesWithAuthor("Rossi")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, BibliographicEntity)

        r = fq.getBibliographicEntitiesWithinPublicationDate("2022","2024")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, BibliographicEntity)

        r = fq.getBibliographicEntitiesWithVenue("Digital Scholarship In The Humanities")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, BibliographicEntity)

        # FullQueryEngine
        # -----

        r = fq.getAuthorSelfCitationsByName("Matt")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, AuthorSelfCitation)

        r = fq.getJournalSelfCitationsByName("Digital Scholarship In The Humanities")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, JournalSelfCitation)

        r = fq.getCitationsOfBibEntityByTitleWithinDate("machine learning", "2005", "2015")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, Citation)

        r = fq.getReferencesOfBibEntityByTitleWithinTimespan("library", "P2Y", "P15Y")
        self.assertIsInstance(r, list)
        for i in r:
            self.assertIsInstance(i, Citation)
