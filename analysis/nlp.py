# (setq python-shell-interpreter "./venv/bin/python")

import pandas as pd

import re

import numpy as np

import matplotlib
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.feature_extraction import stop_words
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

# files and categories to read in 
names_and_cats = [("islamqa.csv", "islamqa"),
                  ("sistani.csv", "sistani"),
                  ("eshaykh.csv", "eshaykh"),
                  ("islamweb.csv", "islamweb"),
                  ("darulifta.csv", "darulifta"),
                  ("aboutislam.csv", "aboutislam")]


category_names = []
file_dfs = []
# read in the files and assign categories
for filename, cat in names_and_cats:
    csv_df = pd.read_csv("data/" + filename)
    csv_df["category"] = cat

    file_dfs.append(csv_df)
    category_names.append(cat)
    
all_df = pd.concat(file_dfs, ignore_index=True)



def remove_urls(string): 
    # findall() has been used  
    # with valid conditions for urls in string 
    url = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', " ", string)
    url = re.sub('www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', " ", url)
    url = re.sub("\(Fatwa:.+\)","", url)
    return ''.join([i if ord(i) < 128 else ' ' for i in url])





# clean data
for col in ["question", "answer"]:
    all_df[col] = [re.sub(" +", " ",
                        # re.sub("^\(Fatwa:.+\)","",
remove_urls(
                          x
                          .replace("Allaah", "Allah")
                          .replace("ã", "a")
                          .replace("\n", " ")
                          .replace("\t", " ")
                          .replace("\xa0", " ")
                          .replace("www.aicchicago.com", " ")
                          .replace("www.imamsenadagic.com", " ")
                          .replace("www.iabna.org", " ")
                          .strip()
                                                                                                                             ).strip()
                          # .replace("Praise be to Allah.", " ")
                          # .replace("And Allah knows best.", " ")
                          # .replace("Allah knows best.", " ")
                          # .replace("Allah Alighty knows best.", " ")
                          # .replace("All perfect praise be to Allah, The Lord of the Worlds. I testify that there is none worthy of worship except Allah and that Muhammad, sallallaahu ʻalayhi wa sallam, is His slave and Messenger.", " ")
                          # .replace("Editor’s note: This fatwa is from Ask the Scholar’s archive and was originally published at an earlier date.", " ")
                          # .replace("Allah knows Best! Darul Ifta,Darul Uloom Deoband", " ")
                          # .replace("بسم الله الرحمن الرحيم", " ")
                        ).strip()
                   for x in all_df[col]]

all_df = all_df.sample(frac=1, random_state=42)


train_df = all_df.sample(frac=0.7, random_state=42)
test_df = all_df.drop(train_df.index)

train_docs = [row["question"] + " " + row["answer"]
              for index, row in train_df.iterrows()]
train_categories = train_df["category"]

test_docs = [row["question"] + " " + row["answer"]
              for index, row in test_df.iterrows()]
test_categories = test_df["category"]




# multinomialnb pipeline
text_clf = Pipeline([
    ('vect', CountVectorizer(ngram_range=(1,2), stop_words=stop_words.ENGLISH_STOP_WORDS)),
    ('tfidf', TfidfTransformer()),
    ('clf', MultinomialNB()),
])

text_clf.fit(train_docs, train_categories)
predicted = text_clf.predict(test_docs)
# near perfect accuracy??? =====================================================
print("multinomialnb model accuracy:", np.mean([pred == target for (pred, target) in zip(predicted, test_categories)]))



# sgd pipeline
text_clf2 = Pipeline([
    ('vect', CountVectorizer(ngram_range=(1,2), stop_words=stop_words.ENGLISH_STOP_WORDS)),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier(max_iter=100, tol=1e-3)),
])

text_clf2.fit(train_docs, train_categories)
predicted2 = text_clf2.predict(test_docs)
# perfect accuracy??? ===========================================================
print("SGDClassifier model accuracy:", np.mean([pred == target for (pred, target) in zip(predicted2, test_categories)]))

from sklearn.metrics import classification_report

print(classification_report(test_categories, predicted))


# functions to create plots
# https://buhrmann.github.io/tfidf-analysis.html
def top_tfidf_feats(row, features, top_n=25):
    ''' Get top n tfidf values in row and return them with their corresponding feature names.'''
    topn_ids = np.argsort(row)[::-1][:top_n]
    top_feats = [(features[i], row[i]) for i in topn_ids]
    df = pd.DataFrame(top_feats)
    df.columns = ['feature', 'tfidf']
    return df

def top_feats_in_doc(Xtr, features, row_id, top_n=25):
    ''' Top tfidf features in specific document (matrix row) '''
    row = np.squeeze(Xtr[row_id].toarray())
    return top_tfidf_feats(row, features, top_n)


def top_mean_feats(Xtr, features, grp_ids=None, min_tfidf=0.1, top_n=25):
    ''' Return the top n features that on average are most important amongst documents in rows
        indentified by indices in grp_ids. '''
    if grp_ids:
        D = Xtr[grp_ids].toarray()
    else:
        D = Xtr.toarray()

    D[D < min_tfidf] = 0
    tfidf_means = np.mean(D, axis=0)
    return top_tfidf_feats(tfidf_means, features, top_n)

def top_feats_by_class(Xtr, y, features, min_tfidf=0.1, top_n=25):
    ''' Return a list of dfs, where each df holds top_n features and their mean tfidf value
        calculated across documents with the same class label. '''
    dfs = []
    labels = np.unique(y)
    for label in labels:
        ids = np.where(y==label)
        feats_df = top_mean_feats(Xtr, features, ids, min_tfidf=min_tfidf, top_n=top_n)
        feats_df.label = label
        dfs.append(feats_df)
    return dfs


def plot_tfidf_classfeats_h(dfs):
    ''' Plot the data frames returned by the function plot_tfidf_classfeats(). '''
    fig = plt.figure(figsize=(25, 9), facecolor="w")
    x = np.arange(len(dfs[0]))
    for i, df in enumerate(dfs):
        ax = fig.add_subplot(1, len(dfs), i+1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_frame_on(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()
        ax.set_xlabel("Mean Tf-Idf Score", labelpad=16, fontsize=14)
        ax.set_title("label = " + str(df.label), fontsize=16)
        ax.ticklabel_format(axis='x', style='sci', scilimits=(-2,2))
        ax.barh(x, df.tfidf, align='center', color='#3F5D7D')
        ax.set_yticks(x)
        ax.set_ylim([-1, x[-1]+1])
        yticks = ax.set_yticklabels(df.feature)
        plt.subplots_adjust(bottom=0.09, right=0.97, left=0.15, top=0.95, wspace=0.52)
    plt.show()



count_vect = CountVectorizer(ngram_range=(1,2), stop_words=stop_words.ENGLISH_STOP_WORDS)

X_train_counts = count_vect.fit_transform(train_docs)

tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

dfs = top_feats_by_class(X_train_tfidf, train_categories, count_vect.get_feature_names())
plot_tfidf_classfeats_h(dfs)


# for one document
# top_feats_in_doc(X_train_tfidf, count_vect.get_feature_names(), 2)

categories = [y for x,y in names_and_cats]

tfidf_df = pd.DataFrame()
dfs_copy = dfs.copy()
for i in range(len(categories)):
    dfs_copy[i]["category"] = dfs_copy[i].label


pd.concat(dfs_copy).to_csv("tfidf-by-site.csv")




for index, row in all_df[all_df["category"] == "eshaykh"].reset_index().iterrows():
    if "www" in row["answer"]:
        print(row["answer"])


        
