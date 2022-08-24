# -*- coding: utf-8 -*-
# @Time : 4/15/2022 9:27 AM
# @Author : Zikikov
# @File : checkin_file.py

import re, os, datetime, numpy
import pandas as pd
from pandas import DataFrame, Series
import json as js
import logging as lg

from reference_table import Table

T = Table()

class CheckinFile:
    BROKEN_RISK = False

    def __init__(self, absolute_file_path: str):

        if os.path.exists(absolute_file_path):
            self.abs_path = absolute_file_path
            self._file_information_check()
            self._initialRead()
        else:
            raise OSError('File path does not exist:{}'.format(absolute_file_path))

    def _file_information_check(self):
        self.filesize_kb = round(os.path.getsize(self.abs_path) / 1024)
        self.basename = os.path.basename(self.abs_path)

    def _initialRead(self):

        self.sectiondict = {}
        with open(self.abs_path, 'r', errors = 'ignore', encoding = 'ANSI', ) as f:
            filefulltext = f.read()
        sectionkeys = list(map(lambda x: x.lower(), re.findall('(?<=\n)Result:.+|^Result:.+', filefulltext)))
        sectionamouts = len(sectionkeys)
        sectionamouts_set = len(set(sectionkeys))
        sectioncontents = re.split('\n(?=Result:)', filefulltext)
        if sectionamouts == len(sectioncontents):
            if sectionamouts_set != sectionamouts:
                sectionkeys.reverse()
                sectioncontents.reverse()
            self.sectiondict = dict(zip(sectionkeys, sectioncontents))
        else:
            self.BROKEN_RISK = True
            lg.warning('Empty Section Exists:\n{}'.format(self.abs_path))

    def read_all(self):

        self.readVehicleData()
        self.readSoftwareIdData()
        self.readErrorMemorry()
        self.readCheckControlMessage()
        self.readHighVoltageStorageData()

    def readVehicleData(self):

        if vehicledatacontent := self.sectiondict.get('Result: Read Vehicle Data'.lower()):
            self.vehicleDataSection = VehicleDataSection()
            self.vehicleDataSection.content = vehicledatacontent
            self.vehicleDataSection.readdata()
            return True
        else:
            lg.warning('readVehicleData Failed: {}'.format(self.abs_path))
            return None

    def readSoftwareIdData(self):
        if softwareiddatacontent := self.sectiondict.get('Result: Read ID Data  ( BN2010 )'.lower()):
            try:
                self.softwareDataSection = SoftwareIdDataSection()
                self.softwareDataSection.content = softwareiddatacontent
                self.softwareDataSection.readdata()
                return True
            except Exception as error:
                lg.warning('Read Software failed.{}'.format(self.abs_path))
                return None
        else:
            lg.error('No SVK section. {}'.format(self.abs_path))
            return None

    def readErrorMemorry(self, read_value = False):

        if (errormemorydatacontent_basic := self.sectiondict.get('Result: Read error memory'.lower())):
            self.errorMemorySection = ErrorMemorySection()
            self.errorMemorySection.content = errormemorydatacontent_basic
            self.errorMemorySection.readbasicsection()
            if self.errorMemorySection.error_amout != 0:
                if (errormemorydatacontent_detail := self.sectiondict.get('Result: Read error memory Details'.lower())):
                    self.errorMemorySection.content2 = errormemorydatacontent_detail
                    self.errorMemorySection.readdetailsection(read_value = read_value)
                    return True
                else:
                    # raise AttributeError('No Error Detail Section :{}.'.format(self.abs_path))
                    lg.error('No Error Detail Section :{}.'.format(self.abs_path))
                    return None
            else:
                lg.info('Error amout is 0.')
                pass

        else:
            # raise AttributeError('No Error Basic Section :{}'.format(self.abs_path))
            lg.error('No Error Basic Section :{}'.format(self.abs_path))
            return None

    def readCheckControlMessage(self):

        if (errormemorydatacontent_basic := self.sectiondict.get('Result: Read Check Control History'.lower())):
            self.checkControlSection = CheckControlSection()
            self.checkControlSection.content = errormemorydatacontent_basic
            if self.checkControlSection.readCheckControlMessage():
                return True
            else:
                return False
        else:
            return None

    def readHighVoltageStorageData(self):

        if (highvoltagestoragecontent := self.sectiondict.get('result: read high-voltage storage data')):
            self.highVoltageStorageDataSection = HighVoltageStorageDataSection()
            self.highVoltageStorageDataSection.content = highvoltagestoragecontent
            if self.highVoltageStorageDataSection.readHighVoltageStorageData():
                return True
            else:
                return False
        elif (highvoltagestoragecontent := self.sectiondict.get('Result: Hybrid data read'.lower())):
            self.highVoltageStorageDataSection = HighVoltageStorageDataSection()
            self.highVoltageStorageDataSection.content = highvoltagestoragecontent
            if self.highVoltageStorageDataSection.readHighVoltageStorageData():
                return True
            else:
                return False
        else:

            return None


class BaseSection:
    content = ''
    content2 = ''
    content3 = ''
    content4 = ''


class VehicleDataSection(BaseSection):

    def __init__(self):

        self.data_dictionary = {
                'datetime_f': datetime.datetime(1991, 12, 25, 0, 0, 0),
                'datetime_s': '',
                'systemtime': -1,
                'series': '',
                'battery_capacity': -1,
                'soc_lv': -1,
                'sov_hv': -1,
                'istep_cas': '',
                'istep_ho': '',
                'istep_plant': '',
                'odo_display': -1,
                'odo_absolute': -1,
                'options': '',
                'pu': '',
                'typekey': '',
                'vin17': '',
                'vin7': '',
                'fuel': -1,
        }

    def readdata(self):

        def _readdatetime(self, line: str):

            date_string_complie = re.search('\d\d\.\d\d\.\d\d\d\d', line)
            time_string_complie = re.search('\d\d:\d\d:\d\d', line)
            datetime_string = '{0}_{1}'.format(date_string_complie.group(), time_string_complie.group())
            self.data_dictionary.update(
                    {
                            'datetime_s': datetime_string,
                            'datetime_f': datetime.datetime.strptime(datetime_string, '%d.%m.%Y_%H:%M:%S')
                    }
            )

        def _readsystemtime(self, line: str):
            if systemtime_complie := re.search('\d+', line):
                self.data_dictionary['systemtime'] = int(systemtime_complie.group())

        def _readseries(self, line: str):

            if (series_complie := re.search('.+', line.split(':')[-1])):
                self.data_dictionary['series'] = series_complie.group()

        def _readbattery(self, line: str):

            if (battery_complie := re.search('\d+', line)):
                self.data_dictionary['battery_capacity'] = int(battery_complie.group())

        def _readsoclv(self, line: str):

            if soclv_complie := re.search('\d+', line):
                self.data_dictionary['soc_lv'] = int(soclv_complie.group())

        def _readvin(self, line: str):

            if 'long' in line:
                if (longvin_complie := re.search('\S+', line.split(':')[-1])):
                    self.data_dictionary['vin17'] = longvin_complie.group()
            else:
                if shortvin_complie := re.search('\S+', line.split(':')[-1]):
                    self.data_dictionary['vin7'] = shortvin_complie.group()

        def _readilevel(self, line: str):

            if (ilevel_complie := re.search('\S{4}-\d{2}-\d{2}-\d{3}', line)):
                ilevel_string = ilevel_complie.group()
                if 'Plant' in line:
                    self.data_dictionary['istep_plant'] = ilevel_string
                if 'HO' in line:
                    self.data_dictionary['istep_ho'] = ilevel_string
                if 'CAS' in line or 'backup' in line.lower():
                    self.data_dictionary['istep_cas'] = ilevel_string

        def _readorder(self, line: str):

            value_string = line.split(':')[-1]
            if (pu_complie := re.search('\d{4}', value_string)):
                self.data_dictionary['pu'] = pu_complie.group()
            if (typekey_complie := re.search(('\S{4}$'), value_string)):
                self.data_dictionary['typekey'] = typekey_complie.group()

        def _readodo(self, line: str):

            value_string = line.split(':')[-1]
            if (odo_complie := re.search('\d+$', value_string)):
                odo_value = int(odo_complie.group())
                if 'Display' in line:
                    self.data_dictionary['odo_display'] = odo_value
                if 'Absolut' in line:
                    self.data_dictionary['odo_absolute'] = odo_value

        def _readfuel(self, line: str):
            if '=' in line:
                value_string = line.split('=')[-1]
                if (fuel_complie := re.search('\S+', value_string)):
                    fuel_value = round(float(fuel_complie.group()), 2)
                    self.data_dictionary['fuel'] = fuel_value
            else:
                pass

        def _readsochv(self, line: str):
            value_string = line.split(':')[-1]
            if (sochv_complie := re.search('\S+(?= %)', value_string)):
                self.data_dictionary['soc_hv'] = round(float(sochv_complie.group()), 2)

        def _readoptions(self, line: str):

            value_string = line.split(':')[-1]
            self.data_dictionary['options'] += '_' + '_'.join(re.findall('\w{3}', value_string))

        if self.content == '':
            # raise ValueError('No vehicle data content loaded.')
            lg.error('No vehicle data content loaded.')
        else:
            contentlist = self.content.split('\n')
            for line in contentlist:
                if re.search('^Date', line):
                    _readdatetime(self, line)
                if re.search('^Systemtime', line):
                    _readsystemtime(self, line)
                if re.search('^Series', line):
                    _readseries(self, line)
                if re.search('^Battery', line):
                    _readbattery(self, line)
                if re.search('^Charge state', line):
                    _readsoclv(self, line)
                if re.search('VIN', line):
                    _readvin(self, line)
                if re.search('I-Leve', line):
                    _readilevel(self, line)
                if re.search('FA-order', line):
                    _readorder(self, line)
                if re.search('KM-State', line):
                    _readodo(self, line)
                if re.search('Fuel', line):
                    _readfuel(self, line)
                if re.search('HV-SoC', line):
                    _readsochv(self, line)
                if re.search('Options', line):
                    _readoptions(self, line)


        # self.data_series=Series(self.data_dictionary)


class ControlUnitSVK:

    def __init__(self):
        self.name = ''
        self.flashdate = datetime.date(1991, 12, 25)
        self.svk = []


class SoftwareIdDataSection(BaseSection):

    def __init__(self):
        self.data_dictionary = {}

    def readdata(self):

        _data_list = []
        # ------------------------------------------------------------------------------------------------------------------------------
        def _readdataline(line: str):

            if (data_complie := re.search(
                    '(^\w{2}\s{1,3}\S+).+(\d(?=\s{3})|\d{2}(?=\s{2})|\d{3}(?=\s)).+(\d{4}\S{4}|FFFFFFFF|FF\d{2}\S{4})|\d{8}.+(\d{3}\.\d{3}\.\d{3})',
                    line
            )):
                data_tuple = data_complie.groups()

                if (date_complie := re.search('\d{2}\.\d{2}\.\d{4}', line)):
                    data_string = date_complie.group()
                    _data_list.append((data_tuple[0], 'flash_date', data_string, ''))
                else:
                    pass
                return data_tuple
            elif '<No SVK Data>' in line:
                lg.warning('No SVK Data of : {}'.format(line))
                return None
            else:
                lg.error('Can not parse data line:{}'.format(line))

        # ------------------------------------------------------------------------------------------------------------------------------
        if self.content == '':
            # raise ValueError('No software id data content loaded.')
            lg.warning('Can not read error amout')
            return None
        else:
            contentlist = self.content.split('\n')
            for line in contentlist:
                try:
                    if re.search('^\w{2}\s', line):
                        data_tuple = _readdataline(line)
                        _data_list.append(data_tuple)
                except:
                    continue

        for each in _data_list:
            if each[0] not in self.data_dictionary:
                t = ControlUnitSVK()
                t.name = each[0]
                if 'flash_date' == each[1]:
                    try:
                        t.flashdate = datetime.datetime.strptime(each[2], '%d.%m.%Y').date()
                    except ValueError:
                        t.flashdate = datetime.date(1991, 12, 25)
                self.data_dictionary[t.name] = t
            else:
                self.data_dictionary[each[0]].svk.append(
                        '{0}_{1}_{2}'.format(T.SVK_CODE.get(int(each[1])), each[2], each[3])
                )

        self.dataframe = pd.DataFrame(_data_list, columns = ['ECU', 'ID', 'ADRESS', 'VARIANT'])


class ErrorEntry(BaseSection):
    ecu, sgbd, hexcode, text, readynessflag_int, errorpresent_int, warningflag_int, occurencecounter_int, healingcounter_int, datasets = '', '', '', '', 0, 0, 0, 1, -1, []

    def update(self, datatuple: tuple):
        self.ecu, self.sgbd, self.hexcode, self.text, self.readynessflag_int, self.errorpresent_int, self.warningflag_int, self.occurencecounter_int, self.healingcounter_int = datatuple


class ErrorMemorySection(BaseSection):

    def readbasicsection(self):

        self.errorbasicdict = {}
        error_basic_list = self.content.split('\n')
        for line in error_basic_list:
            if re.search('^Amount', line):
                _amout = int(re.search('\d+', line).group())
            if ecu_complie := re.search('^\w{2}\s{1,3}\S+', line):
                _ecu = ecu_complie.group()
                if 'No Entry' in line:
                    error_amout = 0
                else:
                    if (error_amout_complie := re.search('\d+(?= Entries)|\d(?= Entry)', line)):
                        error_amout = int(error_amout_complie.group())
                    else:
                        # raise ValueError('Can not read error amout:{}'.format(line))
                        lg.error('Can not read error amout:{}'.format(line))
                self.errorbasicdict[_ecu] = error_amout
        self.error_amout = sum(self.errorbasicdict.values())

    def readdetailsection(self, read_value = False):

        _errordata, _hexcodelist, _amout = [], [], -1

        def readerrorpiece(errorpiece: str, read_value = read_value):

            def readpiececut_basic(piececut_basic: str):
                temp_entryobj = ErrorEntry()
                lines = piececut_basic.split('\n')
                _ecu, _sgbd, _hexcode, _text, _readynessflag_int, _errorpresent_int, _warningflag_int, _occurencecounter_int, _healingcounter_int = '', '', '', '', 0, 0, 0, 1, -1
                for line in lines:
                    if re.search('^Controller', line):
                        _ecu = re.search(r'\b\w{2}\s{2}\S+\b', line).group()
                        _sgbd = re.search('(?<=- ).+(?= -)', line).group()
                    if 'Failure Place' in line:
                        _hexcode = re.search(r'(?<=\s)0x\S+(?=\s)', line).group()
                        _text = re.search('(?<= - ).+', line).group()
                    if 'Readyness Flag' in line:
                        _readynessflag_int = int(re.search('\d+', line).group())
                    if 'Error present' in line:
                        _errorpresent_int = int(re.search('\d+', line).group())
                    if 'Warning Flag' in line:
                        _warningflag_int = int(re.search('\d+', line).group())
                    if 'Occurence Counter' in line:
                        if (occurencecounter_complie := re.search('\d+', line)):
                            _occurencecounter_int = int(occurencecounter_complie.group())
                        else:
                            _occurencecounter_int = -1
                    if 'Healing counter' in line:
                        if (healingcounter_complie := re.search('\d+', line)):
                            _healingcounter_int = int(healingcounter_complie.group())
                        else:
                            _healingcounter_int = -1
                temp_entryobj.update(
                        (_ecu, _sgbd, _hexcode, _text, _readynessflag_int, _errorpresent_int, _warningflag_int,
                         _occurencecounter_int, _healingcounter_int)
                )
                _hexcodelist.append(_hexcode)
                return temp_entryobj

            def readpiececut_dataset(piececut_dataset: str, read_value = read_value):

                _amout, _odo, _timestamp, _clockdate, _clocktime, datavaluelist = 0, -1, -1, '25.12.1991', '00:00:01', {}
                lines = piececut_dataset.split('\n')
                for line in lines:
                    if re.search('^Environment Amount', line) and '---' not in line:
                        _amout = int(re.search('\d+', line).group())
                    if 'Environment KM     :' in line:
                        if (comp := re.search('\d+|-\d+', line)):
                            _odo = int(comp.group())
                        else:
                            _odo = -1
                    if 'Environment Time' in line and 'ERROR' not in line and 'Supreme' not in line:
                        time_complie = re.search(
                                '((?<=\s)\d+(?=\s))\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2}:\d{2})', line
                        )
                        if time_complie:
                            try:
                                _clockdate = time_complie.group(2)
                                _clocktime = time_complie.group(3)
                                _timestamp = int(time_complie.group(1))
                            except:
                                pass
                    if re.search(
                            '(?<=^Environment c.\s{3})\d+|(?<=^Environment c.\s{2})\d+|(?<=^Environment Set\s{3})\d+|(?<=^Environment Set\s{2})\d+',
                            line
                    ) and read_value:
                        t = re.search(r'(\b\d+)\s{2}(.+)', line).groups()
                        datavaluelist.update({t[0]: t[1]})

                return (_amout, _odo, _timestamp, _clockdate, _clocktime, datavaluelist)

            errorpiece_cut1 = re.split(r'\d+\. Data Set\n', errorpiece)
            piececut_basic = errorpiece_cut1[0]
            piececut_datasets = errorpiece_cut1[1:]

            errorentry_obj = readpiececut_basic(piececut_basic)
            errorentry_obj.datasets = [readpiececut_dataset(piece_data) for piece_data in piececut_datasets]
            return errorentry_obj

        errorpiece_list = re.split(r'-{10,1000}\n', self.content2)

        for line in errorpiece_list[1].split('\n'):
            if re.search('^Amount', line):
                if (_amout_complie := re.search('\d+', line)):
                    _amout = int(_amout_complie.group())

            self.error_amout = _amout

        for piece in errorpiece_list[2:]:
            _errordata.append(readerrorpiece(piece))


        _l = []
        for errorentry in _errordata:
            base_tuple = (
                    errorentry.ecu, errorentry.sgbd, errorentry.hexcode, errorentry.text, errorentry.warningflag_int,
                    errorentry.occurencecounter_int, errorentry.errorpresent_int,
                    errorentry.healingcounter_int)
            for dataset_tuple in errorentry.datasets:
                _l.append((*base_tuple, *dataset_tuple[:5]))
        columns = ['ECU', 'SGBD', 'Hexcode', 'Text', 'WarningFlag', 'Occurence', 'PresentFlag', 'HealingCount',
                   'Amount', 'Odo', 'SystemTime', 'ErrorDate', 'ErrorTime']
        self.dataframe = DataFrame(_l, columns = columns)


class CheckControlSection(BaseSection):

    COLUMNS = ['ECU_ADR', 'ECU_NAME', 'JOBSTATUS', 'ODO', 'UNIT', 'TIMESTAMP', 'DATETIME', 'FREQUENCY', 'CC_ID',
               'CC_TEXT']

    def readCheckControlMessage(self):
        _memessage_list=[]

        def _getMessageAmount(basic_content):
            pass

        def _getMessageDataFrame(detail_content):
            pass

        if self.content == '':
            raise ValueError('No content loaded.')
        else:
            content_piece_list = re.split(r'-{10,1000}\n', self.content)
            if len(content_piece_list) < 3:
                return None
            else:
                if (_messageCount_complie := re.search('(?<=Amount {4}: )\d+', content_piece_list[1])):
                    _messageCount = int(_messageCount_complie.group())
                    if _messageCount == 0:
                        return None
                    else:
                        _messageLines = content_piece_list[2].split('\n')
                        for _line in _messageLines:
                            if re.search('^60 {2}KOMBI|63 {2}HEADUNIT', _line):
                                _memessage_list.append(
                                        # re.search('(^60  KOMBI|63  HEADUNIT)\s+OKAY\s+(\S+)\s+km\s+(\S+)\s+(\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(.+)(?=\n)',_line).groups()
                                        dict(zip(self.COLUMNS, re.split('\s{2,100}', _line)))
                                )
        if len(_memessage_list) == 0:
            return None
        else:
            self.dataframe = pd.DataFrame(_memessage_list)
            return True


class HighVoltageStorageDataSection(BaseSection):

    def __init__(self):
        self.dataDict = {}

    def readHighVoltageStorageData(self):

        def readCellLimitVoltage():

            for contentPiece in self.content_piece_list:
                if 'HVS_01 | STATUS_LESEN | ARG;MIN_MAX_ZELLSPANNUNGEN' in contentPiece:
                    _lines = contentPiece.split('\n')
                    for _line in _lines[1:]:
                        try:
                            keyName = re.search('^\S+', _line).group()
                            keyValue = re.search('(?<= ).+(?= V)', _line).group()
                            self.dataDict[keyName] = float(keyValue)
                        except Exception as error:
                            continue

        def readSOCZelleLimit():
            _d = {}
            _l = []

            for contentPiece in self.content_piece_list:
                if 'HVS_01 | STATUS_LESEN | ARG;SOC_ZELLE' in contentPiece:
                    _lines = contentPiece.split('\n')
                    for _line in _lines[1:]:
                        try:
                            keyName = re.search('STAT_SOC_CELL_\d+_WERT', _line).group()
                            theValue = re.search('(?<= ).+(?= %)', _line).group()
                            _d[keyName] = float(theValue)
                            _l.append(float(theValue))
                        except Exception as error:
                            # print(error, _line)
                            continue
                    _lvalid = [_e for _e in _l if _e > 0]
                    maxValue = max(_lvalid)
                    minValue = min(_lvalid)
                    avgValue = round(numpy.average(_lvalid), 3)

                    for eachkey in _d:
                        if _d.get(eachkey) == maxValue:
                            maxKeyName = eachkey
                        if _d.get(eachkey) == minValue:
                            minKeyName = eachkey
                    self.dataDict.update(
                            **{
                                    'maxSOCZelleName': maxKeyName,
                                    'maxSOCZelleValue': maxValue,
                                    'minSOCZelleName': minKeyName,
                                    'minSOCZelleValue': minValue,
                                    'avgSOCZelleValue': avgValue,
                                    'deltaSOCZelle_MaxMin': round(maxValue - minValue, 3),
                                    'deltaSOCZelle_AvgMin': round(avgValue - minValue, 3)
                            }
                    )

        def readVoltageZelleLimit():

            _d = {}
            _l = []

            for contentPiece in self.content_piece_list:
                if 'HVS_01 | STATUS_LESEN | ARG;ZELLSPANNUNGEN_AKTUELL' in contentPiece:
                    _lines = contentPiece.split('\n')
                    for _line in _lines[1:]:
                        try:
                            keyName = re.search('STAT_ZELLSPANNUNG_\d+_WERT', _line).group()
                            theValue = re.search('(?<= ).+(?= V)', _line).group()
                            _d[keyName] = float(theValue)
                            _l.append(float(theValue))
                        except Exception as error:
                            # print(error, _line)
                            continue
                    _lValid = [_v for _v in _l if _v < 10]
                    maxValue = max(_lValid)
                    minValue = min(_lValid)
                    avgValue = round(numpy.average(_lValid), 3)

                    for eachkey in _d:
                        if _d.get(eachkey) == maxValue:
                            maxKeyName = eachkey
                        if _d.get(eachkey) == minValue:
                            minKeyName = eachkey

                    self.dataDict.update(
                            **{
                                    'maxVoltageZelleName': maxKeyName,
                                    'maxVoltageZelleValue': maxValue,
                                    'minVoltageZelleName': minKeyName,
                                    'minVoltageZelleValue': minValue,
                                    'avgVoltageZelleValue': avgValue,
                                    'deltaVoltageZelle_MaxMin': round(maxValue - minValue, 3),
                                    'deltaVoltageZelle_AvgMin': round(avgValue - minValue, 3),
                            }
                    )

        if self.content == '':
            raise ValueError('No content loaded.')
        else:
            self.content_piece_list = re.split(r'-{10,1000}\n', self.content)
            readCellLimitVoltage()
            readSOCZelleLimit()
            readVoltageZelleLimit()


class Tester:
    SOURCE_PATH = R'D:\checkin_files'
    R = []

    def startTest(self):

        for file in os.listdir(self.SOURCE_PATH):
            file_path = os.path.join(self.SOURCE_PATH, file)
            try:
                _c = CheckinFile(file_path)
                _c.readVehicleData()
                _c.readSoftwareIdData()
                _c.readErrorMemorry()
                _c.readCheckControlMessage()
                self.R.append(_c)
            except Exception as e:
                lg.warning(f'{e}_{file_path}')
                input()
                continue


if __name__ == '__main__':
    # T=Tester()
    # T.startTest()
    c = CheckinFile(
            r"C:\00_MyFolder\02_Programming\02_Projects\checkinfile\bev\2022.08.01\6_car_daily\1A04107_20220801_105602_G028_S18A-22-03-563_CheckIN.TXT"
    )
    c.read_all()
