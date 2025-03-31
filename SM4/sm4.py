from os.path import isfile

T = []
T += [0x79cc4519] * 16
T += [0x7a879d8a] * 48

V = [0x7380166f, 0x4914b2b9, 0x172442d7, 0xda8a0600, 0xa96f30bc, 0x163138aa, 0xe38dee4d, 0xb0fb0e4e]


# 对信息分块 eg:  length = 23 return 1
#               length = 452 return 2
def count_blocks(length_of_messages):
    # 长度除以512 计算分块数 左移计算速度更快
    blocks = (length_of_messages >> 9)
    remainder = (length_of_messages - (blocks << 9))
    # print('余数: ', remainder)
    return (blocks + 1) if remainder < 448 else (blocks + 2)


def P_0(x):
    return x ^ ((x << 9 | x >> 23)& 0xffffffff) ^ ((x << 17 | x >> 15)& 0xffffffff)


def P_1(x):
    return x ^ ((x << 15 | x >> 17)& 0xffffffff) ^ ((x << 23 | x >> 9)& 0xffffffff)


def FF(times, x, y, z):
    if times < 16:
        return x ^ y ^ z
    else:
        return (x & y) | (x & z) | (y & z)


def GG(times, x, y, z):
    if times < 16:
        return x ^ y ^ z
    else:
        return (x & y) | (~x & z)


def V_recovery():
    V[0], V[1], V[2], V[3], V[4], V[5], V[6], V[
        7] = 0x7380166f, 0x4914b2b9, 0x172442d7, 0xda8a0600, 0xa96f30bc, 0x163138aa, 0xe38dee4d, 0xb0fb0e4e


# 输入: 512bit Message
# 目的: 计算新V[0...7]
def sm3_algorithm(blockMessage):
    # 将512 bit 消息扩展为 132 word
    B = []
    for t in range(0, 132):
        if t < 16:
            B.append(int.from_bytes(blockMessage[(t * 4): ((t + 1) * 4)]))
        elif t < 68:
            p1result = P_1(B[t - 16] ^ B[t - 9] ^ ((B[t - 3] << 15 | B[t - 3] >> 17)& 0xffffffff))
            B_temp = p1result ^ ((B[t - 13] << 7 | B[t - 13] >> 25) & 0xffffffff) ^ B[t - 6]
            B.append(B_temp)
        else:
            w_index = t - 68
            B_temp = B[w_index] ^ B[w_index + 4]
            B.append(B_temp)
    # 输出扩展结果
    # for i in range (0, 132):
    #     print(f"{B[i]:08x}", end='\t')
    #     if i < 68:
    #         if (i+1) % 8 == 0:
    #             print()
    #         if i == 67:
    #             print()
    #     else:
    #         if (i+1 - 68) % 8 == 0:
    #             print()
    a = V[0]
    b = V[1]
    c = V[2]
    d = V[3]
    e = V[4]
    f = V[5]
    g = V[6]
    h = V[7]
    # 每块进行64轮计算
    # print(f"default: {a:08x}\t{b:08x}\t{c:08x}\t{d:08x}\t{e:08x}\t{f:08x}\t{g:08x}\t{h:08x}")
    for t in range(0, 64):
        SS1_temp = (((a << 12 | a >> 20)& 0xffffffff) + e + (((T[t] << (t % 32)) | T[t] >> (32 - (t % 32))) & 0xffffffff)) & 0xffffffff
        SS1 = (SS1_temp << 7 | SS1_temp >> 25)& 0xffffffff
        SS2 = SS1 ^ ((a << 12 | a >> 20)& 0xffffffff)
        TT1 = (FF(t, a, b, c) + d + SS2 + B[t + 68]) & 0xffffffff
        TT2 = (GG(t, e, f, g) + h + SS1 + B[t]) & 0xffffffff
        d = c
        c = (b << 9 | b >> 23) & 0xffffffff
        b = a
        a = TT1
        h = g
        g = (f << 19 | f >> 13) & 0xffffffff
        f = e
        e = P_0(TT2)
        #b9edc12b 7380166f 29657292 172442d7 b2ad29f4 a96f30bc c550b189 e38dee4d
        # print(f"t={t:02d}: {a:08x}\t{b:08x}\t{c:08x}\t{d:08x}\t{e:08x}\t{f:08x}\t{g:08x}\t{h:08x}")

    V[0] = (a ^ V[0])
    V[1] = (b ^ V[1])
    V[2] = (c ^ V[2])
    V[3] = (d ^ V[3])
    V[4] = (e ^ V[4])
    V[5] = (f ^ V[5])
    V[6] = (g ^ V[6])
    V[7] = (h ^ V[7])


def sm3_file_sum(file_path):
    with open(file_path, 'rb') as read_file:
        # 将指针移到最后，计算文件大小
        read_file.seek(0, 2)
        lengthOfFile = read_file.tell() * 8
        # print('byte:', lengthOfFile // 8)
        blockNumber = count_blocks(lengthOfFile)
        # 最后一次80轮加入这条信息 addMessage
        addMessage = b'\x80'
        zeroBits = (blockNumber * 512 - 64 - 8 - lengthOfFile)
        addMessage += b'\x00' * (zeroBits // 8)
        addMessage += lengthOfFile.to_bytes(8, byteorder='big')
        # 将指针移到开头 开始sha1
        read_file.seek(0, 0)
        # 最后两轮需要额外确认
        if blockNumber >= 2:
            for block in range(0, blockNumber - 2):
                blockMessage = read_file.read(64)
                sm3_algorithm(blockMessage)

            # zeroBits range from 0, 64-8 + 448 = 504
            # 1Block zeroBits from 0 to 448-8 = 440
            # 2Blocks zeroBits from 448 to 504
            if zeroBits <= 440:
                blockMessage = read_file.read(64)
                sm3_algorithm(blockMessage)
                blockMessage = read_file.read()
                blockMessage += addMessage
                sm3_algorithm(blockMessage)
            else:
                blockMessage = read_file.read()
                blockMessage += addMessage
                print('length of block Message', len(blockMessage))
                sm3_algorithm(blockMessage[:64])
                sm3_algorithm(blockMessage[64:])
        # 只有一轮计算则直接addMessage进行计算
        else:
            blockMessage = read_file.read()
            blockMessage += addMessage
            print(blockMessage)
            sm3_algorithm(blockMessage)

    SM3 = f"{V[0]:08x}{V[1]:08x}{V[2]:08x}{V[3]:08x}{V[4]:08x}{V[5]:08x}{V[6]:08x}{V[7]:08x}"
    return SM3


def sm3_str_sum(string):
    byteMessage = string.encode()
    lengthOfMessages = len(byteMessage) * 8
    # 文本分块
    blockNumber = count_blocks(lengthOfMessages)
    # 补位
    byteMessage += b'\x80'
    zeroBits = (blockNumber * 512 - 64 - 8 - lengthOfMessages)
    byteMessage += b'\x00' * (zeroBits // 8)
    byteMessage += lengthOfMessages.to_bytes(8, byteorder='big')
    for block in range(0, blockNumber):
        byteBlock = byteMessage[(block * 64): ((block + 1) * 64)]
        sm3_algorithm(byteBlock)
    SM3 = f"{V[0]:08x}{V[1]:08x}{V[2]:08x}{V[3]:08x}{V[4]:08x}{V[5]:08x}{V[6]:08x}{V[7]:08x}"
    return SM3


def sm3_result(sha1string):
    # 恢复默认算子H
    V_recovery()
    # 将文件和非文件转换为bytes类型
    if isfile(sha1string):
        return sm3_file_sum(sha1string)
    else:
        return sm3_str_sum(str(sha1string))

def sm4_result(data, key):
    return 1