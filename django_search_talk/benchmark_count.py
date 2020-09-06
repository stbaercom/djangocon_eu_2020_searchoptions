
from django_search_app_load import read_entry

from collections import  Counter
import re

def main(fn):
    count = Counter()
    for entry in read_entry(fn):
        for f in ['review_summary', 'review_text']:
            tokens = [t for t in re.split(r"\W",entry[f].lower()) if t]
            count.update(tokens)
    words = count.most_common(2000)[50:2000:50]
    with open("words.txt", mode="w", encoding="utf-8") as out:
        for k,_ in words:
            out.write(f"{k}\n")


if __name__ == '__main__':
    main('movies_100k.txt')