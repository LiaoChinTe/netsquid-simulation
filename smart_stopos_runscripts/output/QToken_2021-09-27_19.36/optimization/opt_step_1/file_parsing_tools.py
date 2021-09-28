"""
Tools for reading in a folder of data files and produce a single csv file.
"""

import sys
import os
import csv
from abc import ABCMeta


CSV_DELIMITER = ","


class FileParser(metaclass=ABCMeta):
    """
    Abstract base class for an object
    that takes parses a single file or
    a folder of files. It can also produce a CSV-file.

    Intended to be subclassed: the user can for example
    make a YAMLFileParser, which is able to read in YAML-files,
    process them, and produce a single CSV file with the results
    of the processing.

    Notes
    -----
    The results of the parsing is stored in the attribute `values`. 
    """

    FILE_EXTENSION = None

    def __init__(self):
        self._values = []

    @property
    def values(self):
        return self._values

    def parse_file(self, filename):

        # check extension
        if not filename.endswith(self.FILE_EXTENSION):
            raise TypeError("filename {} does not end in "\
                    .format(filename, self.FILE_EXTENSION))

        # parse file
        self._values += self._parse_file(filename)

    def _parse_file(self, filename):
        """
        Meant to be overwritten.
        """
        pass

    def parse_folder(self, folder_name):
        filenames = [file_name for file_name in os.listdir(folder_name)]
        for filename in filenames:
            if filename.endswith(self.FILE_EXTENSION):
                self.parse_file(filename=os.path.join(folder_name, filename))

    def to_csv_output_file(self, csv_filename):
        """
        Writes the content of `self.values` directly to file
        by iterating over the elements.
        """
        # FIXME 
        if os.path.exists(csv_filename):
            os.remove(csv_filename)
            print("Remove  *csv file")
        with open(csv_filename, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=CSV_DELIMITER)
            for element in self.values:
                csv_writer.writerow(element)


class CSVFileParser(FileParser):
    """
    FileParser for CSV files.
    For more information, see the documentation of the base class
    :obj:`~netsquid_optimization.analysistools.file_parsing_tools.FileParser`.
    """
    FILE_EXTENSION = "csv"

    def _parse_file(self, filename):
        rows = []
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=CSV_DELIMITER)
            for row in csv_reader:
                rows.append(row)
        return rows
                

class SQLDatabaseParser(FileParser):
    """
    FileParser for SQL files.
    For more information, see the documentation of the base class
    :obj:`~netsquid_optimization.analysistools.file_parsing_tools.FileParser`.
    """

    FILE_EXTENSION = "db"

    def _parser_file(self, filename):
        #TODO
        pass


FILE_PARSERS = [CSVFileParser, SQLDatabaseParser]


def turn_folder_into_csv_output_file(folder_name, csv_output_filename, file_extension="csv"):
    """
    Reads all files in folder <folder_name> with extension type
    <file_extension>, process them using the corresponding 
    :obj:`~netsquid_optimization.analysistools.file_parsing_tools.FileParser`
    class, and produce a single CSV file that holds the results
    of that processing.
    """
   
    # Find the correct file parser for the file extension
    fileparser = None
    for fileparser_cls in FILE_PARSERS:
        if file_extension == fileparser_cls.FILE_EXTENSION:
            fileparser = fileparser_cls()
    if fileparser is None:
        raise ValueError("No FileParser known for the extension {}".format(file_extension))

    # Process all files in the folder an put the results in 
    # a single csv file
    fileparser.parse_folder(folder_name=folder_name)

    fileparser.to_csv_output_file(csv_filename=csv_output_filename)

