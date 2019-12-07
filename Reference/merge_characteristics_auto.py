import sys
import os
import requests
import bs4
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


def write_pairings(pair_filename, pairings):
    with open(pair_filename, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['orig', 'eos'])
        writer.writeheader()
        for orig_char in sorted(pairings):
            writer.writerow({'orig': orig_char, 'eos': pairings[orig_char]})


def write_unknowns(unknowns_filename, true_unknowns):
    with open(unknowns_filename, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['orig', 'eos'])
        for unknown in sorted(true_unknowns):
            writer.writerow(unknown)


def write_characteristics(characteristics_filename, characteristics):
    with open(characteristics_filename, 'w', newline='') as outfile:
        header = ['character', 'gender', 'role', 'genre', 'status', 'word_count']
        writer = csv.DictWriter(outfile, fieldnames=header)
        writer.writeheader()
        for char in sorted(characteristics):
            writer.writerow(characteristics[char])


def main():
    orig_filename = 'Play_Codes.txt'
    eos_filename = 'Play_Codes_EoS.txt'
    orig_char_filename = 'orig_characteristics.csv'
    eos_char_filename = 'social_tags_v7.csv'
    auto_pair_filename = 'auto_pairings.csv'
    man_pair_filename = 'manual_pairings.csv'
    unknowns_filename = 'unknowns.txt'
    characteristics_filename = 'characteristics.csv'

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

    characteristics = get_characteristics(orig_char_filename)
    eos_characteristics = get_eos_characteristics(eos_char_filename, eos_to_orig_play)

    orig_unknowns, eos_unknowns = get_differences(characteristics, eos_characteristics)

    man_pairings = {}
    if os.path.exists(man_pair_filename):
        with open(man_pair_filename, newline='') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                man_pairings[row['orig']] = row['eos']

    unknowns = sorted(set(orig_unknowns) - set(man_pairings.keys()))
    true_unknowns = []

    auto_pairings = {}

    for code in play_codes:
        orig_r = requests.get('https://www.folgerdigitaltexts.org/{}/charText/'.format(code))
        orig_raw = orig_r.text
        soup = bs4.BeautifulSoup(orig_raw, 'html.parser')
        divs = soup.find_all('div')

        play = orig_codes[code]
        eos_url_code = eos_plays[play]['url_code']
        #style = eos_plays[play]['style']
        eos_r = requests.get('https://internetshakespeare.uvic.ca/doc/{}/complete/index.html'.format(eos_url_code))
        eos_raw = eos_r.text
        eos_soup = bs4.BeautifulSoup(eos_raw, 'html.parser')
        eos_divs = eos_soup.find_all('div', 'line')
        if len(eos_divs) == 0:
            print('\n\nURL not working for {}\n\n'.format(code))

        i = 2  # First word count appears at index 2, first character name at index 3
        while i + 1 < len(divs):  # Iterates through characters in Folger
            word_count = int(divs[i].get_text())
            link = divs[i+1].a
            suffix = link.get('href')
            char_code = suffix.split('.html')[0]
            characteristics[char_code]['word_count'] = word_count
            characteristics[char_code]['status'] = ''

            if char_code in man_pairings:
                print(char_code, 'manually paired to', man_pairings[char_code])
                eos_char_code = man_pairings[char_code]
            elif char_code in eos_characteristics:
                print('Exact match:', char_code)
                eos_char_code = char_code
            elif char_code in unknowns and not len(eos_divs) == 0:  # If URL is found in EoS corpus
                eos_char_code = ''
                char_r = requests.get('https://www.folgerdigitaltexts.org/{}/charText/{}'.format(code, suffix))
                char_raw = char_r.text
                char_soup = bs4.BeautifulSoup(char_raw, 'html.parser')
                char_text = char_soup.get_text()
                line1_raw = char_text.lstrip().split('\n')[0].rstrip()
                line1 = ''
                for letter in line1_raw:
                    if letter.isalpha():
                        line1 += letter.lower()
                
                for n in range(len(eos_divs)):  # Iterates through divs of EoS play
                    div = eos_divs[n]
                    found = False
                    string = ''
                    for string_raw in div.strings:  # Merge all strings from a div into one string
                        for letter in string_raw:   # This is important since Folio texts have terrible span organization
                            if letter.isalpha():
                                string += letter.lower()
                    if line1 in string:  # Found a div with the text
                        for offset in [0,1]:
                            if eos_divs[n-offset].find('span', class_='speaker') != None:
                                possible = code + '_' + eos_divs[n-offset].find('span', class_='speaker').get('title')
                                possible = possible.lstrip().rstrip()
                                if possible in eos_characteristics:  # The speaker is in EoS characters
                                    eos_char_code = possible
                                    print(char_code, '::', eos_char_code)
                                    auto_pairings[char_code] = eos_char_code
                                    if 'All' in eos_char_code:  # Add manual verification of character text matches "All"
                                        true_unknowns.append([char_code, eos_char_code])

                                else:  # Found a div with the text, but the listed speaker is not in EoS characters
                                    print(char_code, 'matches', possible, ' but', possible, 'not in EoS characters.')
                                    true_unknowns.append([char_code, possible])

                                break  # Stop checking offsets and move onto next break statement, which brings next character

                        else:  # Found text, but the possible divs did not have a span element with title attribute
                            print('Found first line for', char_code, 'but could not find speaker element.')
                            true_unknowns.append([char_code, 'wrong_div'])
                        
                        break  # Stop looking through divs, move on to next character

                else:  # Checked every div and none contained the text
                    print('No text matched first line for', char_code)
                    true_unknowns.append([char_code, 'no_match'])

            else:  # Skip character because EoS URL was bad (this should not happen anymore)
                print('Bad URL for', code, 'so skipping', char_code)
                true_unknowns.append([char_code, 'bad_url'])

            if eos_char_code != '':
                characteristics[char_code]['status'] = eos_characteristics[eos_char_code]['status']

            i += 2

    write_pairings(auto_pair_filename, auto_pairings)

    write_unknowns(unknowns_filename, true_unknowns)

    write_characteristics(characteristics_filename, characteristics)


if __name__ == '__main__':
    main()
