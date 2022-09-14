import polars as pl

import argparse

parser = argparse.ArgumentParser(description='Help dealing with multiple data')

parser.add_argument(
    '-c',
    '--csv-file',
    type=str,
    default='partialpointcloud.csv',
    help='path to input csv file, which is the output of analysis_logs2.py',
)
parser.add_argument(
    '-o',
    '--out-file',
    type=str,
    default='partialpointcloud_after.csv',
    help='the output csv file contains the finding pairs',
)

args = parser.parse_args()


df = pl.read_csv(args.csv_file, sep='\t')
print(len(df))

# print(df[0:5])
# df2 = df.filter(pl.col('is_success') == 1)

PAIRMETER = [
    (f'partialright0-{i}.txt', f'partialright1-{i}.txt') for i in range(10)
]

df_list = []

for i, (model, data) in enumerate(PAIRMETER):
    # index += 1
    print(i, ' ', model, ' ', data)
    df3 = df.filter((pl.col('model') == model) & (pl.col('data') == data))
    # print(len(df3))
    # print(df3[:10,1:10])
    df4 = df3.filter(pl.col("trimming") == 0.4)
    print(df4)
    df4.write_csv(f"build/test_{i}+.csv", sep="\t")
    # if i == 0:
    #     df_list.append(df3)
    # else:
    #     df_list.append(df3[1:])

for sdf in df_list:
    print(len(sdf))


# df.write_csv(args.out_file)
