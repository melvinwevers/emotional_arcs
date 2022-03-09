#!/usr/bin/python

import argparse
import logging
import os

from src.process_data import pre_process
from src.extract_valence import extract_valence 



if __name__ == '__main__':
    '''
    script for preprocessing books and extracting valence
    example use: python run.py -i ./data/raw -o ./data/emotion_data -t ./data/tmp 
    
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_path', help='input folder', required=True)
    parser.add_argument('-o', '--output_path', help='output folder', required=True)
    parser.add_argument('-t', '--temp', help='temp folder', required=True)
    parser.add_argument('-n', '--normalize', help='normalize valence results', default = True, type=bool)

    args = parser.parse_args()


    logging.basicConfig(filename=args.output_path + "/script.log", level=logging.INFO)
    logging.info('inputfolder:'  + args.input_path)
    logging.info('outputfolder: ' + args.output_path)


    print('preprocessing')
    pre_process(args.input_path, args.temp) #output here is temp folder
    extract_valence(args.temp, args.output_path, args.normalize) #input here is temp folder
    



