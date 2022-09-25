import pandas as pd
import requests.exceptions
from astropy.table import Table
import cfht

# read specific cluster
ComaBer = Table.read('../data/Teff fixed/Coma_Berenices filtered.fits', format='fits')
GroupX = Table.read('../data/Teff fixed/Group_X filtered.fits', format='fits')
LP2442 = Table.read('../data/Teff fixed/LP_2442 filtered.fits', format='fits')


def fetchExpTime(cluster, cluster_name,
                 target_snr, target_seeing, target_h2o, target_airmass):
    list_name = [cluster_name] * len(cluster)
    list_snr = [target_snr] * len(cluster)
    list_seeing = [target_seeing] * len(cluster)
    list_h2o = [target_h2o] * len(cluster)
    list_airmass = [target_airmass] * len(cluster)
    list_texp = []

    for idx in range(len(cluster)):
        print(cluster_name, cluster['source_id'][idx])
        try:
            list_texp.append(cfht.requestCFHTExposureTime(t_eff=cluster['Teff'][idx],
                                                          snr_pixel=target_snr,
                                                          h_mag=cluster['Hmag'][idx],
                                                          seeing=target_seeing,
                                                          h2o=target_h2o,
                                                          air_mass=target_airmass,
                                                          is_export=True,
                                                          export_dir='../output/CFHT/{} SNR{}/'.format(
                                                              cluster_name, target_snr),
                                                          export_file_name='{} t-exp_output.txt'.format(
                                                              cluster['source_id'][idx])))
        except requests.exceptions.ReadTimeout:
            print('CFHT seems not responding... skipping this star...')
            list_texp.append('Failed to Fetch! Perform Manual Request!')
    info = pd.DataFrame(data={'cluster_name': list_name,
                              'star_gaia_id': cluster['source_id'],
                              'star_Hmag': cluster['Hmag'],
                              'star_Teff': cluster['Teff'],
                              'target_signal_noise_ratio': list_snr,
                              'target_seeing': list_seeing,
                              'target_h2o': list_h2o,
                              'target_airmass': list_airmass,
                              'exposure_time': list_texp
                              })
    info.to_csv('../output/CFHT/{} SNR{} summary.csv'.format(cluster_name,
                                                             target_snr),
                index=False)


# SN=100 and 50; seeing =1.0, h2o=1.6; airmass=1.0(coma), airmass=1.5 (group X)

fetchExpTime(cluster=GroupX,
             cluster_name='Group_X',
             target_snr=100,
             target_seeing=1.0,
             target_h2o=1.6,
             target_airmass=1.5)

fetchExpTime(cluster=GroupX,
             cluster_name='Group_X',
             target_snr=50,
             target_seeing=1.0,
             target_h2o=1.6,
             target_airmass=1.5)

fetchExpTime(cluster=ComaBer,
             cluster_name='Coma_Berenices',
             target_snr=100,
             target_seeing=1.0,
             target_h2o=1.6,
             target_airmass=1.0)

fetchExpTime(cluster=ComaBer,
             cluster_name='Coma_Berenices',
             target_snr=50,
             target_seeing=1.0,
             target_h2o=1.6,
             target_airmass=1.0)
