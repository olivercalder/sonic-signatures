# sonic-signatures
Machine learning and data visualization research into phoneme patterns of authors.

### Researchers:
- Eric Alexander _Supervisor_
- Oliver Calder

## Contents:
- `get_characters.py`: Returns a set of character codes from folgersdigitaltexts.org
  - [Description](https://github.com/olivercalder/sonic-signatures#get_characterspy)
  - [Usage](https://github.com/olivercalder/sonic-signatures#Usage)

### Dependencies:
- Python 3
- Libraries:
  - requests
  - bs4
  - json
  - nltk
  - scikit-learn
  - numpy
  - scipy
  - matplotlib

## General Flow:
| Program: | Returns: | Writes: | Depends: |
|----------|----------|---------|----------|
| `get_characters.py` | Set or Dictionary or sets by play | Text or JSON | folgersdigitaltexts.org |
| `get_texts.py` | Dictionary or Dictionary of dictionaries by play | Text or JSON | `get_characters.py` |
| `get_phonemes.py` | Dictionary or Dictionary of dictionaries by play | Text or JSON | `get_texts.py`, `get_characters.py` |
| `count_phonemes.py` | Nested dictionary (`{char:{phoneme:count, ...}, ...}`) or Dictionary of nested dictionaries by play (`{play:{char{phoneme:count, ...}, ...}, ...}`) | `get_phonemes.py`, `get_texts.py`, `get_characters.py` |

### `get_characters.py`
