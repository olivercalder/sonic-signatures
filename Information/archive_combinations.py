'''
archive_combinations.py

Used to generate Archive directory and run baseline accuracy comparisons
'''

from itertools import combinations


defaults = [
        [{'silent':True},  '-s' ],
        [{'wt':True},      '-wt'],
        [{'wj':True},      '-wj'],
        [{'cascade':True}, '-R' ]]

class_defaults = [
        [{'silent':True}, '-s' ],
        [{'wt':True},     '-wt'],
        [{'wj':True},     '-wj']]

eval_defaults = [
        [{'silent':True},  '-s' ],
        [{'wt':True},      '-wt'],
        [{'wj':True},      '-wj'],
        [{'verbose':True}, '-v' ]]


directory = [{'directory':'../Archive/'}, '-d ../Archive/']


load_csv = [{'in_csv':'../Archive/'}, '-lt ../Archive/']

load_json = [{'in_json':'../Archive/'}, '-lj ../Archive/']


load_results_csv = [{'in_csv':'../Results/'}, '-lt ../Results/']

load_results_json = [{'in_json':'../Results/'}, '-lj ../Results/']


write_class_eval = [{'directory':'../Results/'}, '-d ../Results/']


filetype_options = [
        [{'percentages':True},  'percentages.csv', 'Percentages'],
        [{'percentages':False}, 'counts.csv',      'Counts'     ]]

class_options = [
        [{'twofold':False}, ''  , ''       ],
        [{'twofold':True},  '-2', 'Twofold']]


char_combos = [
        [{},                 '',        'All'      ], 
        [{'min_words':100},  '-m 100',  'Min-100'  ], 
        [{'min_words':250},  '-m 250',  'Min-250'  ], 
        [{'min_words':500},  '-m 500',  'Min-500'  ], 
        [{'min_words':1000}, '-m 1000', 'Min-1000' ], 
        [{'min_words':2500}, '-m 2500', 'Min-2500' ], 
        [{'eo':True},        '-eo',     'No-Others']]


options = [
        [{'preserve_emphasis':True}, '-e', 'Emphasis'   ],
        [{'vowels_only'      :True}, '-v', 'Vowels-Only']]
def get_option_combos():
    combos = []
    for i in range(len(options) + 1):
        combo_list = combinations(options, i)
        for combo in combo_list:
            if len(combo) > 0:
                combo = sorted(combo, key=lambda c: c[2])
            combos.append(list(combo))
    return combos


def get_names():
    names = []
    for char_combo in char_combos:
        char_name = char_combo[2]
        for option_combo in get_option_combos():
            name_list = []
            for option in option_combo:
                name_list.append(option[2])
            name_list.append(char_name)
            name = '-'.join(name_list)
            names.append(name)
    return names

def get_class_eval_names():
    names = get_names()
    class_names = []
    for name in names:
        for filetype_option in filetype_options:
            for class_option in class_options:
                new_name = name + '-' + filetype_option[2]
                if class_option[2]:
                    new_name += '-' + class_option[2]
                class_names.append(new_name)
    return class_names


def get_directories():
    directories = []
    names = get_names()
    for name in names:
        directories.append('../Archive/{}'.format(name))
    return directories


def get_param_dicts():
    param_dicts = []
    for char_combo in char_combos:
        char_param = char_combo[0]
        char_name = char_combo[2]
        for option_combo in get_option_combos():
            param_dict = {}
            for item in defaults:
                param_dict.update(item[0])
            param_dict.update(char_param)

            dir_list = []
            for option in option_combo:
                param_dict.update(option[0])
                dir_list.append(option[2])
            dir_list.append(char_name)
            dir_param = directory[0]['directory'] + '-'.join(dir_list)
            param_dict['directory'] = dir_param

            param_dicts.append(param_dict)
    return param_dicts


def get_arg_strings():
    arg_strings = []
    for char_combo in char_combos:
        char_arg = char_combo[1]
        for option_combo in get_option_combos():
            arg_list = []
            arg_list += [arg[1] for arg in defaults]
            arg_list.append(char_arg)
            
            dir_list = []
            for option in option_combo:
                arg_list.append(option[1])
                dir_list.append(option[2])
            dir_list.append(char_combo[2])
            dir_arg = directory[1] + '-'.join(dir_list)
            arg_list.append(dir_arg)

            arg_string = ' '.join(arg_list)
            arg_strings.append(arg_string)
    return arg_strings


def get_class_args():
    arg_strings = []
    for char_combo in char_combos:
        for option_combo in get_option_combos():
            for filetype_option in filetype_options:
                for class_option in class_options:
                    arg_list = []
                    arg_list += [arg[1] for arg in class_defaults]

                    name_list = []
                    for option in option_combo:
                        name_list.append(option[2])
                    name_list.append(char_combo[2])

                    load_arg = load_csv[1] + '-'.join(name_list) + '/' + filetype_option[1]
                    arg_list.append(load_arg)

                    name_list.append(filetype_option[2])
                    if class_option[2]:
                        name_list.append(class_option[2])
                    name = '-'.join(name_list)

                    dir_arg = write_class_eval[1] + name
                    arg_list.append(dir_arg)

                    arg_string = ' '.join(arg_list)
                    arg_strings.append(arg_string)
    return arg_strings

def get_eval_args():
    arg_strings = []
    for char_combo in char_combos:
        for option_combo in get_option_combos():
            for filetype_option in filetype_options:
                for class_option in class_options:
                    arg_list = []
                    arg_list += [arg[1] for arg in eval_defaults]

                    name_list = []
                    for option in option_combo:
                        name_list.append(option[2])
                    name_list.append(char_combo[2])
                    name_list.append(filetype_option[2])
                    if class_option[2]:
                        name_list.append(class_option[2])
                    name = '-'.join(name_list)

                    load_arg = load_results_csv[1] + name + '/' + 'results-dictionary.csv'
                    arg_list.append(load_arg)

                    dir_arg = write_class_eval[1] + name
                    arg_list.append(dir_arg)

                    name_arg = '-n ' + name
                    arg_list.append(name_arg)

                    arg_string = ' '.join(arg_list)
                    arg_strings.append(arg_string)
    return arg_strings


def test():
    combos = get_option_combos()
    print('get_option_combos()')
    for item in combos:
        print(item)
    print()
    
    names = get_names()
    print('get_names()')
    for item in names:
        print(item)
    print()
    
    directories = get_directories()
    print('get_directories()')
    for item in directories:
        print(item)
    print()
    
    params = get_param_dicts()
    print('get_param_dicts()')
    for item in params:
        print(item)
    print()
    
    args = get_arg_strings()
    print('get_arg_strings()')
    for item in args:
        print(item)
    print()

    class_eval_names = get_class_eval_names()
    print('get_class_eval_names()')
    for item in class_eval_names:
        print(item)
    print()

    class_args = get_class_args()
    print('get_class_args()')
    for item in class_args:
        print(item)
    print()

    eval_args = get_eval_args()
    print('get_eval_args()')
    for item in eval_args:
        print(item)
    print()


if __name__ == '__main__':
    test()
