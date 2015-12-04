# Simple tests to make sure the classes are operating correctly

import os
import time

from gdalvalidator import WKTValidate, Proj4Validate, EPSGValidate


if __name__ == '__main__':
    base_path = os.path.dirname(os.path.realpath(__file__))
    test_path = os.path.join(base_path, 'test_lists')

    good_proj4 = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    bad_proj4 = '+proj=lnglat +ellps=WGS84 +datum=W84 +no_defs'
    good_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    bad_wkt = 'GEOGCS["",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    good_epsg = 4326
    bad_epsg = 9999

    t = time.time()
    count = 0
    for prod_file in os.listdir(test_path):
        with open(os.path.join(test_path, prod_file), 'r') as f:
            for line in f:
                sceneid = line.strip()
                print '\n' + sceneid

                if EPSGValidate(2096, sceneid):
                    print 'good'
                else:
                    print 'bad'
                count += 1

    print time.time() - t, count
