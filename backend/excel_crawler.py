import xlrd
import re
from xlrd.biffh import XLRDError

RE_RULE = r'[\u4e00-\u9fa5\d\(\)\uff08\uff09]+'

class ExcelCrawler:
    def __init__(self, loc=''):
        self.loc = loc
        try:
            self.wb = xlrd.open_workbook(loc, formatting_info=True)
            self.tb = self.wb.sheets()[0]
            self.data_start_index = 0
            self.table_name = self.tb.cell_value(0,0)
            self.colnames = self.__col_name_crawl()
            self.rownames = self.__row_name_crawl()
        except XLRDError:
            raise Exception(f'Wrong file formatting: {self.loc}')

    def set_loc_and_reload(self, loc):
        self.__init__(loc=loc)

    def __is_top_lined(self, rx, cx):
        return self.wb.xf_list[self.tb.cell_xf_index(rx, cx)].border.top_line_style != 0 or \
            self.wb.xf_list[self.tb.cell_xf_index(rx-1, cx)].border.bottom_line_style != 0

    def __is_bottom_lined(self, rx, cx):
        return self.wb.xf_list[self.tb.cell_xf_index(rx, cx)].border.bottom_line_style != 0 or \
            self.wb.xf_list[self.tb.cell_xf_index(rx+1, cx)].border.top_line_style != 0

    def __is_right_lined(self, rx, cx):
        return cx == self.tb.ncols-1 or (self.wb.xf_list[self.tb.cell_xf_index(rx, cx)].border.right_line_style != 0 or \
            self.wb.xf_list[self.tb.cell_xf_index(rx, cx+1)].border.left_line_style != 0)

    def __is_left_lined(self, rx, cx):
        return cx == 0 or (self.wb.xf_list[self.tb.cell_xf_index(rx, cx)].border.left_line_style != 0 or \
            self.wb.xf_list[self.tb.cell_xf_index(rx, cx-1)].border.right_line_style != 0)
    
    def __col_name_crawl(self):
        merged_cells = {}
        for rx in range(self.tb.nrows):
            if self.wb.xf_list[self.tb.cell_xf_index(rx,0)].background.pattern_colour_index == 44:
                level_cell_colx_list = []
                for cx in range(self.tb.ncols):
                    if self.__is_bottom_lined(rx, cx):
                        level_cell_colx_list.append(cx)
                curr_merged = []
                for _ in level_cell_colx_list[::-1]:
                    curr_merged.append(level_cell_colx_list[0])
                    del level_cell_colx_list[0]
                    if self.__is_right_lined(rx, curr_merged[-1]):
                        if not self.__is_left_lined(rx, curr_merged[0]):
                            curr_merged.insert(0,curr_merged[0]-1)
                            if not merged_cells.get(str(curr_merged[0])):
                                rx_ = rx
                                merged_name = ''
                                while True:
                                    merged_name = str((self.tb.cell_value(rx_, curr_merged[0]) if self.tb.cell_type(rx_, curr_merged[0]) != 2 else round(self.tb.cell_value(rx_, curr_merged[0])))) + merged_name
                                    if self.__is_top_lined(rx_, curr_merged[0]):
                                        break
                                    rx_ -= 1
                                rx_ = rx
                                while True:
                                    merged_name = merged_name + str((self.tb.cell_value(rx_, curr_merged[0]) if self.tb.cell_type(rx_, curr_merged[0]) != 2 else round(self.tb.cell_value(rx_, curr_merged[0]))))
                                    if self.__is_bottom_lined(rx_, curr_merged[0]):
                                        break
                                    rx_ = rx_ + 1
                                merged_name = ''.join(re.findall(RE_RULE, merged_name))
                                curr_merged_ = tuple(curr_merged)
                                merged_cells_ = list(merged_cells)
                                merged_cells_.reverse()
                                for mcell in merged_cells_:
                                    if set(curr_merged_).issubset(set(mcell)):
                                        merged_name = merged_cells[mcell] + merged_name
                                        break
                                merged_cells[tuple(curr_merged[0:1])] = merged_name
                                merged_cells[curr_merged_] = merged_name
                        elif not merged_cells.get(str(curr_merged[0])):
                            rx_ = rx
                            merged_name = ''
                            while True:
                                merged_name = str((self.tb.cell_value(rx_, curr_merged[0]) if self.tb.cell_type(rx_, curr_merged[0]) != 2 else round(self.tb.cell_value(rx_, curr_merged[0])))) + merged_name
                                if self.__is_top_lined(rx_, curr_merged[0]):
                                    break
                                rx_ -= 1
                            merged_name = ''.join(re.findall(RE_RULE, merged_name))
                            curr_merged_ = tuple(curr_merged)
                            merged_cells_ = list(merged_cells)
                            merged_cells_.reverse()
                            for mcell in merged_cells_:
                                if set(curr_merged_).issubset(set(mcell)):
                                    merged_name = merged_cells[mcell] + merged_name
                                    break
                            merged_cells[curr_merged_] = merged_name
                        curr_merged.clear()
            if self.wb.xf_list[self.tb.cell_xf_index(rx,0)].background.pattern_colour_index == 43:
                self.data_start_index = rx
                break
        merged_cells_ = list(merged_cells)
        for _ in merged_cells_:
            if {0}.issubset(set(_)) or len(_) > 1:
                del merged_cells[_]
        return merged_cells
    
    def __row_name_crawl(self):
        row_names = {}
        for cx in list(self.colnames):
            cx_ = cx[0]
            for rx in range(self.data_start_index, self.tb.nrows):
                if self.tb.cell_type(rx, cx_) == 2 and row_names.get(rx) is None:
                    row_name = ''.join(re.findall(RE_RULE, str(self.tb.cell_value(rx, 0) if self.tb.cell_type(rx, 0) != 2 else round(self.tb.cell_value(rx, 0)))))
                    row_names[rx] = row_name
        return row_names