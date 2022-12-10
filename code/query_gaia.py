import argparse

import astropy.table
import numpy as np

from tap_service import tap_query, ClusterCoord

parser = argparse.ArgumentParser()
parser.description = 'input st date and query mode'
parser.add_argument('-n', '--name', type=str, dest='name', default='target',
                    help='target cluster name')
parser.add_argument('-r', '--radius', type=int, dest='radius', default=100,
                    help='radius of the spherical selection area')
# distance
parser.add_argument('-d', '--dist', type=float, dest='dist', default=None,
                    help='distance to the target centre')
parser.add_argument('-plx', '--parallax', type=float, dest='plx', default=None,
                    help='parallax of the target centre')
# galactic
parser.add_argument('-l', '--longitude', type=float, dest='l', default=None,
                    help='longitude of the target centre (galactic)')
parser.add_argument('-b', '--latitude', type=float, dest='b', default=None,
                    help='latitude of the target centre (galactic)')
# ICRS
parser.add_argument('-ra', '--ra', type=float, dest='ra', default=None,
                    help='right ascension of the target centre (ICRS)')
parser.add_argument('-dec', '--dec', type=float, dest='dec', default=None,
                    help='declination of the target centre (ICRS)')
# Cartesian
parser.add_argument('-x', '--galactic_x', type=float, dest='x', default=None,
                    help='x component of the Cartesian coordinate of the target centre')
parser.add_argument('-y', '--galactic_y', type=float, dest='y', default=None,
                    help='y component of the Cartesian coordinate of the target centre')
parser.add_argument('-z', '--galactic_z', type=float, dest='z', default=None,
                    help='z component of the Cartesian coordinate of the target centre')
# flag
parser.add_argument('-s', '--strict_mode', type=bool, dest='strict', default=True,
                    help='whether to end the process if abnormal occurs, default TRUE')
args = parser.parse_args()

export_dir = 'src_data/'


# TODO query star info from known catalogue or SIMBAD
def get_target_params() -> [float, float, float, float, str]:
    target_centre = ClusterCoord(longitude=args.l,
                                 latitude=args.b,
                                 distance=args.dist,
                                 parallax=args.plx,
                                 ra=args.ra,
                                 dec=args.dec,
                                 cluster_name=args.name)
    target_x, target_y, target_z = target_centre.get_cartesian_coord()

    # the input coordinate is empty but the converted one is not
    if (args.x is None) or (args.y is None) or (args.z is None):
        if (target_x is not None) and (target_y is not None) and (target_z is not None):
            return target_x.value, target_y.value, target_z.value, args.radius, args.name
    # the converted coordinate is empty but the input one is not
    elif (target_x is None) or (target_y is None) or (target_z is None):
        if (args.x is not None) and (args.y is not None) and (args.z is not None):
            return args.x, args.y, args.z, args.radius, args.name
    # both coordinates are not empty and cross-matched
    if (args.x is not None) and (args.y is not None) and (args.z is not None):
        if (target_x is not None) and (target_y is not None) and (target_z is not None):
            if abs(target_x.value - args.x) < 10 ** -1:
                if abs(target_y.value - args.y) < 10 ** -1:
                    if abs(target_z.value - args.z) < 10 ** -1:
                        return args.x, args.y, args.z, args.radius, args.name
            # both coordinates are not empty but fail to cross-match
            elif args.strict:
                raise Exception('the converted cartesian coordinate '
                                f'({target_x.value}, {target_y.value}, {target_z.value}) '
                                'and the input cartesian coordinate'
                                f'({args.x}, {args.y}, {args.z}) differs.\n'
                                f'it is strongly suggested to check the data source.')
            else:
                print('the converted cartesian coordinate '
                      f'({target_x.value}, {target_y.value}, {target_z.value}) '
                      'and the input cartesian coordinate'
                      f'({args.x}, {args.y}, {args.z}) differs.\n'
                      f'it is strongly suggested to check the data source.')
                return args.x, args.y, args.z, args.radius, args.name
    # else
    raise Exception('fail to get the centre cartesian coordinate of the target region\n'
                    'it is advised to check the input data')


def fix_data_type(table: astropy.table.Table) -> astropy.table.Table:
    for col_name in table.colnames:
        if table[col_name].dtype == np.object_:
            if col_name == 'phot_variable_flag':
                src_col_data = table[col_name].data
                new_col = table.Column(src_col_data, dtype='bool')
                table.replace_column(col_name, new_col)
            else:
                src_col_data = table[col_name].data
                new_col = table.Column(src_col_data, dtype='str')
                table.replace_column(col_name, new_col)
        else:
            continue
    return table


if __name__ == "__main__":
    galactic_x, galactic_y, galactic_z, cut_radius, target_name = get_target_params()

    # info
    print(f'filtering cluster {target_name} with '
          f'spherical radius {cut_radius} pc...')
    print('the cartesian coordinate of the cluster centre is')
    print(f'({galactic_x}, {galactic_y}, {galactic_z})')

    print('querying for Gaia DR3...', end='\r')
    obs_table_src = tap_query(x_coord=galactic_x,
                              y_coord=galactic_y,
                              z_coord=galactic_z,
                              query_mode='obs')
    obs_table = fix_data_type(obs_table_src)
    print('saving query result of Gaia DR3...', end='\r')
    obs_table.write(export_dir + f'{target_name}_{cut_radius}.fits', overwrite=True)
    print(f'Gaia DR3 of {target_name} data saved')

    print('querying for Gaia EDR3 mock...')
    mock_table_src = tap_query(x_coord=galactic_x,
                               y_coord=galactic_y,
                               z_coord=galactic_z,
                               query_mode='mock')
    mock_table = fix_data_type(mock_table_src)
    print('saving query result of Gaia EDR3 mock...', end='\r')
    mock_table.write(export_dir + f'{target_name}_mock_{cut_radius}.fits', overwrite=True)
    print(f'Gaia EDR3 mock of {target_name} data saved')
