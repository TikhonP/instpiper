from difflib import get_close_matches, SequenceMatcher
from transliterate import translit
import re
from transliterate.exceptions import LanguageDetectionError
import numpy as np
import os


emoji_pattern = re.compile('['
                           u'\U0001F600-\U0001F64F'
                           u'\U0001F300-\U0001F5FF'
                           u'\U0001F680-\U0001F6FF'
                           u'\U0001F1E0-\U0001F1FF'
                           ']+', flags=re.UNICODE)

dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'names/yob2018.txt')
with open(filename, 'r') as f:
    ddata = f.read()

ddata = ddata.split(sep='\n')
data = []
for line in ddata:
    if line == '':
        continue
    data.append(line.split(sep=','))
m = np.mean([int(i[2]) for i in data])
patterns = [i[0] for i in data]


def splits(txt, seps):
    default_sep = seps[0]

    # we skip seps[0] because that's the default separator
    for sep in seps[1:]:
        txt = txt.replace(sep, default_sep)
    return [i.strip() for i in txt.split(default_sep)]


def returnmatches(name):
    matshes = get_close_matches(name, patterns)
    if len(matshes) > 0:
        for i, n in enumerate(matshes):
            score = SequenceMatcher(None, name, n).ratio()
            matshes[i] = (n, score)
            break
        return matshes
    else:
        return None


def translitt(s):
    s = emoji_pattern.sub(r'', s)
    try:
        return translit(s, reversed=True)
    except LanguageDetectionError:
        return s


def scores(matshes):
    scores = [['M', 0], ['F', 0]]
    for i in matshes:
        if i[0] == 'M':
            scores[0][1] += i[2]
        elif i[0] == 'F':
            scores[1][1] += i[2]
    scores = sorted(scores, key=lambda l: l[1], reverse=True)
    return (scores[0][0], scores[0][1])


def closeMatches(name):
    name = translitt(name)
    names = splits(name, ('_', '.', '-', ' ', '1', '2', '3', '4',
                          '5', '6', '7', '8', '9', '0'))
    matshes = []
    for n in names:
        matsh = returnmatches(n)
        if matsh is None:
            continue
        gender = data[patterns.index(matsh[0][0])]
        if matsh[0][1] < 0.80:
            continue
        matshes.append((gender[1], matsh[0][0], matsh[0][1]))
    true_gender = scores(matshes)
    if matshes == []:
        return None
    else:
        return true_gender


if __name__ == '__main__':
    from datetime import datetime
    import sys
    if len(sys.argv) == 1:
        print('Usage: python parsenames.py <name>')
        sys.exit()
    start_time = datetime.now()
    print(closeMatches(sys.argv[1]))
    print(datetime.now() - start_time)
