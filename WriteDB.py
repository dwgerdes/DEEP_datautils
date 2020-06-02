import pandas as pd
import glob
import numpy as np
import easyaccess as ea
import argparse as ap
import os
import matplotlib.pyplot as plt

'''
Write catalog contents to the database
'''

def check_quality(file_list):

    for f in file_list:
        df = pd.read_csv(f)
        exps, counts = np.unique(df.EXPNUM.values, return_counts=True)
        print(counts)
        median = np.median(counts)
        std = np.std(counts)
        print("Median = {}, stddev = {}".format(median, std))
        for ind, exp in enumerate(exps):
            if counts[ind] > median + 3*std or counts[ind] < median - 3*std:
                print(f"Possible bad exposure: File = {f}, Expnum = {exp}, count = {counts[ind]}")

def writedb(file_list, table, dbname="umtno"):
    conn = ea.connect(section=dbname)
    for f in file_list:
        df = pd.read_csv(f)
        print("Writing {} objects from file {} to database table {}".format(len(df), f, table))
        conn.load_table(f, name=table)

def main():
    parser = ap.ArgumentParser(description='Write catalog to database')
    parser.add_argument('-r','--rootdir', required=True, help="Root directory with CCD* directories")
    parser.add_argument('-c','--ccd', default=None, help="Specify a single CCD number")
    parser.add_argument('-t','--type', required=True, default='diff_se', choices=['diff_se','coadd', 'se'], help="Catalog type: single-epoch DiffImg, Coadd, single-epoch")
    opts = parser.parse_args()
    rootdir = opts.rootdir
    cat_type = opts.type.lower()
    if os.path.isdir(rootdir) is False:
        raise OSError(rootdir, "does not exist")
    if cat_type == 'diff_se':
        filetype = 'diff_se_CCD*.csv'
        table = "DIFF_TEST"
        file_list = glob.glob(os.path.join(rootdir, filetype))
        writedb(file_list, table)
#        check_quality(file_list)
    else:
        pass

if __name__ == "__main__":
    main()



