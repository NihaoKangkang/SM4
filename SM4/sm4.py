import numpy as np
from os.path import isfile
from tqdm import tqdm
from multiprocessing import Pool, shared_memory


FK = [0xA3B1BAC6, 0x56AA3350, 0x677D9197, 0xB27022DC]

CK = [0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269, 0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9, 0xe0e7eef5,
      0xfc030a11, 0x181f262d, 0x343b4249, 0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9, 0xc0c7ced5, 0xdce3eaf1,
      0xf8ff060d, 0x141b2229, 0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299, 0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed,
      0xf4fb0209, 0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279]

# len(SBox) = 256
# Sbox reference link: https://github.com/QingYun65/SM4-SBox-CompositeField/blob/master/result.txt
# Thank you.
SBox = [0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05, 0x2b, 0x67,
        0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86, 0x06, 0x99, 0x9c, 0x42, 0x50, 0xf4,
        0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed, 0xcf, 0xac, 0x62, 0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08,
        0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa, 0x75, 0x8f, 0x3f, 0xa6, 0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba,
        0x83, 0x59, 0x3c, 0x19, 0xe6, 0x85, 0x4f, 0xa8, 0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb,
        0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35, 0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25, 0x22, 0x7c, 0x3b,
        0x01, 0x21, 0x78, 0x87, 0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52, 0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4,
        0xc8, 0x9e, 0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38, 0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1,
        0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34, 0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3, 0x1d, 0xf6,
        0xe2, 0x2e, 0x82, 0x66, 0xca, 0x60, 0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f, 0xd5, 0xdb, 0x37, 0x45,
        0xde, 0xfd, 0x8e, 0x2f, 0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51, 0x8d, 0x1b, 0xaf, 0x92, 0xbb, 0xdd,
        0xbc, 0x7f, 0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8, 0x0a, 0xc1, 0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd,
        0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0, 0x89, 0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e, 0x65, 0xb9,
        0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84, 0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20, 0x79, 0xee, 0x5f, 0x3e,
        0xd7, 0xcb, 0x39, 0x48]


# 输入A: 4 byte int
# 输出b: 4 byte int
def tao(A):
    hexAString = format(A, "08x")
    a = [hexAString[:2], hexAString[2:4], hexAString[4:6], hexAString[6:]]
    # 按位替换
    B = 0
    for i in range(0, 4):
        temp = SBox[int(a[i], 16)]
        B += temp << ((3 - i) * 8)
    return B


def L_(data):
    B = tao(data)
    return B ^ ((B << 13 | B >> 19) & 0xffffffff) ^ ((B << 23 | B >> 9) & 0xffffffff)


def T_(data):
    return L_(data)


def L(data):
    B = tao(data)
    return B ^ ((B << 2 | B >> 30) & 0xffffffff) ^ ((B << 10 | B >> 22) & 0xffffffff) ^ (
            (B << 18 | B >> 14) & 0xffffffff) ^ ((B << 24 | B >> 8) & 0xffffffff)


def T(data):
    return L(data)


def F(xi, xi_1, xi_2, xi_3, rki):
    # print(f"{xi:08x}:{xi_1:08x}:{xi_2:08x}:{xi_3:08x}:{rki:08x}")
    t_temp = xi_1 ^ xi_2 ^ xi_3 ^ rki
    return xi ^ T(t_temp)


def R(X_32, X_33, X_34, X_35):
    return bytes.fromhex(f"{X_35:08x}{X_34:08x}{X_33:08x}{X_32:08x}")


def remove_padding_zeros(data):
    length = len(data)
    while length > 0 and data[length - 1] == 0x00:
        length -= 1
    return data[:length]


def process_block_shm(args):
    block_index, shm_name, total_length, block_size, rk = args
    # 打开共享内存
    shm = shared_memory.SharedMemory(name=shm_name)
    # 利用共享内存构建 numpy 数组，不会拷贝数据
    buf = np.ndarray((total_length,), dtype=np.uint8, buffer=shm.buf)
    start = block_index * block_size
    end = start + block_size
    # 提取当前块数据（转换为 bytes 后调用加密函数）
    block_data = bytes(buf[start:end])
    res = sm4_algorithm(block_data, rk)
    shm.close()
    return res


# data: 128 bit byte stream
# rkList: rk list
def sm4_algorithm(data, rkList):
    X = [int(data[:4].hex(), 16), int(data[4:8].hex(), 16), int(data[8:12].hex(), 16), int(data[12:].hex(), 16)]
    # X[4] = 27FAD345
    for i in range(0, 32):
        Xi_4 = F(X[i], X[i + 1], X[i + 2], X[i + 3], rkList[i])
        X.append(Xi_4)
        # print(f"X{i+4} = {X[i+4]:08x}")
    return R(X[32], X[33], X[34], X[35])


def sm4_file_encode(filename, key):
    # 轮密钥拓展
    keyHexString = format(key, "032x")
    MK = [int(keyHexString[:8], 16), int(keyHexString[8:16], 16), int(keyHexString[16:24], 16),
          int(keyHexString[24:], 16)]
    K = [MK[0] ^ FK[0], MK[1] ^ FK[1], MK[2] ^ FK[2], MK[3] ^ FK[3]]
    rk = []
    for i in range(0, 32):
        temp_K = K[i] ^ T_(K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i])
        K.append(temp_K)
        rk.append(temp_K)
    # 文件读写部分
    file_count = 0
    c_fname = filename + '_encoded' + format(file_count, '02d')
    while isfile(c_fname):
        file_count += 1
        c_fname = filename + '_encoded' + format(file_count, '02d')
    # 加密后文件名c_fname
    with open(filename, 'rb') as text_file:
        # 一次读取整个文件，然后补0 使得 len(filename) % 16 == 0
        byte_file = text_file.read()
    if len(byte_file) % 16 != 0:
        byte_file += b'\x00' * (16 - len(byte_file) % 16)
    total_length = len(byte_file)
    # 分块
    block_size = 16
    blockNumber = total_length // block_size
    # 创建共享内存，将整个文件数据写入共享内存，不会复制多份
    shm = shared_memory.SharedMemory(create=True, size=total_length)
    # 将文件内容拷贝到共享内存中
    shm_buf = np.ndarray((total_length,), dtype=np.uint8, buffer=shm.buf)
    shm_buf[:] = np.frombuffer(byte_file, dtype=np.uint8)
    # 构造参数列表，每个任务只传递共享内存名称和块索引
    args_list = [(i, shm.name, total_length, block_size, rk) for i in range(blockNumber)]
    with Pool() as pool:
        # imap 保证结果顺序与 args_list 顺序一致
        results = list(
            tqdm(pool.imap(process_block_shm, args_list), total=blockNumber, desc='encoding process:', unit='block'))
    # 合并所有加密块
    encodeMessage = b''.join(results)
    with open(c_fname, 'wb') as out_file:
        out_file.write(encodeMessage)
    # 释放共享内存
    shm.close()
    shm.unlink()
    return c_fname


def sm4_file_decode(filename, key):
    # 轮密钥拓展
    keyHexString = format(key, "032x")
    MK = [int(keyHexString[:8], 16), int(keyHexString[8:16], 16), int(keyHexString[16:24], 16),
          int(keyHexString[24:], 16)]
    K = [MK[0] ^ FK[0], MK[1] ^ FK[1], MK[2] ^ FK[2], MK[3] ^ FK[3]]
    rk = []
    for i in range(0, 32):
        temp_K = K[i] ^ T_(K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i])
        K.append(temp_K)
        rk.append(temp_K)
    # 轮密钥反转
    rk.reverse()
    # 文件读写部分
    file_count = 0
    c_fname = filename + '_decoded' + format(file_count, '02d')
    while isfile(c_fname):
        file_count += 1
        c_fname = filename + '_decoded' + format(file_count, '02d')
    # 加密后文件名c_fname
    with open(filename, 'rb') as text_file:
        # 一次读取整个文件，然后补0 使得 len(filename) % 16 == 0
        byte_file = text_file.read()
    if len(byte_file) % 16 != 0:
        byte_file += b'\x00' * (16 - len(byte_file) % 16)
    total_length = len(byte_file)
    # 分块
    block_size = 16
    blockNumber = total_length // block_size
    # 创建共享内存，将整个文件数据写入共享内存，不会复制多份
    shm = shared_memory.SharedMemory(create=True, size=total_length)
    # 将文件内容拷贝到共享内存中
    shm_buf = np.ndarray((total_length,), dtype=np.uint8, buffer=shm.buf)
    shm_buf[:] = np.frombuffer(byte_file, dtype=np.uint8)
    # 构造参数列表，每个任务只传递共享内存名称和块索引
    args_list = [(i, shm.name, total_length, block_size, rk) for i in range(blockNumber)]
    with Pool() as pool:
        # imap 保证结果顺序与 args_list 顺序一致
        results = list(
            tqdm(pool.imap(process_block_shm, args_list), total=blockNumber, desc='decoding process:', unit='block'))
    # 合并所有加密块
    encodeMessage = b''.join(results)
    encodeMessage = remove_padding_zeros(encodeMessage)
    with open(c_fname, 'wb') as out_file:
        out_file.write(encodeMessage)
    # 释放共享内存
    shm.close()
    shm.unlink()

    return c_fname


# def sm4_file_encode(filename, key):
#     # 轮密钥拓展
#     keyHexString = format(key, "032x")
#     MK = [int(keyHexString[:8], 16), int(keyHexString[8:16], 16), int(keyHexString[16:24], 16),
#           int(keyHexString[24:], 16)]
#     K = [MK[0] ^ FK[0], MK[1] ^ FK[1], MK[2] ^ FK[2], MK[3] ^ FK[3]]
#     rk = []
#     for i in range(0, 32):
#         temp_K = K[i] ^ T_(K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i])
#         K.append(temp_K)
#         rk.append(temp_K)
#     # 文件读写部分
#     file_count = 0
#     c_fname = filename + '_encoded' + format(file_count, '02d')
#     while isfile(c_fname):
#         file_count += 1
#         c_fname = filename + '_encoded' + format(file_count, '02d')
#     # 加密后文件名c_fname
#     with open(filename, 'rb') as text_file, open(c_fname, 'wb') as encode_file:
#         # 一次读取整个文件，然后补0 使得 len(filename) % 16 == 0
#         byte_file = text_file.read()
#         if len(byte_file) % 16 != 0:
#             byte_file += b'\x00' * (16 - len(byte_file) % 16)
#         # 分块
#         blockNumber = len(byte_file) // 16
#         # 文件加密
#         args_list = [(i, byte_file, rk) for i in range(blockNumber)]
#         encodeMessage = b''
#         for block in tqdm(range(0, blockNumber), desc='encoding process: ', unit='block'):
#             encodeMessage += sm4_algorithm(byte_file[block * 16: (block + 1) * 16], rk)
#         encode_file.write(encodeMessage)
#     return c_fname


# def sm4_file_decode(filename, key):
#     # 轮密钥拓展
#     keyHexString = format(key, "032x")
#     MK = [int(keyHexString[:8], 16), int(keyHexString[8:16], 16), int(keyHexString[16:24], 16),
#           int(keyHexString[24:], 16)]
#     K = [MK[0] ^ FK[0], MK[1] ^ FK[1], MK[2] ^ FK[2], MK[3] ^ FK[3]]
#     rk = []
#     for i in range(0, 32):
#         temp_K = K[i] ^ T_(K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i])
#         K.append(temp_K)
#         rk.append(temp_K)
#     # 轮密钥反转
#     rk.reverse()
#     # 文件读写部分
#     file_count = 0
#     c_fname = filename + '_decoded' + format(file_count, '02d')
#     while isfile(c_fname):
#         file_count += 1
#         c_fname = filename + '_decoded' + format(file_count, '02d')
#     # 加密后文件名c_fname
#     with open(filename, 'rb') as text_file, open(c_fname, 'wb') as decode_file:
#         # 一次读取整个文件，然后补0 使得 len(filename) % 16 == 0
#         byte_file = text_file.read()
#         if len(byte_file) % 16 != 0:
#             byte_file += b'\x00' * (16 - len(byte_file) % 16)
#         # 分块
#         blockNumber = len(byte_file) // 16
#         # print(f"block number: {blockNumber}")
#         # 文件加密
#         encodeMessage = b''
#         for block in tqdm(range(0, blockNumber), desc='encoding process: ', unit='block'):
#             encodeMessage += sm4_algorithm(byte_file[block * 16: (block + 1) * 16], rk)
#         encodeMessage = remove_padding_zeros(encodeMessage)
#         decode_file.write(encodeMessage)
#     return c_fname


def sm4_str_encode(text, key):
    # 测试用，正式需要放开转换为byte流
    byte_text = text.encode()
    # byte_text = text
    # 1. 补0 len(byte_text) % 16 == 0
    if len(byte_text) % 16 != 0:
        byte_text += b'\x00' * (16 - len(byte_text) % 16)
    # 2. 分块
    blockNumber = len(byte_text) // 16
    # 3. 扩展轮密钥
    # print(f"key: {key:032x}")

    keyHexString = format(key, "032x")
    MK = [int(keyHexString[:8], 16), int(keyHexString[8:16], 16), int(keyHexString[16:24], 16),
          int(keyHexString[24:], 16)]
    K = [MK[0] ^ FK[0], MK[1] ^ FK[1], MK[2] ^ FK[2], MK[3] ^ FK[3]]
    rk = []
    # rk = [0xf12186f9, 0x41662b61, 0x5a6ab19a, 0x7ba92077, 0x367360f4, 0x776a0c61, 0xb6bb89b3, 0x24763151, 0xa520307c, 0xb7584dbd, 0xc30753ed, 0x7ee55b57, 0x6988608c, 0x30d895b7, 0x44ba14af, 0x104495a1, 0xd120b428, 0x73b55fa3, 0xcc874966, 0x92244439, 0xe89e641f, 0x98ca015a, 0xc7159060, 0x99e1fd2e, 0xb79bd80c, 0x1d2115b0, 0xe228aeb, 0xf1780c81, 0x428d3654, 0x62293496, 0x1cf72e5, 0x9124a012]
    for i in range(0, 32):
        temp_K = K[i] ^ T_(K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i])
        K.append(temp_K)
        rk.append(temp_K)

        # print(f"rk_{i} = {rk[i]:08x}")
    # print(format(MK[0], "08x"))
    # print(format(MK[1], "08x"))
    # print(format(MK[2], "08x"))
    # print(format(MK[3], "08x"))
    # 4. 分块依次加密
    # 这部分因为每块之间无关联，可以并行计算
    encodeMessage = b''
    for block in range(0, blockNumber):
        encodeMessage += sm4_algorithm(byte_text[block * 16: (block + 1) * 16], rk)
    # print(byte_text)
    return encodeMessage



def sm4_str_decode(code, key):
    byte_code = bytes.fromhex(code)

    # 加密后的密文肯定长度为128bit的倍数
    # if len(byte_code) % 16 != 0:
    #     byte_code += b'\x00' * (16 - len(byte_code) % 16)
    blockNumber = len(byte_code) // 16
    keyHexString = format(key, "032x")
    MK = [int(keyHexString[:8], 16), int(keyHexString[8:16], 16), int(keyHexString[16:24], 16),
          int(keyHexString[24:], 16)]
    K = [MK[0] ^ FK[0], MK[1] ^ FK[1], MK[2] ^ FK[2], MK[3] ^ FK[3]]
    rk = []
    for i in range(0, 32):
        temp_K = K[i] ^ T_(K[i + 1] ^ K[i + 2] ^ K[i + 3] ^ CK[i])
        K.append(temp_K)
        rk.append(temp_K)
    # 轮密钥反转
    rk.reverse()
    decodeMessage = b''
    for block in range(0, blockNumber):
        temp_message = sm4_algorithm(byte_code[block * 16: (block + 1) * 16], rk)
        # 最后一轮，去除补的0x00
        if block == blockNumber - 1:
            temp_message = remove_padding_zeros(temp_message)
        decodeMessage += temp_message
    return decodeMessage


# 输入：data：string or file location; key：int
# 输出: hex string
def sm4_encode(data, key):
    if isfile(data):
        file_location = sm4_file_encode(data, key)
        return f"File encode success! File location: {file_location}"
    else:
        return sm4_str_encode(data, key)
        # 测试用
        # return sm4_str_encode(str(data), key)


# 输入: data: hex string; key: int
# 输出： byte string or file
def sm4_decode(data, key):
    if isfile(data):
        return sm4_file_decode(data, key)
    else:
        return sm4_str_decode(data, key)
