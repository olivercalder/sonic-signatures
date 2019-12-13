import sys
import os


def print_help_string():
    print('''
Usage: python3 {} [arguments]

Arguments:
    -cd         Class Dictionary: Hold out one class at a time, train on the
                    remaining classes, and then classify characters from the
                    held out classes using the model built on the remaining
                    classes.
'''.format(sys.argv[0]))


def main(classes=False):
    base_class = 'python3 ../Naive-Bayes/classification.py -lc ../Archive/Vowels-Only-All/percentages.csv -c status -e a2 -s -wc -wj -t {1} -d s_VOAP_{0}Results/{1}'
    base_eval = 'python3 ../Naive-Bayes/evaluation.py -lc s_VOAP_{0}Results/{1}/{1}_results-dictionary.csv -s -wt -wc -wj -v -n {1} -t {1} -d s_VOAP_{0}Results/{1}'
    base_title = 's_VOAP_{0}Results_excluding-a2'

    d_arg = ''
    if classes:
        d_arg = 'Class-'
        base_class += ' -cd'


    for mw in [0, 100, 250, 500, 1000, 1500, 2000, 2500]:
        for ecs in [[''], ['7'], ['p'], ['7','p']]:
            new_class = base_class
            new_eval = base_eval
            new_title = '-'.join([base_title] + ecs).rstrip('-').format(d_arg)
            if ecs != ['']:
                for c in ecs:
                    new_class += ' -e {}'.format(c)
            if mw != 0:
                new_class += ' -mw {}'.format(mw)
                new_title += '-min-{}'.format(mw)
            os.system(new_class.format(d_arg, new_title))
            os.system(new_eval.format(d_arg, new_title))

if __name__ == '__main__':
    classes = False

    i = 1
    unrecognized = []
    while i < len(sys.argv):
        if sys.argv[i] == '-h':
            print_help_string()
            quit()
        elif sys.argv[i] == '-cd':
            classes = True
        else:
            unrecognized.append(sys.argv[i])
        i += 1

    if len(unrecognized) > 0:
        print('\nERROR: Unrecognized Arguments:')
        for arg in unrecognized:
            print(arg)
        print()
        print_help_string()
    else:
        main(classes)

