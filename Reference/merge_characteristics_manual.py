import sys
import os
import csv


def get_orig_dicts(orig_filename):
    orig = {}
    orig_codes = {}
    with open(orig_filename, newline='') as orig_file:
        for line in orig_file:
            line = line.rstrip()
            if line != '':
                code, play = line.split(': ')
                orig[play] = code
                orig_codes[code] = play
    return orig, orig_codes


def get_eos_dicts(eos_filename):
    eos = {}
    eos_codes = {}
    with open(eos_filename, newline='') as eos_file:
        reader = csv.DictReader(eos_file, delimiter='|')
        for row in reader:
            play = row['play']
            code = row['code']
            eos[play] = row
            eos_codes[code] = play
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


def check_if_same(orig, eos):
    orig_diff, eos_diff = get_differences(orig, eos)
    return (orig_diff == []) and (eos_diff == [])


def get_play_conversions(orig, eos):
    orig_to_eos_play = {}
    eos_to_orig_play = {}
    for play in orig.keys():
        orig_code = orig[play]
        eos_code = eos[play]['code']
        orig_to_eos_play[orig_code] = eos_code
        eos_to_orig_play[eos_code] = orig_code
    return orig_to_eos_play, eos_to_orig_play


def get_characteristics(char_filename):
    characteristics = {}
    with open(char_filename, newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            char = row['character']
            characteristics[char] = row
    return characteristics


def get_eos_characteristics(char_filename, eos_to_orig_play):
    eos_characteristics = {}
    with open(char_filename, newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            eos_code = row['play']
            if eos_code == '':
                print(row)
            orig_code = eos_to_orig_play[eos_code]
            char = orig_code + '_' + row['character']
            eos_characteristics[char] = row
    return eos_characteristics


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


def write_pairings(man_pair_filename, man_pairings):
    with open(man_pair_filename, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['orig', 'eos'])
        writer.writeheader()
        for char in sorted(man_pairings):
            writer.writerow({'orig': char, 'eos': man_pairings[char]})


def write_unknowns(unknowns_filename, unknowns):
    with open(unknowns_filename, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['orig', 'eos'])
        writer.writeheader()
        for char in sorted(unknowns):
            writer.writerow({'orig': char, 'eos': unknowns[char]})

def write_characteristics(characteristics_filename, characteristics):
    with open(characteristics_filename, 'w', newline='') as outfile:
        header = ['character', 'gender', 'role', 'genre', 'status', 'word_count']
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        for char in sorted(characteristics):
            writer.writerow(characteristics[char])


def quit_procedure(man_pair_filename, man_pairings, unknowns_filename, unknowns, characteristics_filename, characteristics):
    if input('Write pairings to files? [y/n] ').lower()[0] == 'y':
        write_pairings(man_pair_filename, man_pairings)
        write_unknowns(unknowns_filename, unknowns)
        write_characteristics(characteristics_filename, characteristics)
    quit()


def main():
    orig_filename = 'Play_Codes.txt'
    eos_filename = 'Play_Codes_EoS.txt'
    characteristics_filename = 'characteristics.csv'
    eos_char_filename = 'social_tags_v7.csv'
    auto_pair_filename = 'auto_pairings.csv'
    man_pair_filename = 'manual_pairings.csv'
    unknowns_filename = 'unknowns.txt'

    orig_plays, orig_codes = get_orig_dicts(orig_filename)
    eos_plays, eos_codes = get_eos_dicts(eos_filename)
    if not check_if_same(orig_plays, eos_plays):
        orig_play_diff, eos_play_diff = get_differences(orig_plays, eos_plays)
        print('orig - eos:', orig_play_diff)
        print('eos - orig:', eos_play_diff)
        if input('Proceed anyway? [y/n] ')[0].lower() != 'y':
            quit()

    orig_to_eos_play, eos_to_orig_play = get_play_conversions(orig_plays, eos_plays)
    play_codes = sorted(orig_codes.keys())

    characteristics = get_characteristics(characteristics_filename)
    # This is the auto-generated characteristics.csv file, which will be modified and saved

    eos_characteristics = get_eos_characteristics(eos_char_filename, eos_to_orig_play)

    eos_unknowns = get_differences(characteristics, eos_characteristics)[1]
    # eos_unknowns still useful to isolate eos characters which do not have a direct match

    unknowns = {}
    if os.path.exists(unknowns_filename):
        with open(unknowns_filename, newline='') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                unknowns[row['orig']] = row['eos']

    auto_pairings = {}
    if os.path.exists(auto_pair_filename):
        with open(auto_pair_filename, newline='') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                orig_char = row['orig']
                eos_char = row['eos']
                auto_pairings[orig_char] = eos_char
                # characteristics.csv already reflects these auto pairings

    man_pairings = {}
    if os.path.exists(man_pair_filename):
        with open(man_pair_filename, newline='') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                orig_char = row['orig']
                eos_char = row['eos']
                if orig_char in unknowns:
                    del unknowns[orig_char]
                man_pairings[orig_char] = eos_char
                characteristics[orig_char]['status'] = eos_characteristics[eos_char]['status']

    already_matched = set([char for char in list(auto_pairings.values()) + list(man_pairings.values())])

    rem_unknowns = sorted(set(unknowns.keys()) - set(man_pairings.keys()))
    # unknowns and auto_pairings are disjoint, with the exception of characters with "All" in their name

    play_diff_dict = get_play_diff_dict(play_codes, rem_unknowns, eos_unknowns)
    # All orig chars which remain unknown, and all eos chars which have no direct matches
    #     Do not exclude matched eos chars, since orig chars may map to more than one eos char

    for code in play_codes:
        play_unknowns = []
        orig_chars = play_diff_dict[code]['orig']
        eos_chars = play_diff_dict[code]['eos']
        eos_matched_in_play = [char.split('_')[1] for char in already_matched if char.split('_')[0] == code]
        unmatched = sorted(set(eos_chars) - set(eos_matched_in_play))
        print('\n')
        print(code)
        print('\norig:')
        print(orig_chars)
        print('\neos:')
        print(eos_chars)
        print('\nunmatched:')
        print(unmatched)
        for orig_char in orig_chars:
            print('\nCharacter:', orig_char)
            orig_components = orig_char.lower().split('.')
            suggested = unknowns[code+'_'+orig_char]
            if suggested == 'no_match':
                print('Could not find line in the text.')
            elif suggested == 'wrong_div':
                print('Found line, but could not find speaker div.')
            elif suggested == 'bad_url':
                print('Bad URL.')  # This should never happen
            else:
                suggested = suggested.split('_')[1]
                print('Suggested', suggested)
                orig_components += suggested.lower().split(' ')
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
                        choice = input('Does {} match with {}? [y/n/s/q] '.format(orig_char, eos_char)).lower()[0]
                        if choice == 'q':
                            quit_procedure(man_pair_filename, man_pairings, unknowns_filename, unknowns, characteristics_filename, characteristics)
                        elif choice == 's':
                            print('Skipping', orig_char)
                            play_unknowns.append(orig_char)
                            done = True
                            found = True
                        elif choice == 'y':
                            char_code = code+'_'+orig_char
                            match_code = code+'_'+eos_char
                            del unknowns[char_code]
                            man_pairings[char_code] = match_code
                            characteristics[char_code]['status'] = eos_characteristics[match_code]['status']
                            found = True
                        done = True
                    j += (k + 1) // len(eos_components)
                    k = (k + 1) % len(eos_components)
                i += 1

            if not found:
                print('No matches predicted')
                choice = input('Display possibilities? [y/n/s/q] ').lower()[0]
                if choice == 'q':
                    quit_procedure(man_pair_filename, man_pairings, unknowns_filename, unknowns, characteristics_filename, characteristics)
                elif choice == 's':
                    print('Skipping', orig_char)
                    play_unknowns.append(orig_char)
                    continue
                elif choice == 'y':
                    print('\norig:')
                    print(orig_chars)
                    print('\neos:')
                    print(eos_chars)
                    print('\nunmatched:')
                    print(unmatched)
                    print()
                choice = input('Do you wish to type the name of a match? [y/n/s/q] ').lower()[0]
                if choice == 'q':
                    quit_procedure(man_pair_filename, man_pairings, unknowns_filename, unknowns, characteristics_filename, characteristics)
                elif choice == 'y':
                    match = ''
                    matched = False
                    while not matched:
                        match = input('Please enter name of match exactly as it appears above: ')
                        if match not in eos_chars:
                            choice = input("'{}' not found in EoS characters. Try again? [y/n/s/q] ".format(match)).lower()[0]
                            if choice == 'q':
                                quit_procedure(man_pair_filename, man_pairings, unknowns_filename, unknowns, characteristics_filename, characteristics)
                            elif choice != 'y':
                                print('Skipping', orig_char)
                                play_unknowns.append(orig_char)
                                matched = True
                        else:
                            char_code = code+'_'+orig_char
                            match_code = code+'_'+match
                            del unknowns[char_code]
                            man_pairings[char_code] = match_code
                            characteristics[char_code]['status'] = eos_characteristics[match_code]['status']
                            matched = True
                else:
                    print('Skipping', orig_char)
                    play_unknowns.append(orig_char)

        print('Remaining unknowns for {}:'.format(code))
        print(play_unknowns)

    quit_procedure(man_pair_filename, man_pairings, unknowns_filename, unknowns, characteristics_filename, characteristics)

if __name__ == '__main__':
    main()
