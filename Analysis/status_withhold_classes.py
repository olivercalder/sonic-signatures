import os

base_class = 'python3 ../Naive-Bayes/classification.py -lc ../Archive/Vowels-Only-All/percentages.csv -c status -e a2 -cd -s -wc -wj -t {0} -d Status-Withhold-Class-Results/{0}'
base_eval = 'python3 ../Naive-Bayes/evaluation.py -lc Status-Withhold-Class-Results/{0}/{0}_class-results-dictionary.csv -s -wt -wc -wj -v -n {0} -t {0} -d Status-Withhold-Class-Results/{0}'
base_title = 'status-withhold-classes-excluding-a2'

for mw in [0, 100, 250, 500, 1000, 1500, 2000, 2500]:
    for ecs in [[''], ['7'], ['p'], ['7','p']]:
        new_class = base_class
        new_eval = base_eval
        new_title = '-'.join([base_title] + ecs).rstrip('-')
        if ecs != ['']:
            for c in ecs:
                new_class += ' -e {}'.format(c)
        if mw != 0:
            new_class += ' -mw {}'.format(mw)
            new_title += '-min-{}'.format(mw)
        os.system(new_class.format(new_title))
        os.system(new_eval.format(new_title))
