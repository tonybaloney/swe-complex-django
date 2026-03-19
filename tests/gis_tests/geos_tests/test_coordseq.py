from unittest import skipIf

from django.contrib.gis.geos import GEOSGeometry, LineString
from django.contrib.gis.geos.libgeos import geos_version_tuple
from django.test import SimpleTestCase


class GEOSCoordSeqTest(SimpleTestCase):
    def test_getitem(self):
        coord_seq = LineString([(x, x) for x in range(2)]).coord_seq
        for i in (0, 1):
            with self.subTest(i):
                self.assertEqual(coord_seq[i], (i, i))
        for i in (-3, 10):
            msg = f"Invalid GEOS Geometry index: {i}"
            with self.subTest(i):
                with self.assertRaisesMessage(IndexError, msg):
                    coord_seq[i]

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_getitem_m_dimension(self):
        coord_seq = GEOSGeometry("LINESTRING M (1 2 3, 4 5 6)").coord_seq
        self.assertEqual(coord_seq[0], (1.0, 2.0, 3.0))
        self.assertEqual(coord_seq[1], (4.0, 5.0, 6.0))
        self.assertFalse(coord_seq.hasz)
        self.assertTrue(coord_seq.hasm)

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_getitem_zm_dimension(self):
        coord_seq = GEOSGeometry("LINESTRING ZM (1 2 3 4, 5 6 7 8)").coord_seq
        self.assertEqual(coord_seq[0], (1.0, 2.0, 3.0, 4.0))
        self.assertEqual(coord_seq[1], (5.0, 6.0, 7.0, 8.0))
        self.assertTrue(coord_seq.hasz)
        self.assertTrue(coord_seq.hasm)
