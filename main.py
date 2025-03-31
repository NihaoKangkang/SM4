from SM4 import *

if __name__ == "__main__":

    # inputData = input('Input string or file location need to calculate sm3(press ENTER to abort): ')
    # inputKey = input('Input key in hex (16 byte like \'0123456789abcdef0123456789abcdef\', input nothing to abort): ')
    inputData = "0123456789abcdeffedcba9876543210"
    inputKey = "0123456789abcdeffedcba9876543210"
    if inputData and len(inputKey) == 32:
        print('SM4 result: ', sm4_result(inputData, inputKey))
    else:
        print("Check input data.")