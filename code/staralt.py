import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from pathlib import Path


def getSTARALT(check_mode='1',
               target_name: str = None,
               target_ra: str = None,
               target_dec: str = None,
               target_list: str = None,
               obs_year: str = '2023',
               obs_month: str = '04', obs_date: str = '15',
               observatory_name='Mauna Kea Observatory (Hawaii, USA)',
               export_dir='../output/',
               export_file_name='response.gif') -> None:
    if (target_name is None) and (target_list is None):
        raise Exception('target and target list cannot be None in the same time!')

    target = '{} {} {}'.format(target_name, target_ra, target_dec)

    encoded_data = MultipartEncoder(
        fields={
            'action': 'showImage',
            # mode
            'form[mode]': check_mode,
            # observation date
            'form[year]': obs_year,
            'form[month]': obs_month,
            'form[day]': obs_date,
            # observatory
            'form[obs_name]': observatory_name,
            # coordinates
            'form[coordlist]': target,
            # 'form[coordlist]': 'T 34.2 52.2\nA 23.3 -46.4',
            'Content-Type': 'application/octet-stream',
            'coordfile': (
                '', target_list, 'application/octet-stream'),
            # other options
            'form[paramdist]': '2',
            'form[minangle]': '10',
            'form[format]': 'gif',
        },
        boundary='----WebKitFormBoundarywZnma1H8zs5PTGLW'
    )

    headers = {
        'Host': 'catserver.ing.iac.es',
        # 'Content-Length': '1446',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'http://catserver.ing.iac.es',
        'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundarywZnma1H8zs5PTGLW',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.5195.102 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                  'image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://catserver.ing.iac.es/staralt/',
        # 'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'close',
    }

    response = requests.post('http://catserver.ing.iac.es/staralt/index.php',
                             headers=headers, data=encoded_data, verify=False)
    Path(export_dir).mkdir(parents=True, exist_ok=True)
    with open(export_dir + export_file_name, 'wb') as file:
        file.write(response.content)
