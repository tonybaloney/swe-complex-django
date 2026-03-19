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

    def test_hasz(self):
        coord_seq = LineString([(0, 0, 0), (1, 1, 1)]).coord_seq
        self.assertTrue(coord_seq.hasz)

    def test_hasz_false(self):
        coord_seq = LineString([(0, 0), (1, 1)]).coord_seq
        self.assertFalse(coord_seq.hasz)

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_hasm(self):
        ls = GEOSGeometry("LINESTRING M (0 0 0, 1 1 1)")
        self.assertTrue(ls.coord_seq.hasm)
        self.assertFalse(ls.coord_seq.hasz)

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_hasm_false(self):
        ls = LineString([(0, 0), (1, 1)])
        self.assertFalse(ls.coord_seq.hasm)

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_getitem_m(self):
        ls = GEOSGeometry("LINESTRING M (0 1 2, 3 4 5)")
        coord_seq = ls.coord_seq
        self.assertEqual(coord_seq[0], (0.0, 1.0, 2.0))
        self.assertEqual(coord_seq[1], (3.0, 4.0, 5.0))

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_getitem_zm(self):
        ls = GEOSGeometry("LINESTRING ZM (0 1 2 3, 4 5 6 7)")
        coord_seq = ls.coord_seq
        self.assertEqual(coord_seq[0], (0.0, 1.0, 2.0, 3.0))
        self.assertEqual(coord_seq[1], (4.0, 5.0, 6.0, 7.0))

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_tuple_m(self):
        ls = GEOSGeometry("LINESTRING M (0 1 2, 3 4 5)")
        self.assertEqual(ls.coord_seq.tuple, ((0.0, 1.0, 2.0), (3.0, 4.0, 5.0)))

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_tuple_zm(self):
        ls = GEOSGeometry("LINESTRING ZM (0 1 2 3, 4 5 6 7)")
        self.assertEqual(
            ls.coord_seq.tuple, ((0.0, 1.0, 2.0, 3.0), (4.0, 5.0, 6.0, 7.0))
        )

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_getM(self):
        ls = GEOSGeometry("LINESTRING M (0 1 2, 3 4 5)")
        coord_seq = ls.coord_seq
        self.assertEqual(coord_seq.getM(0), 2.0)
        self.assertEqual(coord_seq.getM(1), 5.0)

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_setM(self):
        ls = GEOSGeometry("LINESTRING M (0 1 2, 3 4 5)")
        coord_seq = ls._cs
        coord_seq.setM(0, 10.0)
        self.assertEqual(coord_seq.getM(0), 10.0)

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_setitem_m(self):
        ls = GEOSGeometry("LINESTRING M (0 1 2, 3 4 5)")
        ls._cs[0] = (10.0, 11.0, 12.0)
        self.assertEqual(ls._cs[0], (10.0, 11.0, 12.0))

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_setitem_zm(self):
        ls = GEOSGeometry("LINESTRING ZM (0 1 2 3, 4 5 6 7)")
        ls._cs[0] = (10.0, 11.0, 12.0, 13.0)
        self.assertEqual(ls._cs[0], (10.0, 11.0, 12.0, 13.0))

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_clone_m(self):
        ls = GEOSGeometry("LINESTRING M (0 1 2, 3 4 5)")
        cloned = ls._cs.clone()
        self.assertTrue(cloned.hasm)
        self.assertFalse(cloned.hasz)
        self.assertEqual(cloned[0], (0.0, 1.0, 2.0))

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_clone_zm(self):
        ls = GEOSGeometry("LINESTRING ZM (0 1 2 3, 4 5 6 7)")
        cloned = ls._cs.clone()
        self.assertTrue(cloned.hasm)
        self.assertTrue(cloned.hasz)
        self.assertEqual(cloned[0], (0.0, 1.0, 2.0, 3.0))

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_kml_m(self):
        ls = GEOSGeometry("LINESTRING M (0 1 2, 3 4 5)")
        # KML doesn't support M, so M values should be excluded.
        self.assertEqual(ls.coord_seq.kml, "<coordinates>0.0,1.0,0 3.0,4.0,0</coordinates>")

    @skipIf(geos_version_tuple() < (3, 12), "GEOS >= 3.12.0 is required")
    def test_kml_zm(self):
        ls = GEOSGeometry("LINESTRING ZM (0 1 2 3, 4 5 6 7)")
        # KML doesn't support M, so M values should be excluded.
        self.assertEqual(
            ls.coord_seq.kml, "<coordinates>0.0,1.0,2.0 4.0,5.0,6.0</coordinates>"
        )

    def test_checkdim(self):
        coord_seq = LineString([(0, 0), (1, 1)]).coord_seq
        from django.contrib.gis.geos.error import GEOSException

        for dim in (-1, 4):
            with self.subTest(dim=dim):
                with self.assertRaises(GEOSException):
                    coord_seq.getOrdinate(dim, 0)
