import sys
import os
import csv


def get_orig_dicts(orig_filename):
    orig = {}
    orig_codes = {}
    with open(orig_filename) as orig_file:
        for line in orig_file:
            if line.rstrip() != '' and line[0] != ',':
                line = line.rstrip().replace(', ', '|')
                code, play = line.split(': ')
                play.replace('|', ', ')
                orig[play] = code
                orig_codes[code] = play
    return orig, orig_codes


def get_eos_dicts(eos_filename):
    eos = {}
    eos_codes = {}
    with open(eos_filename) as eos_file:
        i = 0
        for line in eos_file:
            if i > 0 and line.rstrip() != '' and line[0] != ',':
                line = line.rstrip().replace(', ', '|')
                play, code, genre = line.split(',')
                play.replace('|', ', ')
                eos[play] = {'code':code, 'genre':genre}
                eos_codes[code] = play
            i += 1
    return eos, eos_codes


def get_differences(orig, eos):
    if type(orig) == type({}):
        orig_set = set(orig.keys())
    else:
        orig_set = set(orig)

    if type(eos) == type({}):
        eos_set = set(eos.keys())
    else:
        eos_set = set(eos)

    orig_diff = sorted(orig_set - eos_set)
    eos_diff = sorted(eos_set - orig_set)
    return orig_diff, eos_diff


def get_shared(orig, eos):
    if type(orig) == type({}):
        orig_set = set(orig.keys())
    else:
        orig_set = set(orig)

    if type(eos) == type({}):
        eos_set = set(eos.keys())
    else:
        eos_set = set(eos)

    shared = sorted(orig_set & eos_set)
    return shared


def check_if_same(orig, eos):
    orig_diff, eos_diff = get_differences(orig, eos)
    return (orig_diff == []) and (eos_diff == [])


def get_play_conversion(orig, eos_codes):
    eos_to_orig_play = {}
    for code in eos_codes.keys():
        play = eos_codes[code]
        eos_to_orig_play[code] = orig[play]
    return eos_to_orig_play


def get_orig_char_dict(char_filename):
    orig_char_dict = {}
    with open(char_filename, newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            char = row['character']
            orig_char_dict[char] = row
    return orig_char_dict


def get_eos_char_dict(char_filename, eos_to_orig_play):
    eos_char_dict = {}
    with open(char_filename, newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            eos_code = row['play']
            if eos_code == '':
                print(row)
            orig_code = eos_to_orig_play[eos_code]
            char = orig_code + '_' + row['character']
            eos_char_dict[char] = row
    return eos_char_dict


def get_play_diff_dict(play_codes, orig_char_diff, eos_char_diff):
    play_diff_dict = {}
    for code in play_codes:
        play_diff_dict[code] = {'orig': [], 'eos': []}
    for char in orig_char_diff:
        code, name = char.split('_')
        play_diff_dict[code]['orig'].append(name)
    for char in eos_char_diff:
        code, name = char.split('_')
        play_diff_dict[code]['eos'].append(name)
    return play_diff_dict


def write_pairings(pair_filename, pairings):
    with open(pair_filename, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['orig', 'eos'])
        writer.writeheader()
        for orig_char in sorted(pairings):
            writer.writerow({'orig': orig_char, 'eos': pairings[orig_char]})

def quit_procedure(pair_filename, pairings):
    if input('Write pairings to {} ? [y/n] '.format(pair_filename)).lower()[0] == 'y':
        write_pairings(pair_filename, pairings)
    quit()


def main():
    orig_filename = 'Play_Codes.txt'
    eos_filename = 'Play_Codes_EoS.txt'
    orig_char_filename = 'orig_characteristics.csv'
    eos_char_filename = 'social_tags_v7.csv'
    pair_filename = 'manual_pairings.csv'
    unknowns_filename = 'unknowns.txt'

    orig_plays, orig_codes = get_orig_dicts(orig_filename)
    eos_plays, eos_codes = get_eos_dicts(eos_filename)
    if not check_if_same(orig_plays, eos_plays):
        orig_play_diff, eos_play_diff = get_differences(orig_plays, eos_plays)
        print('orig - eos:', orig_play_diff)
        print('eos - orig:', eos_play_diff)
        if input('Proceed anyway? [y/n] ')[0].lower() != 'y':
            quit()

    eos_to_orig_play = get_play_conversion(orig_plays, eos_codes)
    play_codes = sorted(eos_to_orig_play.values())

    orig_char_dict = get_orig_char_dict(orig_char_filename)
    eos_char_dict = get_eos_char_dict(eos_char_filename, eos_to_orig_play)

    orig_unknowns, eos_unknowns = get_differences(orig_char_dict, eos_char_dict)

    pairings = {}
    if os.path.exists(pair_filename):
        with open(pair_filename, newline='') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                pairings[row['orig']] = row['eos']

    unknowns = sorted(set(orig_unknowns) - set(pairings.keys()))

    if unknowns != []:
        play_diff_dict = get_play_diff_dict(play_codes, unknowns, eos_unknowns)

        orig_unknowns_dict = {}
        for code in play_codes:
            orig_unknowns_dict[code] = []
            orig_chars = play_diff_dict[code]['orig']
            eos_chars = play_diff_dict[code]['eos']
            print('\n')
            print(code)
            print('\norig:')
            print(orig_chars)
            print('\neos:')
            print(eos_chars)
            for orig_char in orig_chars:
                print('\nCharacter:', orig_char)
                orig_components = orig_char.lower().split('.')
                found = False
                i = 0  # Index of eos_chars
                while not found and i < len(eos_chars):
                    eos_char = eos_chars[i]
                    eos_components = eos_char.lower().split(' ')
                    if eos_components[0].isdigit():
                        eos_components = eos_components[1:]
                    done = False
                    j = 0  # Index of orig_components
                    k = 0  # Index of eos_components
                    while not done and j < len(orig_components):
                        orig_comp = orig_components[j]
                        eos_comp = eos_components[k]
                        if orig_comp in eos_comp or eos_comp in orig_comp and orig_comp != '' and eos_comp != '':
                            choice = input('Does {} match with {}? [y/n/q] '.format(orig_char, eos_char)).lower()[0]
                            if choice == 'q':
                                quit_procedure(pair_filename, pairings)
                            elif choice == 'y':
                                pairings[code+'_'+orig_char] = code+'_'+eos_char
                                found = True
                            done = True
                        j += (k + 1) // len(eos_components)
                        k = (k + 1) % len(eos_components)
                    i += 1

                if not found:
                    print('No matches predicted')
                    choice = input('Display possibilities? [y/n/q] ').lower()[0]
                    if choice == 'q':
                        quit_procedure(pair_filename, pairings)
                    elif choice == 'y':
                        print(eos_chars)
                        print()
                    choice = input('Do you wish to type the name of a match? [y/n/q] ').lower()[0]
                    if choice == 'q':
                        quit_procedure(pair_filename, pairings)
                    elif choice == 'y':
                        match = ''
                        matched = False
                        while not matched:
                            match = input('Please enter name of match exactly as it appears above: ')
                            if match not in eos_chars:
                                choice = input("'{}' not found in EoS characters. Try again? [y/n/q] ".format(match)).lower()[0]
                                if choice == 'q':
                                    quit_procedure(pair_filename, pairings)
                                elif choice != 'y':
                                    print('Skipping', orig_char)
                                    orig_unknowns_dict[code].append(orig_char)
                                    matched = True
                            else:
                                pairings[code+'_'+orig_char] = code+'_'+match
                                matched = True
                    else:
                        print('Skipping', orig_char)
                        orig_unknowns_dict[code].append(orig_char)

            print('Remaining unknowns for {}:'.format(code))
            print(orig_unknowns_dict[code])

        with open(unknowns_filename, 'w') as outfile:
            print('{:^80}'.format('Names without direct matches or manual pairings:'), file=outfile)
            for code in play_codes:
                print('\n', file=outfile)
                print(code, file=outfile)
                print('\nRemaining unknowns from original list', file=outfile)
                print(orig_unknowns_dict[code], file=outfile)
                print('\neos', file=outfile)
                print(play_diff_dict[code]['eos'], file=outfile)

        write_pairings(pair_filename, pairings)

    else:
        header = ['character', 'gender', 'role', 'genre', 'status']
        complete_chars = []
        shared_chars = get_shared(orig_char_dict, eos_char_dict)
        for orig_char in orig_unknowns:
            eos_char = pairings[orig_char]
        # Build real characteristics file by combining 


if __name__ == '__main__':
    main()
