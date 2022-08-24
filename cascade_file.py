import os
import re
import pandas as pd
import logging as lg


class APDM_File:

    def __init__(self, filepath):

        if os.path.exists(filepath):
            self.path = filepath
            self.filename = os.path.basename(filepath)
            self.filesize = os.path.getsize(filepath)
            if self.parseFileName():
                self.content = self._parseContent()
        else:
            raise OSError('File does not exist: {}'.format(filepath))

    def parseFileName(self):
        if (comp := re.search('^X(\S{7})_(\d{8})_(\d{6})_(\S+)_Compl_(\d+|true|false)_ERR_(\d+).xml', self.filename)):
            return dict(zip(['vin', 'date', 'time', 'test_name', 'complete', 'error'], comp.groups()))
        else:
            return None

    def _parseContent(self):

        self.basic_information_dictionary = {}
        detail_result_list = []
        self.result_variable_dict = {}

        with open(self.path, encoding = 'ISO-8859-1', errors = 'ignore') as f:
            filecontent_lines = f.readlines()

        for line in filecontent_lines:
            if re.search('<fileInfo', line):
                dict_1 = dict(re.findall('(\S+)="(.+?)"', line))
                self.basic_information_dictionary.update(dict_1)
            if re.search('<vehicleInfo', line):
                dict_2 = dict(re.findall('(\S+)="(\S+?)"', line))
                self.basic_information_dictionary.update(dict_2)
            if re.search('<testInfo', line):
                dict_3 = dict(re.findall('(\S+)="(\S+?)"', line))
                self.basic_information_dictionary.update(dict_3)
            if re.search('<result ', line):
                dict_r = dict(re.findall('(\S+)="(.*?)"', line))
                detail_result_list.append(dict_r)
            # if re.search('<resultVariable', line):
            #     dict_rv = dict(re.search('variableKey="(.+)" variableValue="(.+)"', line).groups())
            #     print(re.search('variableKey="(.+)" variableValue="(.+)"', line).groups())

            # self.result_variable_dict.update(dict_rv)
        self.detail_df = pd.DataFrame(detail_result_list)
        self.detail_df = self.detail_df.sort_index(axis = 1, ascending = False)


class PROTOCOL_File:

    def __init__(self, filepath):

        if os.path.exists(filepath):
            self.path = filepath
            self.filename = os.path.basename(filepath)
            self.filesize = os.path.getsize(filepath)
            self.parseFileName()
            self.content = self._parseContent()
        else:
            raise OSError('File does not exist: {}'.format(filepath))

    def parseFileName(self):

        if (comp := re.search('^(\S{7})_(\d{8})_(\d{6})_(\S+)_Compl_(\d+|true|false)_ERR_(\d+).xml', self.filename)):
            return dict(zip(['vin', 'date', 'time', 'test_name', 'complete', 'error'], comp.groups()))
        else:
            return None

    def _parseContent(self):

        self.basic_information_dictionary = {}
        detail_result_list = []
        self.result_variable_dict = {}

        with open(self.path, encoding = 'ISO-8859-1', errors = 'ignore') as f:
            filecontent_lines = f.readlines()

        for line in filecontent_lines:
            if re.search('<fileInfo', line):
                dict_1 = dict(re.findall('(\S+)="(.+?)"', line))
                self.basic_information_dictionary.update(dict_1)
            if re.search('<vehicleInfo', line):
                dict_2 = dict(re.findall('(\S+)="(\S+?)"', line))
                self.basic_information_dictionary.update(dict_2)
            if re.search('<testInfo', line):
                dict_3 = dict(re.findall('(\S+)="(\S+?)"', line))
                self.basic_information_dictionary.update(dict_3)
            if re.search('<result ', line):
                dict_r = dict(re.findall('(\S+)="(.*?)"', line))
                detail_result_list.append(dict_r)
            if re.search('<resultVariable', line):
                dict_rv = dict([re.search('variableKey="(.+)" variableValue="(.+)"', line).groups()])
                self.result_variable_dict.update(dict_rv)

            self.detail_df = pd.DataFrame(detail_result_list)
            self.detail_df = self.detail_df.sort_index(axis = 1, ascending = False)


class ORDER_File:

    def __init__(self, filepath):

        if os.path.exists(filepath):
            self.path = filepath
            self.filename = os.path.basename(filepath)
            self.filesize = os.path.getsize(filepath)

            with open(self.path, 'r', encoding = 'ISO-8859-1', errors = 'ignore') as f:
                order_data_line = ''
                for line in f.readlines():
                    if re.search('<orderData ', line):
                        order_data_line = line
                        break
            if not order_data_line:
                self._parseContent(order_data_line)
                self._getOptions()
                del order_data_line
            else:
                raise ValueError('No <orderData> found : {}'.format(filepath))
        else:

            raise OSError('File does not exist: {}'.format(filepath))

    def _parseContent(self, order_data_line: str):
        DISIRED_KEYS = ['longVIN', 'shortVIN', 'orderId', 'fzs', 'integrationLevel', 'fabricCode', 'colourCode',
                        'timeCriteria', 'typeKey', 'series', 'vehicleType', 'bodyLayout', 'countryVariant',
                        'engineSeries', 'engineDerivative', 'motorSport', 'exhaustType', 'gearboxType', 'bodyType',
                        'driveType', 'driveConfiguration', 'numberOfDoors', 'engineSize', 'hybridType',
                        'driveUnitNumber', 'firstCreationDate', 'latestCreationDate']
        self.data_dictionary = dict(
                [item for item in re.findall('(\S+)="(.+?)"', self.first_line) if item[0] in DISIRED_KEYS]
        )
        if self.data_dictionary == {}:
            lg.warning('No Data Read :{}'.format(self.filename))

    def _getOptions(self):
        self.option_code_list = re.findall('<saCode>(\w{3})</saCode>', self.first_line)


if __name__ == '__main__':
    a = ORDER_File(
            r"C:\00_MyFolder\02_Programming\02_Projects\checkinfile\test_resource\oder_file\AM456768.xml"
    )
