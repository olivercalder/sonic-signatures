'''
archive_combinations.py

Used to generate Archive directory and run baseline accuracy comparisons
'''

from itertools import combinations


defaults = [[{'silent':True},'-s'], [{'wt':True},'-wt'], [{'wj':True},'-wj'], [{'cascade':True},'-R']]

directory = [{'directory':'../Archive/'},'-d ../Archive/']

char_combos = [
        [{},                 '',        'All'      ], 
        [{'min_words':100},  '-m 100',  'Min-100'  ], 
        [{'min_words':250},  '-m 250',  'Min-250'  ], 
        [{'min_words':500},  '-m 500',  'Min-500'  ], 
        [{'min_words':1000}, '-m 1000', 'Min-1000' ], 
        [{'min_words':2500}, '-m 2500', 'Min-2500' ], 
        [{'eo':True},        '-eo',     'No-Others']]


options = [[{'preserve_emphasis':True},'-e','Emphasis'], [{'vowels_only':True},'v','Vowels-Only']]
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


if __name__ == '__main__':
    test()
