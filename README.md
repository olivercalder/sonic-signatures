# sonic-signatures
Machine learning and data visualization research into phoneme patterns of authors.

### Researchers:
- Eric Alexander _Supervisor_
- Oliver Calder

### Dependencies:
- Python 3 (preferably 3.7)
- Libraries:
  - bs4
  - copy
  - collections
  - csv
  - itertools
  - json
  - nltk
  - numpy
  - os
  - queue
  - requests
  - sklearn
  - sys
  - threading
  - time

## General Program Flow:
1. `characters.py` and `texts.py` pull character lists and texts, respectively, from [folgerdigitaltexts.org/api](https://www.folgerdigitaltexts.org/api/)
2. `phonemes.py` converts texts to a list of phonemes for each character
3. `counts.py` and `percentages.py` count the number of occurrences and the percentage of total, respectively, for each phoneme, and returns phoneme vectors
4. `classification.py` loads from a phoneme vector file a list of characters and a list of phoneme vectors and performs hold-one-out classification on each vector in the list, producing a dictionary of actual and predicted class for each character
5. `evaluation.py` takes the classification dictionary and converts it into a confusion matrix, calculating its overall and average accuracy as well as other statistics

## Directory Structure:
- [Archive](https://github.com/olivercalder/sonic-signatures/tree/master/Archive): Saved text, phoneme, counts, and percentages data for a variety of combinations of parameters
- [Information](https://hitgub.com/olivercalder/sonic-signatures/tree/master/Information): Helper scripts and data used by other scripts to classify characters or generate combinations of parameters
- [Naive-Bayes](https://github.com/olivercalder/sonic-signatures/tree/master/Naive-Bayes): Scripts used to classify characters using Naive Bayes
- [Preprocessing](https://github.com/olivercalder/sonic-signatures/tree/master/Preprocessing): Scripts to get character lists and texts from [folgerdigitaltexts.org/api](https://www.folgerdigitaltexts.org/api/) and convert those texts into phonemes, and then count or percentage vectors for each character
- [Results](https://github.com/olivercalder/sonic-signatures/tree/master/Results): Saved classification results and summaries generated from the count or percentage data in the [Archive](https://github.com/olivercalder/sonic-signatures/tree/master/Archive) using the scripts in [Naive-Bayes](https://github.com/olivercalder/sonic-signatures/tree/master/Naive-Bayes)

## Preprocessing Details:
| Program: | Returns: | Writes: | Depends: |
|----------|----------|---------|----------|
| `characters.py` | Set or Dictionary or sets by play | Text or JSON | folgersdigitaltexts.org |
| `texts.py` | Dictionary or Dictionary of dictionaries by play | Text or JSON | `characters.py` |
| `phonemes.py` | Dictionary or Dictionary of dictionaries by play | Text or JSON | `texts.py` |
| `counts.py` | Nested dictionary (`{char:{phoneme:count, ...}, ...}`) or Dictionary of nested dictionaries by play (`{play:{char{phoneme:count, ...}, ...}, ...}`) | JSON or csv | `phonemes.py` |
| `percentages.py` | Nested dictionary (`{char:{phoneme:percentage, ...}, ...}`) or Dictionary of nested dictionaries by play (`{play:{char{phoneme:percentage, ...}, ...}, ...}`) | JSON or csv | `counts.py` |

__Command-Line Argument Guidelines__:
| Argument | Description |
|----------|-------------|
| `-h`       | Help: Prints help string |
| `-p [play_code]` | Includes specified play |
| `-c [char_code]` | Includes specified character |
| `-ep [play_code]` | Excludes specified play (overrides conflicting `-p`) |
| `-ec [char_code]` | Excludes specified character (overrides conflicting `-c`) |
| `-eo` | Exclude characters with the role of "other" |
| `-n` | Nests the output by play |
| `-s` | Silent (does not print to console) |
| `-wt` | Writes output to file as text (or csv) |
| `-wj` | Writes output to file as json |
| `-t [title]` | Specifies title of specified run, to be used in output file names |
| `-d [path/to/dir]` | Specifies directory in which to write output files |
| `-R` | Recursively write each subordinate script's output in the same manner as the primary script being run |
| `-u` | Return unknown words instead of phonemes |
| `-v` | Vowels only: ignore consonants when creating phoneme vectors |
| `-e` | Preserve emphasis marking in phonemes |
| `-r` | Preserve raw text (not recommended beyond `texts.py` |
| `-m [min_words]` | Only include characters who have a total word count greater than or equal to the specified word count |
