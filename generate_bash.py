#!/usr/bin/env python3
#! --- coding:utf-8 ---


INPUT_PAIR = [
    (f'right{i}.txt', f'right{j}.txt')
    for i in range(11)
    for j in range(11)
    if j > i
]

BASH_HEADER = """
#!/usr/bin/bash

EXEC_PATH=""
LOG_DIR=""
DATA_DIR=""

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
                    'pueue add -i -- ${EXEC_PATH} ${DATA_DIR}\\'
                    + model
                    + ' ${DATA_DIR}\\'
                    + data
                    + f' 0 None {MSE_Thresh} -3.1416 -3.1416 -3.1416 6.2832 -0.5 -0.5 -0.5 1.0 {trimFraction/100.0} {distTransSize} 2.0 >'
                    + ' ${LOG_DIR}/'
                    + f'{id_}.txt'
                )
                id_ += 1

print('pueue status')
