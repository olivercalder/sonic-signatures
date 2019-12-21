import os

for k in range(2, 7):
    for ecs in [['a2'], ['a2', 'p'], ['a2', '7'], ['a2', 'p', '7']]:
        for mw in [0, 100, 250, 500, 1000, 1500, 2000, 2500]:
            title = 's_VOAP_{}-means_excluding-{}{}'.format(k, '-'.join(ecs), '_min-{}'.format(mw) if mw != 0 else '')
            directory = 'k-means-results/s_VOAP_{}-means_excluding-{}{}'.format(k, '-'.join(ecs), '_min-{}'.format(mw) if mw != 0 else '')
            exclude_string = ' '.join(['-e {}'.format(c) for c in ecs])
            k_means_str = 'python3 k_means.py -lc ../Archive/Vowels-Only-All/percentages.csv -k {} {} -mw {} -s -wc -wj -t {} -d {}'.format(k, exclude_string, mw, title, directory)
            print(k_means_str)
            os.system(k_means_str)
            k_means_eval_str = 'python3 k_means_evaluation.py -lc {1}/{0}_k-means-dictionary.csv -c status -s -wt -wc -wj -v -t {0} -d {1}'.format(title, directory)
            print(k_means_eval_str)
            os.system(k_means_eval_str)
