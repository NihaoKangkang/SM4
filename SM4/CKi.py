# 用程序来计算轮密钥中的CKi参数算法
# 因为是固定值，实际上将取值直接存到程序中即可

def CKi_generator():
    CK = []
    for i in range(0, 32):
        temp_CK = 0
        for j in range(0, 4):
            CKij = ((4 * i + j) * 7) % 256
            # 将字节移动到大端
            temp_CK += (CKij << (3 - j) * 8)
        CK.append(temp_CK)
    for i in CK:
        print( "0x"+format(i, "08x"), end=', ')

CKi_generator()