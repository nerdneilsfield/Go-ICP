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


def remove_lineheadandtail_space(text):
    while text[0] == '\t':
        text = text[1:]
    while text[0] == ' ':
        text = text[1:]
    while text[-1] == '\t':
        text = text[:-1]
    while text[-1] == ' ':
        text = text[:-1]
    return text


class Result:
    def __init__(self):
        self.T = []
        self.R = []

    def parse_result_file(self, file):

        with open(file, 'r') as f:
            lines = f.readlines()
            if len(lines) >= 9:
                self.R.extend(remove_lineheadandtail_space(lines[-6]).split())
                self.R.extend(remove_lineheadandtail_space(lines[-5]).split())
                self.R.extend(remove_lineheadandtail_space(lines[-4]).split())
                self.T[0] = remove_lineheadandtail_space(lines[-3])
                self.T[1] = remove_lineheadandtail_space(lines[-2])
                self.T[2] = remove_lineheadandtail_space(lines[-1])
            else:
                print('wrong line of result')


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

        # for result file
        self.index = 0
        self.T = ['0', '0', '0']
        self.R = ['0', '0', '0', '0', '0', '0', '0', '0', '0']

    def __str__(self):
        T_str = '\t'.join(self.T)
        R_str = '\t'.join(self.R)
        return f'{self.index}\t{1 if self.is_success else 0}\t{self.model}\t{self.data}\t{self.mse}\t{self.dist}\t{self.trimming}\t{self.build_time}\t{self.register_time}\t{self.total_time}{T_str}\t{R_str}'

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
            self.total_time = (
                log_lines[-1][:-1]
                .replace('\t', '')
                .replace('\n', '')
                .replace(' ', '')
            )
            self.register_time = (
                log_lines[-5][:-1]
                .replace('\t', '')
                .replace('\n', '')
                .replace(' ', '')
            )

        self.model = (
            log_lines[13]
            .split('/')[-1][:-1]
            .replace('\t', '')
            .replace('\n', '')
            .replace(' ', '')
        )
        self.data = (
            log_lines[14]
            .split('/')[-1][:-1]
            .replace('\t', '')
            .replace('\n', '')
            .replace(' ', '')
        )
        self.mse = (
            log_lines[1][:-1]
            .replace('\t', '')
            .replace('\n', '')
            .replace(' ', '')
        )
        self.trimming = (
            log_lines[10][:-1]
            .replace('\t', '')
            .replace('\n', '')
            .replace(' ', '')
        )
        self.dist = (
            log_lines[11][:-1]
            .replace('\t', '')
            .replace('\n', '')
            .replace(' ', '')
        )
        self.build_time = (
            log_lines[22][:-1]
            .replace('\t', '')
            .replace('\n', '')
            .replace(' ', '')
        )

    def parse_log_file(self, file, index, result_dir):
        self.index = index
        with open(file, 'r') as f:
            self.parse_logs(f.readlines())
        if self.is_success:
            result_file_path = os.path.abspath(
                os.path.join(result_dir, f'{self.index}.txt')
            )

            result = Result()
            result.parse_result_file(result_file_path)
            self.T = result.T
            self.R = result.R


def parse_log_file(log_dir, result_dir, start_index, end_index, csv_file):

    log_path = ''

    test_log = TestLog()

    for index in range(start_index, end_index + 1):

        log_path = os.path.join(os.path.abspath(log_dir), f'{index}.txt')

        logging.debug(f'parse log: {log_path}')

        test_log.index = index

        test_log.parse_log_file(log_path, index, result_dir)

        with open(csv_file, 'a') as f:
            logging.debug('write information to csv file')
            logging.debug(str(test_log))
            f.write(str(test_log))
            f.write('\n')


def add_csv_header(csv_file):
    with open(csv_file, 'w') as f:
        f.write(
            'index\tis_success\tmodel\tdata\tmse\tdist\ttrimming\tbuild_time\tregister_time\ttotal_time\tT0\tT1\tT2\tR1\tR2\tR3\tR4\tR5\tR6\tR7\tR8\tR9\n'
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
        '-r',
        '--result_dir',
        type=str,
        default='./results',
        help='the directory for results',
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
        args.directory,
        args.result_dir,
        args.start_index,
        args.end_index,
        args.output_csv_file,
    )
