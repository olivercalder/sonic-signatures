import sys
sys.path.append('../Reference')
from archive_combinations import get_names
from z_scores import build_z_scores


def main():
    names = get_names()
    for name in names:
        for filetype in ['counts', 'percentages']:
            in_json = '../Archive/' + name + '/' + filetype + '.json'
            out_dir = '../Archive/' + name
            build_z_scores(in_json=in_json, nested=False, silent=True, wt=True, wj=True, title=filetype, directory=out_dir)


if __name__ == '__main__':
    main()
