import pyvo
from astropy import units
from astropy.coordinates import Distance, SkyCoord
from astropy.table import Table


class ClusterCoord:
    def __init__(self,
                 parallax: float | units.quantity.Quantity = None,
                 longitude: float | units.quantity.Quantity = None,
                 latitude: float | units.quantity.Quantity = None,
                 ra: float | units.quantity.Quantity = None,
                 dec: float | units.quantity.Quantity = None,
                 distance: float | units.quantity.Quantity = None,
                 strict_mode: bool = True,
                 cluster_name: str = None):
        # initialize
        self.plx = self.__unit_check(parallax, units.mas)
        self.long = self.__unit_check(longitude, units.deg)
        self.lat = self.__unit_check(latitude, units.deg)
        self.ra = self.__unit_check(ra, units.deg)
        self.dec = self.__unit_check(dec, units.deg)
        self.dist = self.__unit_check(distance, units.pc)
        self.strict_mode = strict_mode
        self.name = cluster_name
        # flag
        self.converted_dist: bool = False
        self.converted_plx: bool = False
        # Cartesian coords
        self.galactic_x: units.quantity.Quantity | None = None
        self.galactic_y: units.quantity.Quantity | None = None
        self.galactic_z: units.quantity.Quantity | None = None

        # verify distance
        if (self.dist is not None) and (self.plx is not None):
            if abs(Distance(parallax=self.plx).value - self.dist.value) > 10 ** -5:
                self.__exception_handling(f'Input distance \'{self.dist}\' does not match the '
                                          f'converted distance \'{Distance(parallax=self.plx)}\'.\n'
                                          'It is strongly recommended to check the input data.')
        # fill values
        elif (self.dist is not None) and (self.plx is None):
            self.plx = (1000 / self.dist.value) * units.mas
        elif (self.plx is not None) and (self.dist is None):
            self.dist = Distance(parallax=self.plx)

    def info(self):
        attrs = vars(self)
        print('{:*^30}'.format(f' {self.name} '))
        for item in attrs.items():
            if item[1] is None:
                continue
            if item[0] in ['converted_dist', 'converted_plx', 'strict_mode', 'name',
                           'galactic_x', 'galactic_y', 'galactic_z']:
                continue
            elif item[0] == 'plx':
                if self.converted_plx:
                    print('{:<14}{:<12.5f}'.format('*cnvrt. plx', self.plx))
                else:
                    print('{:<14}{:<12.5f}'.format(item[0], item[1]))
            elif item[0] == 'dist':
                if self.converted_dist:
                    print('{:<14}{:<12.5f}'.format('*cnvrt. dist', self.plx))
                else:
                    print('{:<14}{:<12.5f}'.format(item[0], item[1]))
            else:
                print('{:<14}{:<12.5f}'.format(item[0], item[1]))
        print('{:*^30}'.format(''))

    def get_cartesian_coord(self):
        galactic_coord_icrs = None
        galactic_coord_galactic = None
        try:
            if (self.dist is not None) and (self.ra is not None) and (self.dec is not None):
                galactic_coord_icrs = SkyCoord(ra=self.ra, dec=self.dec, distance=self.dist,
                                               frame='icrs').galactic

            if (self.plx is not None) and (self.long is not None) and (self.lat is not None):
                galactic_coord_galactic = SkyCoord(l=self.long, b=self.lat, distance=self.dist,
                                                   frame='galactic')

            # cross ref and return value
            if (galactic_coord_icrs is not None) and (galactic_coord_galactic is not None):
                if abs(galactic_coord_icrs.cartesian.x.value - galactic_coord_galactic.cartesian.x.value) < 0.1:
                    if abs(galactic_coord_icrs.cartesian.y.value - galactic_coord_galactic.cartesian.y.value) < 0.1:
                        if abs(galactic_coord_icrs.cartesian.z.value - galactic_coord_galactic.cartesian.z.value) < 0.1:
                            self.galactic_x = self.__compute_average(galactic_coord_icrs.cartesian.x,
                                                                     galactic_coord_galactic.cartesian.x)
                            self.galactic_y = self.__compute_average(galactic_coord_icrs.cartesian.y,
                                                                     galactic_coord_galactic.cartesian.y)
                            self.galactic_z = self.__compute_average(galactic_coord_icrs.cartesian.z,
                                                                     galactic_coord_galactic.cartesian.z)
                else:
                    self.__exception_handling(f'Conversion from from \'{galactic_coord_icrs}\' '
                                              f'and \'{galactic_coord_galactic}\' differs.\n'
                                              'It is strongly recommended to check the data')

            elif galactic_coord_icrs is not None:
                self.galactic_x = galactic_coord_icrs.cartesian.x
                self.galactic_y = galactic_coord_icrs.cartesian.y
                self.galactic_z = galactic_coord_icrs.cartesian.z
            elif galactic_coord_galactic is not None:
                self.galactic_x = galactic_coord_galactic.cartesian.x
                self.galactic_y = galactic_coord_galactic.cartesian.y
                self.galactic_z = galactic_coord_galactic.cartesian.z

            return self.galactic_x, self.galactic_y, self.galactic_z

        except AttributeError:
            self.__exception_handling('Unable to perform coordinate conversion with limited parameters.\n'
                                      # 'either ra.,dec. and long., lat. or either dist. and plx. are empty value.\n'
                                      'Check the availability of value by ClusterCoord.info()')

    @staticmethod
    def __unit_check(param: float | units.quantity.Quantity,
                     unit_type: units.core.Unit):
        if param is None:
            return None
        elif type(param) == units.quantity.Quantity:
            if param.unit == unit_type:
                return param
            else:
                return param.value * unit_type
        else:
            return param * unit_type

    @staticmethod
    def __compute_average(value_a: units.quantity.Quantity,
                          value_b: units.quantity.Quantity):
        if value_a.unit != value_b.unit:
            raise Exception(f'unit \'{value_a.unit}\' and \'{value_b.unit}\' do not match!')

        return ((value_a.value + value_b.value) / 2) * value_a.unit

    def __exception_handling(self, warning_text):
        if self.strict_mode:
            raise Exception(warning_text)
        else:
            print(warning_text)


def query_gaia_dr3(x_coord: float, y_coord: float, z_coord: float,
                   selection_radius: float = 100, maxrec: int = 10000000,
                   tap_host: str = 'https://gea.esac.esa.int/tap-server/tap'):
    # construct Gaia DR3 query
    obs_query = 'SELECT *,'
    obs_query += '1000/g.parallax*cos(g.b*3.1415/180)*cos(g.l*3.1415/180) as X,'
    obs_query += '1000/g.parallax*cos(g.b*3.1415/180)*sin(g.l*3.1415/180) as Y,'
    obs_query += '1000/g.parallax*sin(g.b*3.1415/180) as Z '
    obs_query += 'FROM gaiadr3.gaia_source as g '
    obs_query += 'WHERE (g.parallax_over_error > 10) AND (g.astrometric_excess_noise < 1) AND '
    obs_query += f'(sqrt(power((1000/g.parallax*cos(g.b*3.1415/180) * cos(g.l*3.1415/180) - ({x_coord})),2) + '
    obs_query += f'power((1000/g.parallax*cos(g.b*3.1415/180) * sin(g.l*3.1415/180) - ({y_coord})),2) + '
    obs_query += f'power((1000/g.parallax*sin(g.b*3.1415/180) - ({z_coord})),2)) < {selection_radius})'

    obs_service = pyvo.dal.TAPService(tap_host)
    obs_result = obs_service.run_async(obs_query, maxrec=maxrec)

    # clear abnormal column 'phot_variable_flag'
    # change variable type 'object' to 'bool'
    src_col_data = obs_result['phot_variable_flag'].data
    new_col = Table.Column(src_col_data, dtype='bool')
    obs_result.replace_column('phot_variable_flag', new_col)

    return obs_result.to_table()


def query_gaia_edr3_mock(x_coord: float, y_coord: float, z_coord: float,
                         selection_radius: float = 100, maxrex: int = 16000000,
                         tap_host: str = 'http://dc.zah.uni-heidelberg.de/__system__/tap/run/tap'):
    # construct mock field query
    mock_query = 'SELECT * '
    mock_query += 'FROM gedr3mock.main as g '
    mock_query += 'WHERE (g.parallax/g.parallax_error > 10) AND (g.popid!=11) AND '
    mock_query += f'(sqrt(power((1000/g.parallax*cos(g.b*3.1415/180) * cos(g.l*3.1415/180) - ({x_coord})),2) + '
    mock_query += f'power((1000/g.parallax*cos(g.b*3.1415/180) * sin(g.l*3.1415/180) - ({y_coord})),2) + '
    mock_query += f'power((1000/g.parallax*sin(g.b*3.1415/180) - ({z_coord})),2)) < {selection_radius})'

    mock_service = pyvo.dal.TAPService(tap_host)
    mock_result = mock_service.run_async(mock_query, maxrec=maxrex)

    # clear abnormal column 'phot_variable_flag'
    # change variable type 'object' to 'bool'
    src_col_data = mock_result['phot_variable_flag'].data
    new_col = Table.Column(src_col_data, dtype='bool')
    mock_result.replace_column('phot_variable_flag', new_col)

    return mock_result.to_table()
