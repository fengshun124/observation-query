import argparse

from tap_service import *

parser = argparse.ArgumentParser()
parser.description = 'input st date and query mode'
parser.add_argument('-n', '--name', type=str, dest='name',
                    help='target cluster name')
parser.add_argument('-r', '--radius', type=int, dest='radius', default=100,
                    help='radius of the spherical selection area')
args = parser.parse_args()

export_dir = 'src_data/'


# TODO query star info from known catalogue or SIMBAD
def get_target_params() -> [ClusterCoord, int]:
    return ClusterCoord(parallax=5.718,
                        longitude=147.3566,
                        latitude=-06.4040,
                        # ra=51.6167,
                        # dec=48.9750,
                        cluster_name='Pleiades'), args.radius


if __name__ == "__main__":
    target, selection_radius = get_target_params()
    target.get_cartesian_coord()

    # info
    print(f'filtering cluster {target.name} with '
          f'spherical radius {selection_radius} pc...')
    target.info()
    print('the cartesian coordinate of the cluster centre is')
    print(target.get_cartesian_coord())

    print('querying for Gaia DR3...', end='\r')
    obs_table = query_gaia_dr3(x_coord=target.galactic_x.value,
                               y_coord=target.galactic_y.value,
                               z_coord=target.galactic_z.value)
    # save file
    print('saving query result of Gaia DR3...', end='\r')
    obs_table.write(export_dir + f'{target.name}_{selection_radius}.fits', overwrite=True)
    print(f'Gaia DR3 of {target.name} data saved')

    print('querying for Gaia EDR3 mock...')
    mock_table = query_gaia_edr3_mock(x_coord=target.galactic_x.value,
                                      y_coord=target.galactic_y.value,
                                      z_coord=target.galactic_z.value)
    print('saving query result of Gaia EDR3 mock...', end='\r')
    mock_table.write(export_dir + f'{target.name}_mock_{selection_radius}.fits', overwrite=True)
    print(f'Gaia EDR3 mock of {target.name} data saved')
