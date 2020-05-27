# /usr/bin/env python
from astropy.io import fits
import pandas as pd
import numpy as np
import os, sys
import argparse as ap

# For SE catalogs
cat_cols = ['FLUX_AUTO', 'FLUXERR_AUTO', 'X_WORLD', 'Y_WORLD', 'XWIN_IMAGE', 'YWIN_IMAGE', 'ERRAWIN_IMAGE',
            'ERRBWIN_IMAGE', 'ERRTHETAWIN_IMAGE', 'FLAGS', 'FLAGS_WEIGHT', 'FWHM_IMAGE', 'FLUX_RADIUS',
            'MAG_AUTO', 'MAGERR_AUTO', 'A_IMAGE', 'B_IMAGE','THETA_IMAGE', 'ERRAWIN_IMAGE', 'ERRBWIN_IMAGE',
            'ERRTHETAWIN_IMAGE']



def makecatalog(rootdir, cat_type):
    for root, dirs, _ in os.walk(rootdir):
        for d in dirs:
            df_all = pd.DataFrame()
            for a, b, files in os.walk(os.path.join(root, d)):
                ccd = d.split('CCD')[-1]
                if cat_type == 'diff_se':
                    target_files = [f for f in files if f[-10:] == 'diff.1.cat' and f[:3] ==  'c4d']
                elif cat_type == 'se':
                    target_files = [f for f in files if f[-4:] == '.cat' and 'diff' not in f and 'coadd' not in f and f[:3] == 'c4d']
                elif cat_type == 'coadd':
                    target_files = [f for f in files if f == 'coadd.cat']
                else:
                    print('Catalog type {} not recognized'.format(cat_type))    # this should never happen
                for f in target_files:
                    file_base = f.split('_CCD')[0]
                    try:
                        expnum = int(file_base[-6:])
                    except ValueError:
                        print('Unable to extract exposure number for file {}'.format(f))
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
                        if 'se' in cat_type:
                            df_cat['EXPNUM'] = expnum
                        df_cat['CCD'] = ccd
                        df_cat.rename(columns={'X_WORLD': 'RA', 'Y_WORLD': 'DEC'}, errors='raise', inplace=True)
                        #                        fout = os.path.join(root,file_base)+'_{}_{}.csv'.format(expnum,ccd)
                        #                        print(fout)
                        df_all = pd.concat([df_all, df_cat])
            bigoutfile = os.path.join(root, '{}_{}.csv'.format(cat_type, d))
            df_all.to_csv(bigoutfile, index=None)
            print('Writing {} objects to file {}'.format(len(df_all), bigoutfile))

def main():
    parser = ap.ArgumentParser(description='Configure DEEP Catalog construction')
    parser.add_argument('-r','--rootdir', required=True, help="Root directory with CCD* directories")
    parser.add_argument('-c','--ccd', default=None, help="Specify a single CCD number")
    parser.add_argument('-t','--type', required=True, default='diff_se', choices=['diff_se','coadd', 'se'], help="Catalog type: single-epoch DiffImg, Coadd, single-epoch")
    opts = parser.parse_args()
    rootdir = opts.rootdir
    cat_type = opts.type.lower()
    if os.path.isdir(rootdir) is False:
        raise OSError(rootdir, "does not exist")
    makecatalog(rootdir, cat_type)
    print('Done!')

if __name__ == '__main__':
    main()