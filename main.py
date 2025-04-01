from SM4 import *

if __name__ == "__main__":

    # inputData = input('Input string or file location need to calculate sm3(press ENTER to abort): ')
    # inputKey = input('Input 128 bits secret key in hex (like \'0123456789abcdef0123456789abcdef\', input nothing to abort): ')
    inputData = b"\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10"
    inputKey = "0123456789abcdeffedcba9876543210"
    # try:
    #     if inputData and len(inputKey) == 32:
    #         print('SM4 encode result: ', sm4_encode(inputData, int(inputKey, 16)))
    #     else:
    #         print("Check input data.")
    # except ValueError:
    #     print("Check input data.")
    # if inputData and len(inputKey) == 32:
    #     print('SM4 encode result: ', sm4_encode(inputData, int(inputKey, 16)))
    # else:
    #     print("Check input data.")

    for i in range(0, 1000000):
        if i % 10000 == 0:
            print(i)
        inputData = sm4_encode(inputData, int(inputKey, 16))
    print(inputData.hex())