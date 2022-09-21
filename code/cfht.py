from pathlib import Path

import requests
import re


# CALCOPT=0 / compute SNR
# CALCOPT=1 / compute e-time


def requestCFHTExposureTime(calc_option: int = 1,
                            t_eff: float = 3200,
                            snr_pixel: float = 100.0,
                            h_mag: float = 7.0,
                            seeing: float = 1.,
                            h2o: float = 1.6,
                            air_mass: float = 1.0,
                            # detailed_info: bool = False,
                            is_export: bool = False,
                            export_dir: str = '../output/',
                            export_file_name: str = 't-exp_output.txt') -> str:
    request_head = 'https://etc.cfht.hawaii.edu/cgi-bin/spi/etc.pl?'
    # if detailed_info:
    request_end = 'DETAILS=1'
    # else:
    #     request_end = 'DETAILS=0'
    if (seeing > 5.) or (seeing < 0.1):
        raise Exception('\'{}\' is not a valid value for seeing, which lies between 0.1 and 5'.format(seeing))

    param_calcopt = 'CALCOPT={}&'.format(calc_option)
    param_snr_pixel = 'SNR={}&'.format(snr_pixel)
    param_t_eff = 'TMP={}&'.format(t_eff)
    param_h_mag = 'MAG={}&'.format(h_mag)
    param_h2o = 'H2O={}&'.format(h2o)
    param_see = 'SEE={}&'.format(seeing)
    param_air_mass = 'AIRMASS={}&'.format(air_mass)

    # unknown params
    param_dist = 'DIST=27&'
    param_rstar = 'RSTAR=0.15&'

    # not applicable params
    param_exp_time = 'TEXP=0&'

    request_content = request_head + param_calcopt + param_exp_time
    request_content += param_snr_pixel + param_h_mag + param_t_eff
    request_content += param_see + param_rstar + param_dist
    request_content += param_h2o + param_air_mass + request_end

    response = requests.get(request_content)

    if is_export:
        Path(export_dir).mkdir(parents=True, exist_ok=True)
        with open(export_dir + export_file_name, 'wb') as file:
            file.write(response.content)

    exposure_time = re.search(r"(?<=texp=)[-+]?[0-9]*\.?[0-9]+s",
                              response.text)[0]
    # encounter unexpected response
    if exposure_time is None:
        Path('../error/').mkdir(parents=True, exist_ok=True)
        with open('../error/error_output.txt', 'wb') as file:
            file.write(response.content)

    return str(exposure_time)


# not ready!!
def requestCFHTSignalNoiseRatio(calc_option: int = 1,
                                t_eff: float = 3200,
                                exposure_time: float = 1800,
                                h_mag: float = 7.0,
                                seeing: float = 1.,
                                h2o: float = 1.6,
                                air_mass: float = 1.0,
                                is_export: bool = False,
                                export_dir: str = '../output/',
                                export_file_name: str = 'snr_output.txt') -> str:
    request_head = 'https://etc.cfht.hawaii.edu/cgi-bin/spi/etc.pl?'
    request_end = 'DETAILS=1'

    # validation
    if (seeing > 5.) or (seeing < 0.1):
        raise Exception('\'{}\' is not a valid value for seeing, which lies between 0.1 and 5'.format(seeing))

    param_calcopt = 'CALCOPT={}&'.format(calc_option)
    param_exp_time = 'TEXP={}&'.format(exposure_time)
    param_t_eff = 'TMP={}&'.format(t_eff)
    param_h_mag = 'MAG={}&'.format(h_mag)
    param_h2o = 'H2O={}&'.format(h2o)
    param_see = 'SEE={}&'.format(seeing)
    param_air_mass = 'AIRMASS={}&'.format(air_mass)

    # unknown params
    param_dist = 'DIST=27&'
    param_rstar = 'RSTAR=0.15&'

    # not applicable params
    param_snr_pixel = 'SNR=0&'

    request_content = request_head + param_calcopt + param_exp_time
    request_content += param_snr_pixel + param_h_mag + param_t_eff
    request_content += param_see + param_rstar + param_dist
    request_content += param_h2o + param_air_mass + request_end

    response = requests.get(request_content)

    if is_export:
        Path(export_dir).mkdir(parents=True, exist_ok=True)
        with open(export_dir + export_file_name, 'wb') as file:
            file.write(response.content)

    signal_noise_ratio = re.search(r"(?<=texp=)[-+]?[0-9]*\.?[0-9]+s",
                                   response.text)[0]

    # encounter unexpected response
    if signal_noise_ratio is None:
        Path('../error/').mkdir(parents=True, exist_ok=True)
        with open('../error/error_output.txt', 'wb') as file:
            file.write(response.content)

    return str(signal_noise_ratio)
