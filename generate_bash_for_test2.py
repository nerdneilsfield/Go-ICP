# /usr/bin/env python3
#! --- coding: utf-8 ---

import argparse
import os
import sys

parser = argparse.ArgumentParser(description='generate bash for running test')

parser.add_argument(
    '--exec-path',
    type=str,
    default='./GoICP_BF',
    help='the path to the exec file',
)
parser.add_argument(
    '--log-dir', type=str, default='./log', help='the path to the log dir'
)
parser.add_argument(
    '--data-dir', type=str, default='./data', help='the path to the data dir'
)
parser.add_argument(
    '--result-dir',
    type=str,
    default='./result',
    help='the path to the result dir',
)

args = parser.parse_args()

if (
    args.exec_path is None
    or args.log_dir is None
    or args.data_dir is None
    or args.result_dir is None
):
    print(
        'Please specify the path to the exec file, log dir, data dir and result dir'
    )
    sys.exit(1)


INPUT_PAIR = [
    (f'right{i}.txt', f'right{j}.txt')
    for i in range(11)
    for j in range(11)
    if j > i
]

BASH_HEADER = f"""
#!/usr/bin/bash

EXEC_PATH="${os.path.abspath(args.exec_path)}"
LOG_DIR="${os.path.abspath(args.log_dir)}"
DATA_DIR="${os.path.abspath(args.data_dir)}"
RESULT_DIR="${os.path.abspath(args.result_dir)}"

# use half thread not all
pueue parallel $(($(nproc) / 2))

"""

MSE_Thresh_Values = [0.001, 0.0001, 0.00001]
distTransSize_Values = range(0, 600, 50)
trimFraction_Values = range(0, 100, 20)

# print(len(INPUT_PAIR))

print(BASH_HEADER)

id_ = 0
for model, data in INPUT_PAIR:
    # print(model, data)
    for MSE_Thresh in MSE_Thresh_Values:
        for distTransSize in distTransSize_Values:
            for trimFraction in trimFraction_Values:
                print(
                    'pueue add  -- "${EXEC_PATH} ${DATA_DIR}/'
                    + model
                    + ' ${DATA_DIR}/'
                    + data
                    + ' 0'
                    + ' ${RESULT_DIR}/'
                    + f'${id_}.txt'
                    + f'{MSE_Thresh} -3.1416 -3.1416 -3.1416 6.2832 -0.5 -0.5'
                    + f' -0.5 1.0 {trimFraction/100.0} {distTransSize} 2.0 >'
                    + ' ${LOG_DIR}/'
                    + f'{id_}.txt"'
                )
                id_ += 1

print('pueue status')
