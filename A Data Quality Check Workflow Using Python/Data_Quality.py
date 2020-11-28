# -*- coding: utf-8 -*-
"""
@author: alezanper
"""

import pandas as pd 
import itertools
import os


class Rules:  
    
    encoding = 'iso-8859-1'    
    counter = 0             # Size of dataFrame
    goods = False           # False for return bad registers
    delimiter = ','         # Default delimiter
    parts = []              # part from split function
    
    
    """
    initializing the class
    """
    def __init__(self, filename, delimiter, goods):
        self.goods = goods
        self.delimiter = delimiter
        self.parts = self.split(filename, 50)   
        

    """
    Close class and remove data
    """
    def close(self):
        for i in range(len(self.parts)):
            os.remove(self.parts[i])
        self.parts = []
    
    """
    It takes a filename and returns a dataframe
    """
    def getDataFrame(self, filename):
        data = pd.read_csv(filename,
                       delimiter = self.delimiter,
                       encoding = self.encoding)
        return data

    
    """
    Split a big file into small files
    """
    def split(self, filename, numLines):
        parts = []
        with open(filename, encoding = self.encoding) as f:
            file = f.readlines()
            size = len(file)
            
            for i in range(int(size/numLines)+1):
                with open('part_' + str(i) + '_' + filename, "w", encoding = self.encoding) as csv:
                    parts.append('part_' + str(i) + '_' + filename)
                    csv.write(''.join(list(itertools.islice(file, 0, 1))))
                    csv.write(''.join(list(itertools.islice(file, 1, numLines)))) if (i == 0) else csv.write(''.join(list(itertools.islice(file, numLines*i, numLines + numLines*i))))
        return parts
         
    
    """
    Checking for null values
    """        
    def checkNull(self, columnToAnalize):
        data = pd.DataFrame()
        
        for i in range(len(self.parts)):
            dataPart = self.getDataFrame(self.parts[i])            
            data = data.append(
                    dataPart[dataPart[columnToAnalize].isna()== (not self.goods)]
                    )
        return data.reset_index()
    

    """
    Checking for pattern
    """
    def checkPattern(self, columnToAnalize, pattern):    
        data = pd.DataFrame()

        for i in range(len(self.parts)):
            dataPart = self.getDataFrame(self.parts[i])            
            data = data.append(
                    dataPart[dataPart[columnToAnalize].astype(str).str.contains(pattern, regex = True) 
                         == self.goods].append(dataPart[dataPart[columnToAnalize].isna()
                         == (not self.goods)])
                    )   
        return data.reset_index()
    
    
    """
    Checking for email structure
    includes a simple pattern that could be updated according needs
    """
    def checkEmail(self, columnToAnalize):
        return self.checkPattern(columnToAnalize, '[\w]+@[\w]+.com')
    
    
    """
    Checking for names
    includes a simple pattern for checking names with only letters
    """
    def checkName(self, columnToAnalize):
        return self.checkPattern(columnToAnalize, '^[A-Za-zñÑÁÉÍÓÚáéíóú]+$')
    

    """
    Checking for numbers
    includes a simple pattern for checking numbers
    """
    def checkNumber(self, columnToAnalize):
        return self.checkPattern(columnToAnalize, '^[0-9]+\.?[0-9]*$')
    
    
    """
    Checking for specific word in a field
    """
    def checkContains(self, columnToAnalize, wordToFind):
        data = pd.DataFrame()

        for i in range(len(self.parts)):
            dataPart = self.getDataFrame(self.parts[i])            
            data = data.append(
                    dataPart[dataPart[columnToAnalize].astype(str).str.contains(wordToFind) 
                         == self.goods])
                       
        return data.reset_index()
    
    
    """
    Checking for data in list reference
    """
    def checkListReference(self, listname, listColumn, columnToAnalize):   
        data = pd.DataFrame()

        listref = pd.read_csv(listname,
                       delimiter = self.delimiter,
                       encoding = self.encoding)
        
        for i in range(len(self.parts)):
            dataPart = self.getDataFrame(self.parts[i])            
            data = data.append(
                    dataPart[dataPart[columnToAnalize].isin(list(listref[listColumn]))
                         == self.goods]
                    )  
        
        return data.reset_index()
    

    """
    Checking length
    """
    def checkMaxLength(self, columnToAnalize, length):   
        data = pd.DataFrame()
        
        for i in range(len(self.parts)):
            dataPart = self.getDataFrame(self.parts[i])    
            if(self.goods):
                data = data.append(
                        dataPart[dataPart[columnToAnalize].
                                        astype(str).str.len() <= length])
            else:
                data = data.append(
                        dataPart[dataPart[columnToAnalize].
                                        astype(str).str.len() >= length])
        
        return data.reset_index()
    

#    """
#    Checking for unicity
#    """
#    def checkUnity(self, columnToAnalize, maxRepeated):
#        #Checking for null values
#        if(self.goods):
#            return self.data.groupby(columnToAnalize).filter(lambda x: len(x) == 1)
#        else:
#            return self.data.groupby(columnToAnalize).filter(lambda x: len(x) > maxRepeated)
                
        
    """
    For cleaning data
    This is a native function in Pandas adapted for use in large files.
    """
    def removeReplace(self, columnToImprove, bad, good):   
        data = pd.DataFrame()
        
        for i in range(len(self.parts)):
            dataPart = self.getDataFrame(self.parts[i])               
            dataPart[columnToImprove] = dataPart[columnToImprove].str.replace(bad, good)
            data = data.append(dataPart)        
        return data.reset_index()  