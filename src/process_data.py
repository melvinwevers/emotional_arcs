from bs4 import BeautifulSoup as bs
import spacy
import os
import glob
import argparse
import json
import unicodedata

nlp = spacy.load('nl_core_news_sm', disable=['ner', 'tagger', 'parser'])
nlp.add_pipe('sentencizer')
nlp.max_length = 1500000

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

def extract_text(content):
    #raw_text = ' '.join([x.get_text(separator=' ', strip=True) \
    #                    for x in content.find_all('div', {'type': 'chapter'})])

    list_txt = []
    for chapter in content.find_all('div', {'type': 'chapter'}):
        for p in chapter.findAll('p'):
            list_txt.append(p.get_text(separator=' ', strip=True))
    raw_text = strip_accents(' '.join(list_txt))
    return raw_text

def write_output(text, file_, output_path):
    filename = os.path.basename(file_)[:-4] + '.json'
    print(filename)

    with open(os.path.join(output_path, filename), "w") as jsonfile:
        json.dump(text, jsonfile)

def prepare_text(file_):
    xml_content = read_xml(file_)
    raw_text = extract_text(xml_content)

    doc = nlp(raw_text)
    lemmatized_sentences = [sentence.lemma_ for sentence in doc.sents]

    # turn this into a nested list of lemmas in sentence in sentences
    output_text = [[word for word in sentence.split()] for sentence in lemmatized_sentences]
    return output_text

def pre_process(input_path, output_path):
    print(input_path)
    files_ = load_files(input_path)

    for file_ in files_:
        print(file_)
        text = prepare_text(file_)
        write_output(text, file_, output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str)
    parser.add_argument('--output_path', default = '../data/prepared_data', type=str)
    args = parser.parse_args()

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)
    
    pre_process(args.input_path, args.output_path)
