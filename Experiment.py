import gzip
import os
import time
import csv
import unittest
import sys
from typing import List
from datetime import datetime, timedelta
from Shrink.TimeSeriesReader import TimeSeriesReader
from Shrink.Shrink import Shrink
from Shrink.Point import Point
from Shrink.utilFunction import *
import QuanTRC
path = '../Data/'





class TestSHRINK(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        """
        The initial function of the class
        Parameters:
        """
        super().__init__(*args, **kwargs)
        self.duration = 0
        self.tsDecompressed = None
        self.decompBaseTime = 0
        self.decompResTime = 0



    def Assert(self, shrink, epsilonPct, ts):
        """
        Decompress the data into Base and residual, and assert the values are within the error threshold
        Parameters:
            - shrink: the algorithm
            - epsilonPct: current epsilon for compression
            - ts: the time series data
        """
        idx = 0
        self.tsDecompressed, self.decompBaseTime  = shrink.decompress()
        Dequant_val, self.decompResTime  = shrink.residualDecode(outputPath='../Data/Compressed/residuals', epsilon = epsilonPct)

        for expected in self.tsDecompressed:
            actual = ts.data[idx]
            approximateVal = expected.value + Dequant_val[idx]
            if expected.timestamp != actual.timestamp:
                continue
            if(epsilonPct==0):
                #也可以用1e-10,即认为相等sys.float_info.epsilon
                self.assertAlmostEqual(actual.value, approximateVal, delta=1e-10, msg="Value did not match for timestamp " + str(actual.timestamp))
            else:
                self.assertAlmostEqual(actual.value, approximateVal, delta=epsilonPct, msg="Value did not match for timestamp " + str(actual.timestamp))
            idx += 1


        self.assertEqual(idx, len(ts.data))

    
    def run(self, filenames: List[str], epsilons, BaseEpsilons) -> None:
        """
        The entrance function to extact base and residuals for datasets
        Parameters:
            - filenames: list of the files
            - epsilons: list of the desired epsilon for compression
        """
        
        for idx, filename in enumerate(filenames):
            # 0. Set Base error
            BaseEpsilon = BaseEpsilons[filenames.index(filename)]
            if(idx==0): print(f"Shrink: BaseEpsilon = {BaseEpsilon}")

            # 1. Read dataset
            ts = TimeSeriesReader.getTimeSeries(path+filename)
            ts.size = os.path.getsize(path+filename)           ## use the size of .csv. If using bit size, comment this. 
            print(f"{filename}: {ts.size/1024/1024:.2f}MB")
            
             # 2. Extract Base 
            shrink = Shrink(points=ts.data, epsilon=BaseEpsilon)
            binary = shrink.toByteArray(variableByte=False, zstd=False)
            origibaseSize = shrink.saveByte(binary, filename)

            # 3. Entropy coding for Base 
            inpath = '../Data/Compressed/Base/'+filename[:-7]+"_Base.bin"
            outputPath = '../Data/Compressed/Base/'
            QuanTRC.compress(inpath,outputPath)
            baseTime = int(shrink.baseTime)
            baseSize = os.path.getsize('../Data/Compressed/Base/codes.rc')

            # 4. Get Residuals 
            residuals = shrink.getResiduals()

            # 5. Encoding for different epsilons
            meanCR, meanResCR = 0, 0
            meanCompreTime, meanDecTime, decBasetime  = baseTime, 0, 0
            decBase= False
            for epsilonPct in epsilons:
                if (epsilonPct>=BaseEpsilon):
                    print(f"Epsilon: {epsilonPct }\tCompression Ratio: {ts.size/baseSize :.5f}\t Residual CR: {0}\tCompress Time: {baseTime}ms\t Decompress Time: {decBasetime} + {self.decompResTime} = {self.decompBaseTime +self.decompResTime}ms  \tRange: {ts.range :.3f}")
                    print(f"baseSize: {baseSize/1024 :.3f}KB \t Size of residual: {0}KB \t origibaseSize: {origibaseSize/1024}KB")
                    # meanCR += baseSize/ ts.size
                    meanCR += ts.size/baseSize
                    meanResCR += 0
                    meanTime += 0
                    meanDec += 0
                    continue

                residualSize = shrink.residualEncode(residuals, epsilonPct)
                residualTime = shrink.residualTime

                compressedSize = baseSize + residualSize
                ResidualCR = ts.size/residualSize
                CR =  ts.size/ compressedSize

                if(decBase==False):   # To decompress the Base only one,we should assert error is bounded with current errorthreshold epsilonPct
                    self.Assert(shrink, epsilonPct, ts)
                    decBase = True
                    decBasetime = self.decompBaseTime

                print(f"Epsilon: {epsilonPct }\tCompression Ratio: {CR:.5f} \t baseSize: {baseSize/1024 :.3f}KB \t residualSize: {residualSize/1024 :.3f}KB \tCompress Time: {baseTime} + {residualTime} = {baseTime + residualTime}ms\t Decompress Time: {decBasetime} + {self.decompResTime} = {self.decompBaseTime +self.decompResTime}ms")

                meanCR += CR
                meanResCR += ResidualCR
                meanCompreTime += residualTime
                meanDecTime += self.decompResTime

            meanCompreTime, meanDecTime = meanCompreTime/len(epsilons), (meanDecTime+self.decompBaseTime)/len(epsilons)
            meanCR, meanResCR = meanCR/len(epsilons), meanResCR/len(epsilons)
            print(f"The average compresstime: {meanCompreTime:.1f}ms \n")


    def main(self) -> None:
        """
        The main function of the whole project
        Parameters:
            None
        """
        filenames    =  ["FaceFour.csv", "MoteStrain.csv", "Lightning.csv",]
        BaseEpsilons =  [ 0.525,          0.85,             1.235,]
        epsilons     =  [0.01, 0.0075, 0.005, 0.0025, 0.001, 0.00075, 0.0005, 0.00025, 0.0001]
        self.run(filenames, epsilons, BaseEpsilons)



if __name__ ==  '__main__':
    test = TestSHRINK()
    test.main()