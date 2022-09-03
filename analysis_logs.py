#!/usr/bin/env python3
# coding=utf-8

import argparse
import logging
import os


def search_text(text, lines):
    # line_len = len(lines)
    # if line_len == 1:
    #     return (text in lines[0])
    # if line_len % 2 == 0:
    #     return search_text(lines[:(line_len / 2 + 1)]) or search_text(lines[(line_len / 2 + 1):])
    # else:
    #     return search_text(lines[:((line_len+1) / 2 + 1)]) or search_text(lines[((line_len+1) / 2+1):])
    for line in lines:
        if text in line:
            return True
    return False


class TestLog:
    def __init__(
        self,
        index=0,
        model='',
        data='',
        mse=0.001,
        dist=300,
        trimming=0.0,
        build_time=-1.0,
        register_time=-1.0,
        total_time=-1.0,
    ):
        self.index = index
        self.model = model
        self.data = data
        self.mse = mse
        self.dist = dist
        self.trimming = trimming
        self.build_time = build_time
        self.register_time = register_time
        self.total_time = total_time
        self.is_success = False

    def __str__(self):
        return f'{self.index}\t{1 if self.is_success else 0}\t{self.model}\t{self.data}\t{self.mse}\t{self.dist}\t{self.trimming}\t{self.build_time}\t{self.register_time}\t{self.total_time}'

    def print(self):
        print('index: {}'.format(self.index))
        print('status: ', 'sucess' if self.is_success else 'failure')
        print('model: ', self.model)
        print('data: ', self.data)
        print('mse: ', self.mse)
        print('dist: ', self.dist)
        print('trimming: ', self.trimming)
        print('build_time: ', self.build_time)
        print('register_time: ', self.register_time)
        print('total_time: ', self.total_time)

    def parse_logs(self, log_lines):
        self.is_success = False
        if search_text('Success', log_lines):
            self.is_success = True

        if self.is_success:
            self.total_time = log_lines[-1][:-1]
            self.register_time = log_lines[-5][:-1]

        self.model = log_lines[13].split('/')[-1][:-1]
        self.data = log_lines[14].split('/')[-1][:-1]
        self.mse = log_lines[1][:-1]
        self.trimming = log_lines[10][:-1]
        self.dist = log_lines[11][:-1]
        self.build_time = log_lines[22][:-1]

    def parse_log_file(self, file):
        with open(file, 'r') as f:
            self.parse_logs(f.readlines())


def parse_log_file(directory, start_index, end_index, csv_file):

    log_path = ''

    test_log = TestLog()

    for index in range(start_index, end_index + 1):

        log_path = os.path.join(os.path.abspath(directory), f'{index}.txt')

        logging.debug(f'parse log: {log_path}')

        test_log.index = index

        test_log.parse_log_file(log_path)

        with open(csv_file, 'a') as f:
            logging.debug('write information to csv file')
            logging.debug(str(test_log))
            f.write(str(test_log))
            f.write('\n')


def add_csv_header(csv_file):
    with open(csv_file, 'w') as f:
        f.write(
            'index\tis_success\tmodel\tdata\tmse\tdist\ttrimming\tbuild_time\tregister_time\ttotal_time\n'
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A log parser for go-icp')
    parser.add_argument(
        '-d',
        '--directory',
        type=str,
        default='.',
        help='the directory of output text',
    )
    parser.add_argument(
        '-s',
        '--start_index',
        type=int,
        default=0,
        help='the start index of logs',
    )
    parser.add_argument(
        '-e',
        '--end_index',
        type=int,
        default=0,
        help='the end index of logs(inclued)',
    )
    parser.add_argument(
        '-o',
        '--output_csv_file',
        type=str,
        default='go_icp.csv',
        help='the output csv file of experiment data',
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='show more information'
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    add_csv_header(args.output_csv_file)
    parse_log_file(
        args.directory, args.start_index, args.end_index, args.output_csv_file
    )
