import numpy as np
from timeit import default_timer as timer
from scipy.interpolate import interp1d
import os
import csv
import time 

'''
Loads a dataset in for compression, data is assumed
to be a numpy array. Normalizes the data between 0 and
1 automatically. 
'''
def load(data):
    compression_stats = {}
    start = timer()

    #store the variables
    data = data.copy()
    N,p = data.shape

    normalization = np.vstack([np.max(data,axis=0), np.min(data,axis=0)])
    normalization = np.hstack([normalization, np.array([N, p]).reshape(2,1)])

    #print(self.normalization.shape)
    #get all attrs between 0 and 1
    for i in range(p):
        data[:,i] = (data[:,i] - normalization[1,i])/(normalization[0,i] - normalization[1,i])

    NORMALIZATION += '.npy'
    np.save(NORMALIZATION, normalization)
    compression_stats['load_time'] = timer() - start
    compression_stats['original_size'] = data.size * data.itemsize

    return compression_stats

def compress(InFilePath, outputPath=""):
    TURBO_CODE_LOCATION = "Turbo-Range-Coder/turborc"
    TURBO_CODE_PARAMETER = "20"
    trc_flag = '-' + TURBO_CODE_PARAMETER
    CODES = outputPath + '/codes'

    command = " ".join(['./Turbo-Range-Coder/turborc', trc_flag, InFilePath, CODES])
    #print("command: ", command)
    os.system(command)

def decompress(compressedPath, decompressedPath):
    command = " ".join(['./Turbo-Range-Coder/turborc', "-d", compressedPath, decompressedPath])
    #print("command: ", command)
    os.system(command)

def Calculate_CR(originalFile, compressedFile):
    #print("Original size: ", os.path.getsize(originalFile))
    #print("CompressedSize", os.path.getsize(compressedFile))
    return os.path.getsize(compressedFile)/os.path.getsize(originalFile)

def EqualOrNot(file1_path, file2_path):
    # 创建两个空列表来存储文件中的数据
    data1 = []
    data2 = []

    # 打开第一个CSV文件，读取数据并存储到data1列表中
    with open(file1_path, mode='r', newline='') as file1:
        csv_reader = csv.reader(file1)
        for row in csv_reader:
            data1.append(float(row[0]))

    # 打开第二个CSV文件，读取数据并存储到data2列表中
    with open(file2_path, mode='r', newline='') as file2:
        csv_reader = csv.reader(file2)
        for row in csv_reader:
            data2.append(float(row[0]))

    # 比较两个列表是否相同
    if data1 == data2:
        print("The two files are Equal")
    else:
        print("The two files are Not Equal")

        # 查找并指示前10个不相等的行的行号和值
        num_differences = 0
        for i in range(min(len(data1), len(data2))):
            if data1[i] != data2[i]:
                num_differences += 1
                print(f"行号 {i + 1}: 值为 {data1[i]} (文件1) 和 {data2[i]} (文件2)")
                if num_differences >= 10:
                    break



if __name__ == '__main__':
    InFilePath = '/home/guoyou/Lossless/data/'
    InFilePath = "/home/guoyou/ExtractSemantic/Data/Test/"

    outputPath = '/home/guoyou/Lossless/data/code'
    filenames = ["Cricket.csv","FaceFour.csv", "Lightning.csv", "MoteStrain.csv", "Wafer.csv", "WindSpeed.csv", "WindDirection.csv", "Pressure.csv"]

    InFilePath = "/home/guoyou/ExtractSemantic/Base/"
    filenames = ["WindSpeed_Base.bin", "WindDirection_Base.bin", "Ecg_Base.bin", "Wafer_Base.bin", "Pressure_Base.bin"]
                

    InFilePath = "/home/guoyou/ExtractSemantic/Base/"
    filenames = ["active_power_Base.bin"]
    
    InFilePath = "/home/guoyou/Simpiece/segments/"
    filenames = ["segments.bin"]

    InFilePath = "/home/guoyou/ExtractSemantic/residuals/"
    filenames = ["codes.rc"]

    InFilePath = "/home/guoyou/Lossy/HIRE/testdataset/"
    filenames = ["Cricket.npy"]

    for filename in filenames:
        print(filename)
        start_time = time.time() 
        compress(InFilePath+filename, outputPath)
        end_time = time.time()
        duration = int((end_time - start_time) * 1000)

        sourceSize = os.path.getsize(InFilePath+filename)
        compressSize = os.path.getsize('/home/guoyou/Lossless/data/code/codes.rc')
        print(f"Original size: {sourceSize/1024}KB  CompressedSize: {compressSize/1024}KB")
        print("Compression ratio: ", Calculate_CR(InFilePath+filename, '/home/guoyou/Lossless/data/code/codes.rc'), f"  Execution Time: {duration}ms ")
    
        start_time = time.time()
        decompress(outputPath+ '/codes'+'.rc', outputPath+"/Neworginal"+'.csv')
        end_time = time.time()
        decompResTime = int((end_time - start_time) * 1000)
        print(f"Time of decompressing: {decompResTime:.2f}")
        print()

        #EqualOrNot("/home/guoyou/Lossless/residuals.csv", "/home/guoyou/Lossless/Neworginal.csv")