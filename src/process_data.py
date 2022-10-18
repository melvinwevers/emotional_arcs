from bs4 import BeautifulSoup as bs
import spacy
import os
import glob
import argparse
import json
import unicodedata
from itertools import chain


# print('downloading spacy model')
# os.system("curl -0L https://github.com/explosion/spacy-models/releases/download/nl_core_news_sm-3.2.0/nl_core_news_sm-3.2.0.tar.gz | tar -xz")

nlp = spacy.load('nl_core_news_sm', disable=['ner', 'tagger', 'parser'])

nlp.add_pipe('sentencizer')


def load_files(input_path):
    return glob.glob(os.path.join(input_path, '*.xml'))

def read_xml(doc_path):
    with open(doc_path, 'r') as file:
        content = file.readlines()
        content = ''.join(content)
        bs_content = bs(content, "lxml")
    return bs_content

def strip_accents(text):
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    return text.decode("utf-8")

def get_chunks(s, maxlength):
    start = 0
    end = 0
    while start + maxlength  < len(s) and end != -1:
        end = s.rfind(" ", start, start + maxlength + 1)
        yield s[start:end]
        start = end +1
    yield s[start:]


def extract_text(content):
    #raw_text = ' '.join([x.get_text(separator=' ', strip=True) \
    #                    for x in content.find_all('div', {'type': 'chapter'})])

    book_text = [] 
    for chapter in content.find_all('div', {'type': 'chapter'}):
        chapter_text = []
        for p in chapter.findAll('p'):
            chapter_text.append(p.get_text(separator=' ', strip=True))
        chapter_raw = ' '.join(chapter_text)
        # making chunks to circumvent the max_length limit in spacy
        # then we use generator object to go through chunks 
        # and use chain.from_iterable to flatten nested list
        chapter_chunks = get_chunks(chapter_raw, maxlength=100000)
        doc_list = [nlp(chunk) for chunk in chapter_chunks]
        lemmatized_sentences = list(chain.from_iterable([[sentence.lemma_ for sentence in doc.sents] for doc in doc_list]))
        chapter_processed = [[strip_accents(word) for word in sentence.split()] for sentence in lemmatized_sentences]
        book_text.append(chapter_processed)
    return book_text

def write_output(text, file_, output_path):
    filename = os.path.basename(file_)[:-4] + '.json'
    #print(filename)

    with open(os.path.join(output_path, filename), "w") as jsonfile:
        json.dump(text, jsonfile)

def prepare_text(file_):
    xml_content = read_xml(file_)
    book_text = extract_text(xml_content)

    #doc = nlp(raw_text)
    #lemmatized_sentences = [sentence.lemma_ for sentence in doc.sents]

    # turn this into a nested list of lemmas in sentence in sentences
    #output_text = [[word for word in sentence.split()] for sentence in lemmatized_sentences]
    return book_text

def pre_process(input_path, output_path):
    files_ = load_files(input_path)
    print(f'there are {len(files_)} files')
    for file_ in files_:
        # to do: skip if output already exists
        text = prepare_text(file_)
        write_output(text, file_, output_path)
