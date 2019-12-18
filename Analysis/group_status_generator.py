import os

for m in [0, 100, 250, 500, 1000, 1500, 2000, 2500]:
    for n in range(1, 8):
        for d in ['', '-d']:
            print('python3 group_status.py -m {} -n {} {}'.format(m, n, d))
            os.system('python3 group_status.py -m {} -n {} {}'.format(m, n, d))

    for g in ['', '-g ovl', '-g avg', '-g f1', '-g mcc']:
        for d in ['', '-d']:
            print('python3 group_status.py -m {} -n 1 {} {}'.format(m, g, d))
            os.system('python3 group_status.py -m {} -n 1 {} {}'.format(m, g, d))
