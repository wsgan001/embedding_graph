## this tests the libHIN

from libHIN.IO import load_hinmine_object, generate_cv_folds  ## gml_parser
from libHIN.embeddings import hinmine_embedding ## basic embedding
from libHIN.decomposition import * ## basic embedding
from dataloaders import read_rfa, read_bitcoin, read_web
from libHIN.label_propagation import *
import networkx as nx
import numpy as np

def decompose_test(fname, delim):

    example_net = load_hinmine_object(fname,delim) ## add support for weight
    
    ## split and re-weight
    print("Beginning decomposition..")

    # c2 = ["movie_____features_____person_____acts_in_____movie"]
   
    decomposed = hinmine_decompose(example_net,heuristic="idf", cycle=None, parallel=True)
    
    ## embedding
    print("Starting embedding..")
    embedding = hinmine_embedding(decomposed, parallel=True,verbose=True)
    print(embedding)
        
    return embedding

def test_classification(graph,delimiter):

    ## CV classification
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.dummy import DummyClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score
    from sklearn.metrics import accuracy_score
    from sklearn.naive_bayes import GaussianNB
    from sklearn.ensemble import AdaBoostClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.svm import LinearSVC
    from sklearn.neighbors import KNeighborsClassifier


    classifiers = {'rf' : RandomForestClassifier(n_estimators=100, random_state=1),
                   'dummy' : DummyClassifier(strategy='most_frequent',random_state=13),
                    'nb' : GaussianNB(),
                   'ada' : AdaBoostClassifier(n_estimators=500),
                   'SVC' : LinearSVC(random_state=0),
                   'MLP' : MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(8, 5,3,2), random_state=13),
                   'knn' : OneVsRestClassifier(KNeighborsClassifier(n_neighbors=10))}

    ## result container

    embedding = decompose_test(graph,delimiter)
    
    results = []
    for k,v in classifiers.items():

        v = OneVsRestClassifier(v)
        scores = cross_val_score(v, embedding['data'], embedding['targets'], cv=5, scoring='f1_weighted',n_jobs=4)        
        results.append((k,np.mean(scores)))
        
    results= sorted(results, key=lambda tup: tup[1])
    for x in results:
        cls, score = x
        print("Classifier: {} performed with score of {}".format(cls,score))

    print("Finished test 2 - classification")


def test_automl(graph, delimiter):

    import autosklearn.classification
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score
    
    classifiers = {'autoML' :autosklearn.classification.AutoSklearnClassifier(per_run_time_limit=15, time_left_for_this_task=1200)}

    ## result container
    embedding = decompose_test(graph,delimiter)
    
    results = []
    for k,v in classifiers.items():

        v = OneVsRestClassifier(v)
        scores = cross_val_score(v, embedding['data'], embedding['targets'], cv=5, scoring='f1_weighted')        
        results.append((k,np.mean(scores)))
        
    results= sorted(results, key=lambda tup: tup[1])
    for x in results:
        cls, score = x
        print("Classifier: {} performed with score of {}".format(cls,score))

    print("Finished test 2 - classification")

def test_rnn(graph, delimiter):

    from sklearn.model_selection import StratifiedKFold
    from keras.models import Sequential
    from keras.layers import Dense, Dropout
    from sklearn.model_selection import KFold
    from sklearn.metrics import f1_score
    embedding = decompose_test(graph,delimiter)
    cvscores = []

    X = embedding['data']
    Y = embedding['targets']
    print(X.shape,Y.shape)
    kf = KFold(n_splits=10,random_state=None, shuffle=False)
    for train, test in kf.split(X):
        # create model
        model = Sequential()
        model.add(Dense(X.shape[1], input_dim=X.shape[1], activation='relu'))
        model.add(Dense(200, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(50,activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(40,activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(30, activation='relu'))
        model.add(Dense(Y.shape[1], activation='sigmoid'))
        # Compile model
        model.compile(loss='binary_crossentropy', optimizer='adam')
        # Fit the model
        model.fit(X[train], Y[train], epochs=300, batch_size=40, verbose=1)
        # evaluate the model
        preds = model.predict(X[test])
        preds[preds>=0.5] = 1
        preds[preds<0.5] =  0
        cvscores.append(f1_score(Y[test], preds, average='weighted'))
        
    print("Mean F1: {} and std: {}".format(np.mean(cvscores),np.std(cvscores)))
    
def test_embedding_raw():

    ## test simple embedding
    simple_net = load_hinmine_object("../data/example_weighted.txt", targets=False) ## embed only
    embedding = hinmine_embedding(simple_net,use_decomposition=False, parallel=8,verbose=True)

def test_embedding_prediction():
    ## do embedding + prediction
    pass

def test_label_propagation():

    example_net = load_hinmine_object("../data/imdb_gml.gml","---") ## add support for weight
    ## split and re-weight
    print("Beginning decomposition..")   
    decomposed = hinmine_decompose(example_net,heuristic="idf", cycle=None)
    print("Beginning label propagation..")
    pmat = run_label_propagation(decomposed,weights="balanced")
    print(pmat)


def test_writing(fname,delim,outname):

    example_net = load_hinmine_object(fname,delim) ## add support for weight
    embedding = hinmine_embedding(example_net, parallel=True,verbose=True,use_decomposition=False,return_type="file",outfile=outname)
    
    pass


def parse_mat(fname, delim):

    ## direct decomposition
    example_net = load_hinmine_object(fname,delim) ## add support for weight
    embedding = hinmine_embedding(example_net, parallel=True,verbose=True,use_decomposition=False,from_mat=True)

    print("Trainset dimension {}, testset dimension {}.".format(embedding['data'].shape,embedding['targets'].shape))

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.multiclass import OneVsRestClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.dummy import DummyClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score
    from sklearn.metrics import accuracy_score
    from sklearn.naive_bayes import GaussianNB
    from sklearn.ensemble import AdaBoostClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.svm import LinearSVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.naive_bayes import BernoulliNB

    # classifiers = {'rf' : RandomForestClassifier(n_estimators=100, random_state=1),
    #                'dummy' : DummyClassifier(strategy='most_frequent',random_state=13),
    #                'nb' : GaussianNB(),
    #                'ada' : AdaBoostClassifier(n_estimators=500),
    #                'LR' : LogisticRegression( penalty='l1', tol=0.01),
    #                'SVC' : LinearSVC(random_state=0),
    #                'MLP' : MLPClassifier(solver='lbfgs', alpha=1e-5,hidden_layer_sizes=(8, 5,3,2), random_state=13),
    #                'knn' : OneVsRestClassifier(KNeighborsClassifier(n_neighbors=10))}


    from sklearn.model_selection import ShuffleSplit
    import scipy.io as spi

#    data = spi.loadmat("../data/Homo_sapiens.mat")
#    print(data)
#    embedding['data'] = data['network']
#    embedding['targets'] = data['group']
    
    ## 10 splits 50% train
    
    rs = ShuffleSplit(n_splits=5, test_size=0.5, random_state=0)    
            
    results = []

    v = LogisticRegression(penalty='l2')
    v = OneVsRestClassifier(v)

    scores = []
    batch = 0
    
    for train_index, test_index in rs.split(embedding['data'],embedding['targets']):

        batch += 1
        print("Fold: {}".format(batch))
        train_X = embedding['data'][train_index,]
        train_Y = embedding['targets'][train_index,]
        test_X = embedding['data'][test_index,]
        test_Y = embedding['targets'][test_index,]
        model_preds = v.fit(train_X,train_Y).predict(train_X)
        sc = f1_score(train_Y, model_preds, average='macro')
        scores.append(sc)
            
    results.append(("LR",np.mean(scores)))
        
    results= sorted(results, key=lambda tup: tup[1])
    for x in results:
        cls, score = x
        print("Classifier: {} performed with score of {}".format(cls,score))

    print("Finished test - classification basic")
    

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--test_classification")
    parser.add_argument("--test_automl")
    parser.add_argument("--decompose_test")
    parser.add_argument("--test_label_prop")
    parser.add_argument("--graph")
    parser.add_argument("--delimiter")
    parser.add_argument("--test_rnn")
    parser.add_argument("--frommat")
    parser.add_argument("--test_write")
    
    args = parser.parse_args()

    if args.test_label_prop:
        test_label_propagation()
            
    if args.decompose_test:
        decompose_test(args.decompose_test," ")
        
    if args.test_classification:
        test_classification(args.graph,args.delimiter)

    if args.test_automl:
        test_automl(args.graph,args.delimiter)
        
    if args.test_rnn:
        test_rnn(args.graph, "---")

    if args.frommat:
        parse_mat(args.graph, " ")
    if args.test_write:
        test_writing(args.graph, " ","test.emb")
