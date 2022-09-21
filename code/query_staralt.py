import argparse
from typing import Any

from astropy.io import ascii

import staralt

parser = argparse.ArgumentParser()
parser.description = 'input target date and query mode'
parser.add_argument('-dd', '--day', type=int, dest='day',
                    help='query date in format of xx, applicable with \'staralt\' and \'startrack\' only')
parser.add_argument('-mm', '--month', type=int, dest='month',
                    help='query month in format of xx, applicable with \'staralt\' and \'startrack\' only')
parser.add_argument('-yy', '-year', type=int, dest='year',
                    help='query year in format of xxxx, applicable with \'staralt\' and \'startrack\' only')
parser.add_argument('-m', '--mode', type=str, dest='mode',
                    help='query mode, staralt / startrack / starobs / starmult')
args = parser.parse_args()

dict_mode = {'staralt': '1',
             'startrack': '2',
             'starobs': '3',
             'starmult': '4'}


def getQueryParams() -> tuple[str, str, str, str | None | Any]:
    # year
    if args.year is None:
        print('intput query year for \'staralt\' and \'startrack\':')
        query_year = int(input())
    else:
        query_year = args.year
    # validation
    if query_year not in range(1985, 2030):
        raise Exception('\'{}\' is not a valid year'.format(query_year))
    else:
        query_year = str(query_year)

    # month
    if args.month is None:
        print('intput query month for \'staralt\' and \'startrack\':')
        query_month = int(input())
    else:
        query_month = args.month
    # validation
    if query_month not in range(1, 13):
        raise Exception('\'{}\' is not a valid month'.format(query_month))
    else:
        query_month = str(query_month).zfill(2)

    # day
    if args.day is None:
        print('intput query day for \'staralt\' and \'startrack\':')
        query_day = int(input())
    else:
        query_day = args.day
    # validation
    if query_day not in range(1, 32):
        raise Exception('\'{}\' is not a valid day'.format(query_day))
    else:
        query_day = str(query_day).zfill(2)

    # mode
    query_mode = None
    if args.mode not in ['staralt', 'startrack', 'starobs', 'starmult', None]:
        print('\'{}\' does not match to any known mode...\n'
              'Avaliable modes are \'staralt\', \'startrack\', \'starobs\' and \'starmult\''.format(args.mode))
    elif args.mode is None:
        print('intput query mode:')
        query_mode = str(input())
        if query_mode == '':
            print('No mode specified...using default mode \'staralt\'')
            query_mode = 'staralt'
    else:
        query_mode = args.mode

    return query_year, query_month, query_day, query_mode


if __name__ == "__main__":
    yy, mm, dd, mode = getQueryParams()

    date = yy + mm + dd
    if mode in ['staralt', 'startrack']:
        print('query date - {}\nquery mode - {}'.format(date, mode))
    elif mode in ['starobs', 'starmult']:
        print('query mode - {}'.format(mode))

    star_catalog = ascii.read('../data/oc_85_summary.csv')
    print('start querying STARALT...')
    print('cluster_name -  median_ra - median_dec')

    for idx in range(len(star_catalog)):
        cluster_name = star_catalog['cluster_name'][idx].replace('_', '')
        cluster_name = cluster_name.replace('gp', 'GP').replace('isl', 'ISL')
        median_ra = star_catalog['median_ra'][idx]
        median_dec = star_catalog['median_dec'][idx]

        print(cluster_name, median_ra, median_dec)

        if mode in ['staralt', 'startrack']:
            exp_dir = '../output/overall {}/{}/'.format(mode, date)
            exp_filename = '{}_{}_{}.gif'.format(mode, cluster_name, date)
        elif mode in ['starobs', 'starmult']:
            exp_dir = '../output/overall {}/'.format(mode)
            exp_filename = '{}_{}.gif'.format(mode, cluster_name)
        else:
            raise Exception('\'{}\' is not match to any known mode!'.format(mode))

        staralt.requestSTARALT(check_mode=str(dict_mode[mode]),
                               target_name=cluster_name,
                               target_ra=median_ra,
                               target_dec=median_dec,
                               obs_year=yy,
                               obs_month=mm,
                               obs_date=dd,
                               export_dir=exp_dir,
                               export_file_name=exp_filename)

    print('query complete!')
    if mode in ['staralt', 'startrack']:
        print('figs have been exported to \'../output/overall {}/{}/\''.format(mode, date))
    else:
        print('figs have been exported to \'../output/overall {}/\''.format(mode))
