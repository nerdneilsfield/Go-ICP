#!/usr/bin/env python3
#! --- coding:utf-8 ---



INPUT_PAIR = [(f'right{i}.txt', f'right{j}.txt') for i in range(11) for j in range(11) if j > i]


if __name__ == '__main__':
    # for (source_pc, target_pc) in INPUT_PAIR:
    #     print(f'source_pc: {source_pc}, target_pc: ${target_pc}')
    print(len(INPUT_PAIR))
    for pair in INPUT_PAIR:
        print(pair)
