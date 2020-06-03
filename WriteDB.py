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

def check_quality(file_list, bad_threshold=20000):
    bad_file = []
    bad_exp = []
    bad_counts = []
    for f in file_list:
        df = pd.read_csv(f)
        exps, counts = np.unique(df.EXPNUM.values, return_counts=True)
        print(counts)
        median = np.median(counts)
        std = np.std(counts)
        print("Median = {}, stddev = {}".format(median, std))
        for ind, exp in enumerate(exps):
            if counts[ind] > bad_threshold:
                print("Possible bad exposure: File = {}, Expnum = {}, count = {}".format(f, exp, counts[ind]))
                bad_file.append(f)
                bad_exp.append(exp)
                bad_counts.append(counts[ind])
    return bad_file, bad_exp, bad_counts

def writedb(file_list, table, dbname="umtno"):
    conn = ea.connect(section=dbname)
    table_exists = False
    query = "select table_name from user_tables where table_name='{}'".format(table)
    result = conn.query_to_pandas(query)
    if (len(result)): table_exists = True
    for f in file_list:
        df = pd.read_csv(f)
        print("Writing {} objects from file {} to database table {}".format(len(df), f, table))
        if table_exists:
            conn.append_table(f, name=table)
        else:
            conn.load_table(f, name=table)
            table_exists = True

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
        table = "DIFF_SE_OBJECT"
        file_list = glob.glob(os.path.join(rootdir, filetype))
        writedb(file_list, table)
        bad_file, bad_exps, bad_counts = check_quality(file_list, bad_threshold=0)
        df = pd.DataFrame({'file':bad_file, 'expnum':bad_exps, 'counts':bad_counts})
        df.to_csv('counts_by_expnum.csv', index=None)
    else:
        pass

if __name__ == "__main__":
    main()



