from SM4 import *

if __name__ == "__main__":

    inputData = input('Input text,hex data or file location need to calculate sm4(press ENTER to abort): ')
    # inputKey = input('Input 128 bits secret key in hex (like \'0123456789abcdef0123456789abcdef\', input nothing to abort): ')
    # 因为示例为16进制字符串，所以这边进行了byte流输出，实际输入应当为string
    # inputData = b"\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10"
    # inputData = "681edf34d206965e86b3e94f536e4246"
    # Same Key
    inputKey = "0123456789abcdeffedcba9876543210"
    try:
        if inputData and len(inputKey) == 32:
            encodeFlag = input("Do you want to encode(y)/decode(n) this data?(Y/n): ")
            if encodeFlag == 'y' or encodeFlag == 'Y' or encodeFlag == '':
                print('SM4 encode result: ', sm4_encode(inputData, int(inputKey, 16)).hex())
            else:
                print('SM4 decode result: ', sm4_decode(inputData, int(inputKey, 16)))
        else:
            print("Check input data.")
    except ValueError:
        print("Check input data.")







    # 加密部分
    # if inputData and len(inputKey) == 32:
    #     print('SM4 encode result: ', sm4_encode(inputData, int(inputKey, 16)).hex())
    # else:
    #     print("Check input data.")

    # for i in range(0, 1000000):
    #     if i % 10000 == 0:
    #         print(i)
    #     inputData = sm4_encode(inputData, int(inputKey, 16))
    # print(inputData.hex())

    # 解密测试
    # inputData = "681edf34d206965e86b3e94f536e4246"
    # inputKey = "0123456789abcdeffedcba9876543210"
    # if inputData and len(inputKey) == 32:
    #     print('SM4 encode result: ', sm4_decode(inputData, int(inputKey, 16)).hex())
    # else:
    #     print("Check input data.")

    # 1m times decode testing.
    # inputData = "595298c7c6fd271f0402f804c33d3f66"
    # inputKey = "0123456789abcdeffedcba9876543210"
    # for i in range(0, 1000000):
    #     if i % 10000 == 0:
    #         print(i)
    #     inputData = sm4_decode(inputData, int(inputKey, 16)).hex()
    # print(inputData)