#! /usr/bin/env python3

'''concatenate last rows of .csv files under output/ into one file: csv_output.csv'''

from file_parsing_tools import turn_folder_into_csv_output_file
import os
import shutil


if __name__ == "__main__":
    # Create directory
    if not os.path.exists('output'):
        os.mkdir('output')
    
    current_path = os.getcwd()
    new_path = current_path + '/output'
    for f in os.listdir('.'):
        ext = os.path.splitext(f)[-1].lower()
        if ext == '.csv':
            shutil.move(current_path+'/'+f, new_path+'/'+f)
    
    turn_folder_into_csv_output_file(folder_name="output",
                                     csv_output_filename="csv_output.csv",
                                     file_extension="csv")
