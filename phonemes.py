'''
File: get_phonemes.py
Created: Oliver Calder, 26 June 2019
Sonic Signatures Research
Supervised by Eric Alexander
Carleton College

Texts sourced from https://folgersdigitaltexts.org/api

This script returns a dictionary containing each character code paired to that that character's
text in the form of a list of phonemes. If one or more characters or plays is specified, the
dictionary will be built using only the codes and phonemes for those characters. Otherwise,
the script will build a dictionary containing every character by default.

The script can sort characters by play using the -d argument. This causes a dictionary to be
returned with a key for each play mapped to a dictionary where each character code is mapped to
the phoneme list for that character. This takes the form:
{'Mac':{'Mac_Macbeth':phonemes, 'Mac_Macduff':phonemes, ...}, 'Ham':{'Ham_Hamlet':phonemes, ...}}

Any character or play which is excluded using -ec or -ep, respectively, will not be included in
the dictionary.
'''


import get_characters
import get_texts
import nltk
# nltk.download('cmudict')
# OR
# $ python3 -m nltk.downloader [-d /usr/share/nltk_data] cmudict


def nest_dict_by_play(phoneme_dict):
    phoneme_dict_nested = {}
        for char in phoneme_dict:
            play = char.split('_')[0]
            if play not in phoneme_dict_nested:
                phoneme_dict_nested[play] = {}
            phoneme_dict_nested[play][char] = phoneme_dict[char]
        return phoneme_dict_nested


def unnest_dict(phoneme_dict_nested):
    phoneme_dict = {}
    for play in phoneme_dict_nested:
        for char in play:
            phoneme_dict[char] = phoneme_dict_nested[play][char]
    return phoneme_dict


def convert_text_to_phonemes(text, preserve_emphasis=False):
    d = nltk.corpus.cmudict.dict()
    phonemes = []
    unknowns = []
    for w in text.split():
        word = w.lower()
        if word in d:
            word_phonemes = d[word][0]
            for phon in word_phonemes:
                if phon[-1].isdigit() and not preserve_emphasis:
                    phonemes.append(phon[:-1])
                else:
                    phonemes.append(phon)
        else:
            unknowns.append(word)
    return phonemes, unknowns


def get_phoneme_dict(text_dict, nested=False, preserve_emphasis=False):
    for item in text_dict: # Way to check type of some unspecified item
        if type(item) == type({}):
            td = get_texts.unnest_dict(text_dict)
        else:
            td = text_dict
        break
    text_dict = td

    phoneme_dict = {}
    unknowns = []
    for char in text_dict:
        phoneme_dict[char], new_unknowns = convert_text_to_phonemes(text_dict[char], preserve_emphasis)
        for word in new_unknowns:
            unknowns.append(word)
    if nested:
        phoneme_dict = nest_dict_by_play(phoneme_dict)
    return phoneme_dict, unknowns


def build_phoneme_dict(play_codes=set([]), char_codes=set([]), ep=set([]), ec=set([]), nested=False, silent=False, wt=False, wj=False, cascade=False, raw=False, min_words=0):
    text_dict = get_texts.build_text_dict(play_codes, char_codes, ep, ec, nested, silent and cascade, wt and cascade, wj and cascade, cascade, raw, min_words)
    phoneme_dict = get_phoneme_dict(text_dict, nested, preserve_emphasis)
    # TODO:
    # if not silent:
    #     print_phonemes(phoneme_dict)
    # if wt != False:
    #     write_text(text_dict, wt)
    # if wj != False:
    #     write_json
