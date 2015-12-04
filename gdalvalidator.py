import os
import sqlite3

from osgeo import osr


class ValidationException(Exception):
    pass


class GDALValidator(osr.SpatialReference):
    """
    Used for validating a spatial reference against GDAL's library
    to make sure it is compatible

    Currently only supports Landsat based scene id's
    Will revisit to support other sensor types
    """
    # TODO All prints really should be routed to a logger or warnings

    # Deprecated, here just in case
    POLAR_WKT = 'PROJCS["WGS 84 / Antarctic Polar Stereographic",GEOGCS["WGS 84",\
    DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]]\
    ,AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],\
    UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]\
    ,UNIT["metre",1,AUTHORITY["EPSG","9001"]],PROJECTION["Polar_Stereographic"],\
    PARAMETER["latitude_of_origin",-71],PARAMETER["central_meridian",0],\
    PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],\
    AUTHORITY["EPSG","3031"],AXIS["Easting",UNKNOWN],AXIS["Northing",UNKNOWN]]'

    def __init__(self, sceneid=''):
        super(GDALValidator, self).__init__()

        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.sql_db = os.path.join(self.base_path, 'conversion-table.db')

        if not os.path.exists(self.sql_db) and sceneid:
            print('Database not found, unable to verify scene location')
            sceneid = ''

        self.sceneid = sceneid
        self.sceneproj = osr.SpatialReference()
        self.path = ''
        self.row = ''
        self.zone = 0
        self.valid = False
        self.err_num = 5
        self.err_msg = self.ogrerr_msg(self.err_num)

        if sceneid:
            self.build_sceneinfo()

    def __nonzero__(self):
        return self.valid

    def build_sceneinfo(self):
        self.set_pathrow()
        self.check_db()
        self.set_sceneproj()

    def check_db(self):
        """
        Check the database to get the LPGS UTM (or polar) projection it should
        fall in
        """
        conn = sqlite3.connect(self.sql_db)
        cur = conn.cursor()

        try:
            cur.execute('SELECT zone FROM conversion WHERE path = ? AND row = ?', (self.path, self.row))
            self.zone = cur.fetchone()
        except Exception as e:
            raise ValidationException(e)

        conn.close()

    def check_transform(self):
        """
        Checks to see if the a coordinate transformation object can
        be created between the two projections

        :return: pass or fail bool
        """

        try:
            _ = osr.CoordinateTransformation(self.sceneproj, self)
            _.TransformPoint(1, 1)
            _ = osr.CoordinateTransformation(self, self.sceneproj)
            _.TransformPoint(1, 1)
            return True
        except NotImplementedError:
            self.err_num = 5
            self.err_msg = self.ogrerr_msg(self.err_num)
            return False

    def check_valid(self):
        self.err_num = self.Validate()
        self.err_msg = self.ogrerr_msg(self.err_num)

        if not self.sceneid:
            if not self.err_num and self.ExportToWkt():
                self.valid = True
                print('Scene ID not provided or database not found, appears OK')
        else:
            if not self.err_num and self.check_transform():
                self.valid = True

    @staticmethod
    def ogrerr_msg(num):
        """
        Pair OGRERR code with the message defined in the
        GDAL source code, made static for portability

        When validating projection information, usually the only
        values that come up are 0, 5, or 7

        :param num: OGRERR/GDAL error code
        :type num: int
        :return: associated error message
        """
        err_msg = {1: 'OGRERR_NOT_ENOUGH_DATA',
                   2: 'OGRERR_NOT_ENOUGH_MEMORY',
                   3: 'OGRERR_UNSUPPORTED_GEOMETRY_TYPE',
                   4: 'OGRERR_UNSUPPORTED_OPERATION',
                   5: 'OGRERR_CORRUPT_DATA',
                   6: 'OGRERR_FAILURE',
                   7: 'OGRERR_UNSUPPORTED_SRS',
                   8: 'OGRERR_INVALID_HANDLE',
                   9: 'OGRERR_NON_EXISTING_FEATURE'}

        if num in err_msg.keys():
            return err_msg[num]
        else:
            return 'Unknown GDAL/OGR Error'

    def set_pathrow(self):
        """
        Build the path/row attributes from the Landsat scene id
        Must begin with an l/L
        """
        try:
            self.path = int(self.sceneid[3:6])
            self.row = int(self.sceneid[6:9])
        except ValueError:
            # raise ValidationException(e)
            print('Unable to parse scene id, defaulting to no scene id')
            self.sceneid = ''

    def set_sceneproj(self):
        """
        Set the spatial reference for the scene to be re-projected based on the
        LPGS UTM
        """
        utm_proj4 = '+proj=utm +zone={0} +datum=WGS84 +units=m +no_defs'.format(self.zone)
        if self.zone == 3031:
            self.sceneproj.ImportFromEPSG(3031)
        else:
            self.sceneproj.ImportFromProj4(utm_proj4)


class WKTValidate(GDALValidator):
    """
    GDALValidator subclass for checking well-known-texts
    """
    def __init__(self, wkt, sceneid=''):
        super(WKTValidate, self).__init__(sceneid=sceneid)

        try:
            self.ImportFromWkt(wkt)
        except TypeError as e:
            raise ValidationException(e)

        self.check_valid()


class Proj4Validate(GDALValidator):
    """
    GDALValidator subclass for checking proj4 strings
    """
    def __init__(self, proj4, sceneid=''):
        super(Proj4Validate, self).__init__(sceneid=sceneid)

        try:
            self.ImportFromProj4(proj4)
        except TypeError as e:
            raise ValidationException(e)

        self.check_valid()


class EPSGValidate(GDALValidator):
    """
    GDALValidator subclass for checking EPSG codes
    """
    def __init__(self, epsg, sceneid=''):
        super(EPSGValidate, self).__init__(sceneid=sceneid)

        try:
            self.ImportFromEPSG(epsg)
        except TypeError as e:
            raise ValidationException(e)

        self.check_valid()
