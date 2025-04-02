def remove_padding_zeros(data):
    length = len(data)
    print(data[length - 4])
    while length > 0 and data[length - 1] == 0x00:
        length -= 1
    print(length)
    return data[:length]

text = b'hello, world.\x00\x00\x00'
print(remove_padding_zeros(text))