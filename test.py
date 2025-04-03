i = 1
s = 'filename' + format(i, '01d') + 'test'
for j in range(0, 20):
    print(s)
    i += 1
    s = 'filename' + format(i, '01d') + 'test'