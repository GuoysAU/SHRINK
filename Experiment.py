from typing import List
import gzip
import sys
import os
import time
import csv
import unittest
import sys
from datetime import datetime, timedelta
from Shrink.TimeSeriesReader import TimeSeriesReader
from Shrink.Shrink import Shrink
from Shrink.Point import Point
from Shrink.utilFunction import *
from Shrink.Transform import Transform
from Shrink.Transform import DeTransform

import QuanTRC
import faulthandler

faulthandler.enable()
sys.path.append('/home/guoyou/ExtractSemantic/Data/')
path = '/home/guoyou/ExtractSemantic/Data/'
# path = "/home/guoyou/SHRINK/ProjectDataAnalysis/" ### for file Tool1Merge.csv

# path = "/home/guoyou/DataMine/" ### for testing TSB-UAD$
# path = "/home/guoyou/SHRINK/OutlierDection/"




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
        self.BaseEpsilon = 0.5 
        self.BaseEpsilon = 0.05 ### for testing TSB-UAD$
        self.BaseEpsilon = 1000 ### for testing Tool1Merge.csv
        self.BaseEpsilon = 0.03125



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
        Dequant_val, self.decompResTime  = shrink.residualDecode(outputPath='/home/guoyou/ExtractSemantic/residuals', epsilon = epsilonPct)

        # 指定CSV文件名 epsilons = [10] BaseEpsilon = 1000
        filename = "BaseTool1Fres.csv"
        values = [p.value for p in self.tsDecompressed]
        with open(path+filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            for value in values:
                writer.writerow([value])
        values.clear()
        # print(f"{filename} 文件已保存。")

        for expected in self.tsDecompressed:
            actual = ts.data[idx]
            approximateVal = expected.value + Dequant_val[idx]
            values.append(approximateVal)
            if expected.timestamp != actual.timestamp:
                continue
            if(epsilonPct==0):
                #也可以用1e-10,即认为相等sys.float_info.epsilon
                self.assertAlmostEqual(actual.value, approximateVal, delta=1e-7, msg="Value did not match for timestamp " + str(actual.timestamp))
            else:
                self.assertAlmostEqual(actual.value, approximateVal, delta=epsilonPct, msg="Value did not match for timestamp " + str(actual.timestamp))
            idx += 1

        # 指定CSV文件名 epsilons = [10] BaseEpsilon = 1000
        filename = "Decom_Tool1Fres.csv"
        with open(path+filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            for value in values:
                writer.writerow([value])
        values.clear()
        # print(f"{filename} 文件已保存。")

        self.assertEqual(idx, len(ts.data))

    
    def run(self, filenames: List[str], epsilons) -> None:
        """
        The entrance function to extact base and residuals for datasets
        Parameters:
            - filenames: list of the files
            - epsilons: list of the desired epsilon for compression
        """
        print(f"Shrink: BaseEpsilon = {self.BaseEpsilon}")
        for filename in filenames:
            ts = TimeSeriesReader.getTimeSeries(path+filename)
            ts.size = os.path.getsize(path+filename)           #取CSV的大小
            print(f"{filename}: {ts.size/1024/1024:.2f}MB")
            
                
            shrink = Shrink(points=ts.data, epsilon=self.BaseEpsilon)
            # representatives = Transform(shrink)
            # indexs, points = DeTransform(representatives)
            binary = shrink.toByteArray(variableByte=False, zstd=False)
            origibaseSize = shrink.saveByte(binary, filename)
            print("origibaseSize = ", origibaseSize/1024/1024)
            inpath = '/home/guoyou/ExtractSemantic/Base/'+filename[:-7]+"_Base.bin"
            outputPath = '/home/guoyou/ExtractSemantic/Base/'
            QuanTRC.compress(inpath,outputPath)
            baseTime = int(shrink.baseTime * 1000)
            baseSize = os.path.getsize('/home/guoyou/ExtractSemantic/Base/codes.rc')
            # baseSize = origibaseSize

            residuals = shrink.getResiduals()

            meanCR, meanResCR = 0, 0
            meanCompreTime, meanDecTime, decBasetime  = baseTime, 0, 0
            decBase= False
            for epsilonPct in epsilons:
                if (epsilonPct>=self.BaseEpsilon):
                    print(f"Epsilon: {epsilonPct }\tCompression Ratio: {ts.size/baseSize :.5f}\t Residual CR: {0}\tCompress Time: {baseTime}ms\t Decompress Time: {decBasetime} + {self.decompResTime} = {self.decompBaseTime +self.decompResTime}ms  \tRange: {ts.range :.3f}")
                    print(f"baseSize: {baseSize/1024 :.3f}KB \t Size of residual: {0}KB \t origibaseSize: {origibaseSize/1024}KB")
                    meanCR += baseSize/ ts.size
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
        epsilons = [0.01, 0.0075, 0.005, 0.0025, 0.001, 0.00075, 0.0005, 0.00025, 0.0001, 0.00001]
        filenames = ["FaceFour.csv", "MoteStrain.csv", "Lightning.csv", "Ecg.csv", "Cricket.csv",  
                    "WindDirection.csv", "Wafer.csv", "WindSpeed.csv",  "Pressure.csv"]   
        # epsilons = [10]     
        filenames = ["Tool1Fres.csv"]
        filenames = ["MoteStrain.csv", "FaceFour.csv",  "Ecg.csv"]

        epsilons = [0.01, 0.0075, 0.005, 0.0025, 0.001, 0.00075, 0.0005, 0.00025, 0.0001, 0.00001]
        filenames = ["Modified_005_UCR_Anomaly_DISTORTEDCIMIS44AirTemperature1_4000_5391_5392.csv"]
        filenames = ["MoteStrain.csv"]
        self.run(filenames, epsilons)



if __name__ ==  '__main__':
    test = TestSHRINK()
    test.main()
    print("Congratulation! All test have passed!")