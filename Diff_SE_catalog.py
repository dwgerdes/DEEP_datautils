# /usr/bin/env python
from astropy.io import fits
import pandas as pd
import numpy as np
import os,

# For SE catalogs
cat_cols = ['FLUX_AUTO', 'FLUXERR_AUTO', 'X_WORLD', 'Y_WORLD', 'XWIN_IMAGE', 'YWIN_IMAGE', 'ERRAWIN_IMAGE',
            'ERRBWIN_IMAGE', 'ERRTHETAWIN_IMAGE', 'FLAGS', 'FLAGS_WEIGHT', 'FWHM_IMAGE', 'FLUX_RADIUS',
            'MAG_AUTO', 'MAGERR_AUTO', 'A_IMAGE', 'B_IMAGE','THETA_IMAGE', 'ERRAWIN_IMAGE', 'ERRBWIN_IMAGE',
            'ERRTHETAWIN_IMAGE']



def makecatalog(rootdir):
    for root, dirs, _ in os.walk(rootdir):
        for d in dirs:
            df_all = pd.DataFrame()
            for a, b, files in os.walk(os.path.join(root, d)):,
                ccd = d.split('CCD')[-1]
                for f in files:
                    if f[-4:] == '.cat' and f[-10:] == 'diff.1.cat' and 'coadd' not in f:
                        file_base = f.split('_CCD')[0]
                        expnum = int(file_base[-6:])
                        fitsfile = os.path.join(root, d, f)
                        print('Processing {}'.format(fitsfile))
                        with fits.open(os.path.join(root, d, f)) as hdu:
                            dat = hdu[1].data
                            try:
                                df_cat = pd.DataFrame(dat)
                                df_cat = df_cat[cat_cols]
                            except ValueError:
                                df_cat = pd.DataFrame(np.array(
                                    dat).byteswap().newbyteorder())  # fixes endian weirdness with Fits file on some linux machines
                                df_cat = df_cat[cat_cols]
                            df_cat['EXPNUM'] = expnum
                            df_cat['CCD'] = ccd
                            df_cat.rename(columns={'X_WORLD': 'RA', 'Y_WORLD': 'DEC'}, errors='raise', inplace=True)
                            #                        fout = os.path.join(root,file_base)+'_{}_{}.csv'.format(expnum,ccd)
                            #                        print(fout)
                            df_all = pd.concat([df_all, df_cat])
            bigoutfile = os.path.join(root, 'Diffcat_{}.csv'.format(d))
            df_all.to_csv(bigoutfile, index=None)
            print('Writing {} objects to file {}'.format(len(df_all), bigoutfile))

def main():
    rootdir = sys.argv[-1]
    makecatalog(rootdir)
    print('Done!')

if __name__ == '__main__':
    main()