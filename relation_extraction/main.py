import os
import sys
import pickle as pkl
import numpy as np


pwd = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(pwd))

import init_django_env
from data_process.models import SemEval2010Data
from stanfordcorenlp import StanfordCoreNLP
from relation_extraction.utils import MyWord2VecPKL, generate_x_y
from relation_extraction.model import BiLstmAttr
from mytools.word_preprocessing import MultyProcessWordPreprocessing


# stanford_ip_port_list = [('49.140.78.189', 9000), ('127.0.0.1', 9000)]
stanford_ip_port_list = [('127.0.0.1', 9000)]


def get_processed_train_test_datalist():
    train_data_file = os.path.join(pwd, 'pkl', 'train_data.pkl')
    test_data_file = os.path.join(pwd, 'pkl', 'test_data.pkl')
    if os.path.exists(train_data_file) and os.path.exists(test_data_file):
        return pkl.load(open(train_data_file, 'rb')), pkl.load(open(test_data_file, 'rb'))
    train_data_list = SemEval2010Data.objects.filter(is_train=True)
    test_data_list = SemEval2010Data.objects.filter(is_train=False)
    train_data_list = MultyProcessWordPreprocessing(stanford_ip_port_list, train_data_list).get_processed_data()
    test_data_list = MultyProcessWordPreprocessing(stanford_ip_port_list, test_data_list).get_processed_data()
    pkl.dump(train_data_list, open(train_data_file, 'wb'))
    pkl.dump(test_data_list, open(test_data_file, 'wb'))
    return train_data_list, test_data_list



def main():
    model_file = os.path.join(pwd, 'pkl', 'bilstm_attr_model.h5')
    train_datalist, test_datalist = get_processed_train_test_datalist()
    myword2vecpkl = MyWord2VecPKL.getMyWord2vecPKL()
    max_words = 100
    train_X, train_y = generate_x_y(train_datalist, myword2vecpkl, max_words)
    test_X, test_y = generate_x_y(test_datalist, myword2vecpkl, max_words)
    config = {
        'max_words': max_words,
        'word_num': myword2vecpkl.word_num,
        'word_dim': myword2vecpkl.word_dim,
        'embedding_matrix': myword2vecpkl.embedding_matrix,
        'n_classes': 10,
        'learning_rate': 1e-3,
        'batch_size': 200,
        'dropout': 0.5,
        'epoches': 50,
        'digits': 4,
        'verbose': True,
    }

    model = BiLstmAttr(config, model_file=model_file)
    model.fit(train_X, train_y)
    model.predict(test_X, test_y)
    print(model.classify_report)


if __name__ == "__main__":
    main()
    