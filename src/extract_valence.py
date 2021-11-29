import pandas as pd
import json
import numpy as np
import argparse
import os
import glob


def prepare_df():
    df = pd.read_csv('../data/emotion_lexicons/nrc/NRC_dutch.csv')
    df.drop_duplicates(subset=['Dutch (nl)'], keep='first', inplace=True)
    conditions = [
        (df['Positive'] == 0) & (df['Negative'] == 0),
        (df['Positive'] == 1) & (df['Negative'] == 0),
        (df['Positive'] == 0) & (df['Negative'] == 1)]

    choices = [0, 1, -1]

    df['valence'] = np.select(conditions, choices)
    return df

def sentence_polarity(sentence, normalize=True):
    valence = 0
    for word in sentence:
        try:
            val_score = df[df['Dutch (nl)'] == word]['valence'].values[0]
            valence += val_score
        except:
            pass
    if normalize:
        return valence / len(sentence)
    else:
        return valence

def load_files(input_path):
    return glob.glob(os.path.join(input_path, '*.json'))
    

def calculate_book_polarity(book_path, output_path, df, normalize=True):
    with open(book_path, 'r') as j:
        contents = json.loads(j.read())
    
    print(book_path)
    d = {}
    for index, chapter in enumerate(contents):
        print(f'chapter: {index}')
        valence_chapter = []
        for sentence in chapter:
            if len(sentence) > 0:
                valence_chapter.append(sentence_polarity(sentence, normalize=True))
        d[index] = valence_chapter

    
    #concat entire series
    time_series = sum(d.values(), [])

    filename = os.path.basename(book_path)[:-4] + 'csv'
    output_file_path = os.path.join(output_path, filename)

    pd.DataFrame(time_series).T.to_csv(output_file_path, header=False)

    #todo: add index for chapter to include vlines



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # to do add argument for different emotion lexicons. 
    parser.add_argument('--input_path', type=str)
    parser.add_argument('--output_path', type=str, default='../data/emotion_data')
    parser.add_argument('--normalize', default = True, type=bool)

    args = parser.parse_args()

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    df = prepare_df()
    print(df)
    
    files_ = load_files(args.input_path)

    for file_ in files_:
        calculate_book_polarity(file_, args.output_path, df, normalize=True)