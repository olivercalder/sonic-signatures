# sonic-signatures
Research into the classification of characters based on the patterns of phoneme occurrence in their speech. 

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
1. [`characters.py`](https://github.com/olivercalder/sonic-signatures/blob/master/Preprocessing/characters.py) and `texts.py` pull character lists and texts, respectively, from [folgerdigitaltexts.org/api](https://www.folgerdigitaltexts.org/api/)
2. [`phonemes.py`](https://github.com/olivercalder/sonic-signatures/blob/master/Preprocessing/phonemes.py) converts texts to a list of phonemes for each character
3. [`counts.py`](https://github.com/olivercalder/sonic-signatures/blob/master/Preprocessing/counts.py) and [`percentages.py`](https://github.com/olivercalder/sonic-signatures/blob/master/Preprocessing/percentages.py) count the number of occurrences and the percentage of total, respectively, for each phoneme, and returns phoneme vectors
4. [`z_scores.py`](https://github.com/olivercalder/sonic-signatures/blob/master/Statistics/z_scores.py) calculates Z-scores for the count or percentage vectors in a given file
5. [`classification.py`](https://github.com/olivercalder/sonic-signatures/blob/master/Naive-Bayes/classification.py) loads from a phoneme vector file a list of characters and a list of phoneme vectors and performs hold-one-out classification on each vector in the list, producing a dictionary of actual and predicted class for each character
6. [`evaluation.py`](https://github.com/olivercalder/sonic-signatures/blob/master/Naive-Bayes/evaluation.py) takes the classification dictionary and converts it into a confusion matrix, calculating its overall and average accuracy as well as other statistics
7. [`beeswarm.js`](https://github.com/olivercalder/sonic-signatures/blob/master/Visualization/beeswarm.js) and [`barchart.js`](https://github.com/olivercalder/sonic-signatures/blob/master/Visualization/barchart.js) use Z-scores generated by `z_scores.py` and stored in `/Archive/<option-combo>/<counts/percentages>_Z-scores.json` to create interactive visualizations 

## Directory Structure:
- [Analysis](https://github.com/olivercalder/sonic-signatures#analysis-details): Scripts and outputs for the analysis of trends in the results of different classifications
- [Archive](https://github.com/olivercalder/sonic-signatures/tree/master/Archive): Saved text, phoneme, counts, and percentages data for a variety of combinations of parameters
- [Naive-Bayes](https://github.com/olivercalder/sonic-signatures#naive-bayes-details): Scripts used to classify characters using Naive Bayes
- [Preprocessing](https://github.com/olivercalder/sonic-signatures#preprocessing-details): Scripts to get character lists and texts from [folgerdigitaltexts.org/api](https://www.folgerdigitaltexts.org/api/) and convert those texts into phonemes, and then count or percentage vectors for each character
- [Reference](https://github.com/olivercalder/sonic-signatures#reference-details): Helper scripts and data used by other scripts to classify characters or generate combinations of parameters
- [Results](https://github.com/olivercalder/sonic-signatures/tree/master/Results): Saved classification results and summaries generated from the count or percentage data in the [Archive](https://github.com/olivercalder/sonic-signatures/tree/master/Archive) using the scripts in [Naive-Bayes](https://github.com/olivercalder/sonic-signatures#naive-bayes-details)
- [Statistics](https://github.com/olivercalder/sonic-signatures#statistics-details): Scripts to generate statistical information (including [Z-scores](https://github.com/olivercalder/sonic-signatures/blob/master/Statistics/z_scores.py)) on phoneme vectors, and to be used by other scripts to yield more informative results regarding classifications
- [Visualization](https://github.com/olivercalder/sonic-signatures#visualization-details): Interactive visualizations to explore statistical and classification data
- [lib](https://github.com/olivercalder/sonic-signatures/tree/master/lib): Libraries (d3v4.js, jQuery, and bootstrap.js)

## Analysis Details:
| Program: | Description: |
|----------|--------------|
| `compare_plays.py` | Uses `classification.py` and `evaluation.py` to perform hold-one-out classification on an entire play, with every character from that play held out from the training data, and then tested once the classifier is built. Provides information about the overall predictability of each play relative to other plays. |
| `option_analysis.py` | Uses a [results file](https://github.com/olivercalder/sonic-signatures/blob/master/Results/role/results_role_overall_sorted.csv) to tally up the average accuracies for each option, such as Emphasis vs non-Emphasis or All vs No-Others. |

## Naive-Bayes Details:
| Program: | Description: |
| `classification.py` | Uses a counts or percentages file to perform hold-one-out classification on each character phoneme vector, constructing a results dictionary containing each character's name, actual class and predicted class. |
| `evaluation.py` | Uses a results dictionary to generate confusion matrices and various other statistics about the success of the classification. |
| `generate_evaluations.py` | Uses count and percentage files stored in the Archive to run `classification.py` and `evaluation.py` on every combination of options, saving the results to Results or the specified directory. |

## Preprocessing Details:
| Program: | Returns: | Writes: | Depends: |
|----------|----------|---------|----------|
| `characters.py` | Set or Dictionary of sets by play | Text or JSON | folgersdigitaltexts.org |
| `texts.py` | Dictionary or Dictionary of dictionaries nested by play | Text or JSON | `characters.py` |
| `phonemes.py` | Dictionary or Dictionary of dictionaries nested by play | Text or JSON | `texts.py` |
| `counts.py` | Nested dictionary (`{char:{phoneme:count, ...}, ...}`) or Dictionary of dictionaries nested by play (`{play:{char{phoneme:count, ...}, ...}, ...}`) | JSON or csv | `phonemes.py` |
| `percentages.py` | Nested dictionary (`{char:{phoneme:percentage, ...}, ...}`) or Dictionary of dictionaries nested by play (`{play:{char{phoneme:percentage, ...}, ...}, ...}`) | JSON or csv | `counts.py` |
| `fast_generate_Archive.py` | N/A | Recursive output of `percentages.py`, and `phonemes.py` with the `-u` flag enabled, run on every combination of options with a new process handling each combination, to the Archive  | `percentages.py`, `phonemes.py` |
| `safe_generate_Archive.py` | N/A | Recursive output of `percentages.py`, and `phonemes.py` with the `-u` flag enabled, run on every combination of options with a new thread handling each combination, to the Archive  | `percentages.py`, `phonemes.py` |

__Command-Line Argument Guidelines__:

| Argument           | Description                                                                                           |
|--------------------|-------------------------------------------------------------------------------------------------------|
| `-h`               | Help: Prints help string                                                                              |
| `-p [play_code]`   | Includes specified play                                                                               |
| `-c [char_code]`   | Includes specified character                                                                          |
| `-ep [play_code]`  | Excludes specified play (overrides conflicting `-p`)                                                  |
| `-ec [char_code]`  | Excludes specified character (overrides conflicting `-c`)                                             |
| `-eo`              | Exclude characters with the role of "other"                                                           |
| `-n`               | Nests the output by play                                                                              |
| `-s`               | Silent (does not print to console)                                                                    |
| `-wt`              | Writes output to file as text (or csv)                                                                |
| `-wj`              | Writes output to file as json                                                                         |
| `-t [title]`       | Specifies title of specified run, to be used in output file names                                     |
| `-d [path/to/dir]` | Specifies directory in which to write output files                                                    |
| `-R`               | Recursively write each subordinate script's output in the same manner as the primary script being run |
| `-u`               | Return unknown words instead of phonemes                                                              |
| `-v`               | Vowels only: ignore consonants when creating phoneme vectors                                          |
| `-e`               | Preserve emphasis marking in phonemes                                                                 |
| `-r`               | Preserve raw text (not recommended beyond `texts.py`                                                  |
| `-m [min_words]`   | Only include characters who have a total word count greater than or equal to the specified word count |

## Reference Details:
| File: | Description: |
|-------|--------------|
| `Play_Codes.txt` | Reference file defining which play each play code refers to. |
| `archive_combinations.py` | Helper script which generates names, directories and parameters for every combination of options found in the Archive and Results directories. |
| `characteristics.csv` | Reference file defining the classes of each character. |

## Statistics Details:
| Program: | Description: |
|----------|--------------|
| `generate_statistics.py` | Runs all other statistics scripts on every combination of options, generated from `archive_combinations.py`. |
| `z_scores.py` | Uses phoneme vectors from a counts or percentages file to generate Z-score vectors. |

## Visualization Details:
The two visualizations, beeswarm and barchart, are built to examine trends in the phoneme usage of characters and classes of characters.
The Z-scores are sourced from files in the Archive specific to the combination of options set in the control panel.

### Control Panel Model Selection:
| Control: | Description: |
|----------|--------------|
| Characters | Change which characters are included in the model, such as by total word count or by class |
| Calculation | Change whether counts or percentages files are used in the model |
| Preserve Emphasis | Toggle whether vowel phonemes are split up by emphasis |
| Vowels Only | Toggle whether consonants are excluded from the model |

### Beeswarm:

Generates beeswarm charts for each phoneme in the dataset, sourced from Z-score files in the Archive.
Each circle represents the Z-score of an individual character for that phoneme, and the color of the circle corresponds to the class of the character with regard to the current classifier.
For example, if the classifier is "role", the possible classes are "protag", "antag", "fool", and "other".
The distribution of circles of different classes can reveal trends for characters of that class, or reveal outliers.

Additionally, average circles can be toggled, displaying a single larger circle for the average Z-score of each class.
The color of the circle corresponds to the class, and the size correlates roughly with the total number of characters from the current model who fit that class.

Hovering the mouse over a circle will display the identity of the character as well as its Z-score, appearing on every chart.
Clicking a circle will toggle its persistent selection, allowing the user to select multiple characters at once and compare their Z-scores more directly.

The user can also filter the charts using the search bar.
Any circles which do not match the search are made transparent, thus allowing the user to focus on a smaller subset of characters at a time.
Any character which is selected will remain opaque, despite filters, thus allowing the user to search for desired characters, select them, and compare them with all other circles made transparent.

#### Beeswarm-Specific Visualization Controls:
| Control: | Description: |
|----------|--------------|
| Show Averages | Overlay average circles onto the visualization, with one circle for each class at an x position corresponding to the average Z-score for that class |
| Classifier | Switch which classifier is being used to color character circles and overlay average circles |
| Filter by | Change whether the search box applies to the name or the class of circles |
| Search box | Filter the beeswarms by making all circles which do not match the search term transparent |

### Barchart:

Generates bar charts for each character in the dataset, sourced from Z-score files in the Archive.
Each bar represents the Z-score for a specific phoneme, with the height of the bar scaled based upon the score.
Positive bars (and thus Z-scores) show that the character uses that phoneme more than average, and negative bars show that the character uses that phoneme less than average.

The color of the bars corresponds to the class of the character with respect to the current classifier.
Additionally, averages for the class can be overlayed atop the existing colored bars, allowing the user to compare all of the character's phonemes to the averages for its class.

#### Barchart-Specific Visualization Controls:
| Control: | Description: |
|----------|--------------|
| Show Averages | Overlay average bars onto the visualization, allowing a direct comparison between the Z-scores of each character and averages for that character's class |
| Classifier | Switch which classifier is being used to color Z-score bars and overlay averages |
| Sort by | Change the order in which charts appear on the screen |
| Search box | Filter the bar charts to show only those whose names include the search term |
