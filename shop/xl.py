#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import xlrd

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                import cElementTree as etree
            except ImportError:
                try:
                    import elementtree.ElementTree as etree
                except ImportError:
                    print("Failed to import ElementTree from any known place")
                    
class XL:
    
    sheet = None
    
    def __init__(self, xlfile):
        rb = xlrd.open_workbook(xlfile,formatting_info=True)
        self.sheet = rb.sheet_by_index(0)
        
    def xlsheet(self):
        return self.sheet
    
    def row(self, rownum):
        row = self.sheet.row_values(rownum)
        return row 
        
    def col(self, colnum):
        return self.sheet.col_values(colnum)
    
    def v(self, i, j):
        return self.sheet.cell(i,j).value
    
    def colbyname(self, name):
        
        for col_index in range(self.sheet.ncols):
            if self.sheet.cell(0, col_index).value == name:
                return self.sheet.col_values(col_index)
            
        return False
    
    def colmap(self):
        
        d = {}
        
        for col_index in range(self.sheet.ncols):
            d[self.sheet.cell(0, col_index).value] = col_index 
            
        return d
    
    def nrows(self):
        return self.sheet.nrows
        
            
        
    
                        