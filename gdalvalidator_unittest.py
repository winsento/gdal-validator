import unittest

from gdalvalidator import WKTValidate, Proj4Validate, EPSGValidate


class ValidatorTestCase(unittest.TestCase):
    good_proj4 = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    bad_proj4 = '+proj=lnglat +ellps=WGS84 +datum=W84 +no_defs'
    good_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    bad_wkt = 'GEOGCS["",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    good_epsg = 4326
    bad_epsg = 9999

    def test_proj4validate(self):
        self.assertTrue(Proj4Validate(self.good_proj4))
        self.assertFalse(Proj4Validate(self.bad_proj4))

    def test_wktvalidate(self):
        self.assertTrue(WKTValidate(self.good_wkt))
        self.assertFalse(WKTValidate(self.bad_wkt))

    def test_epsgvalidate(self):
        self.assertTrue(EPSGValidate(self.good_epsg))
        self.assertFalse(EPSGValidate(self.bad_epsg))

if __name__ == '__main__':
    unittest.main()
