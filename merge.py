# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    merge.py                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: ecross <marvin@42.fr>                      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2020/03/17 16:55:24 by ecross            #+#    #+#              #
#    Updated: 2020/03/18 18:07:11 by ecross           ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import xlrd
import os
import shutil
from mailmerge import MailMerge

class Merge:
    
    copy_list = []
    merge_list = []
    
    def __init__(self, ref):
        self.ref = ref
        #needs changing to current dir
        dst_root = '../'
        for dirs in os.listdir(dst_root):
            if dirs.startswith(self.ref):
                path = dst_root + dirs
                self.find_workbook(path)
                self.find_dst_path(path)
        if self.dst == None or self.workbook == None:
            exit()
    
    def find_dst_path(self, path):
        for dirs in os.listdir(path):
            if dirs.startswith('HOP'):
                self.dst = os.path.join(path, dirs)
                return
        self.dst = None
        print('Could not find output location. Please check job number\
                is correct, and that it\'s folder exists in \'Sales\'')
    
    def find_workbook(self, path):
        for dirs in os.listdir(path):
            if dirs.startswith('Install'):
                path = os.path.join(path, dirs)
                for files in os.listdir(path):
                    if files.endswith('xlsx'):
                        with xlrd.open_workbook(os.path.join(path, files), on_demand = True) as workbook:
                            self.workbook = workbook
                        return
        self.workbook = None
        print('Could not find installation spreadsheet.')

    def get_col(self, sheet, title):
        i = 0
        for x in sheet.row(0):
            if x.value == title:
                return (i)
            i += 1
        return 0

    def fill_lists(self):
        sheet = self.workbook.sheet_by_name('HOP Merge')
        infile_col = get_col(sheet, 'Input Doc')
        outfile_col = get_col(sheet, 'Output Doc')
        i = 0
        for x in sheet.col(infile_col):
            if x.value != xlrd.empty_cell.value:
                #need to check on positions and directions of strokes
                src_folder = str(sheet.cell(i, infile_col - 1).value)
                if src_folder[len(src_folder) - 1] != '/':
                    src_folder += '/'
                if self.dst[len(self.dst) - 1] != '/':
                    self.dst += '/'
                #might need to return to a pair with path of each, if complete destination
                #file name is provided in spreadsheet
                tup = (src_folder, str(sheet.cell(i, infile_col).value), self.dst, str(sheet.cell(i, outfile_col).value))
                if sheet.cell(i, ind + 1).value == 'Copy':
                    self.copy_list.append(tup)
                if sheet.cell(i, ind + 1).value == 'Merge':
                    self.merge_list.append(tup)
            i += 1

    def copy_files(self):
        for tup in self.copy_list:
            shutil.copy(tup[0] + tup[1], tup[2] + tup[3])

    def make_merges(self):
        
        def get_value(key, sheet):
            i = 0
            for x in sheet.row(0):
                if key == x.value:
                    return str(sheet.cell(1, i).value)
                i += 1

        for doc in self.merge_list:
            with MailMerge(doc[0] + doc[1]) as document:
                mydict = {}
                merge_fields = document.get_merge_fields()
                for f in merge_fields:
                    mydict[f] = get_value(f.replace('_', ' '), self.workbook.sheet_by_name('A Merge Data'))
                first_space = doc[1].index(' ')
                document.merge(**mydict)
                document.write(doc[2] + doc[3][:first_space] + ' ' + self.ref +  doc[3][first_space:])
                print('merged doc------>')
                print(doc[2] + doc[3][:first_space] + ' ' + self.ref +  doc[3][first_space:])
 
#object with:
#   workbook as openened by xlrd
#   string containing the job ref
#   two lists of tuples, containing:
#       (src folder, src file name, dest folder, dest file name)
#   for files to be copied and those to be merged
#   method to fill lists
#   method to copy files using copy_list
#   method to make merges from merge_list


job = 'a'
while job.isdigit() == False:
    job = input('Please enter 4 digits of job number here: TL')
merge_obj = Merge('TL' + job)
merge_obj.fill_lists()
merge_obj.copy_files()
merge_obj.make_merges()
