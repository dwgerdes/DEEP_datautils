import pandas as pd
import glob
import easyaccess as ea
import argparse as ap
import os
'''
Write catalog contents to the database
'''

def writedb(file_list, table, dbname="umtno"):
    conn = ea.connect(section=dbname)
    for f in files:
        df = pd.read_csv(f)
        print("Writing {} objects from file {} to database table {}".format(len(df), f, table))
        conn.load_table(df, tablename=table)

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
    else:
        pass

if __name__ == "__main__":
    main()



