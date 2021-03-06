import logging
import init_django_env
from stanfordcorenlp import StanfordCoreNLP
from django.db.models import Q
from data_process.models import (
    SemEval2010Data, SemEval2010Relation
)
from activation_force import get_word_frequency_dict
from utils import (
    get_relation_trigger_seed, get_trigger_idx_list_by_waf,
    calculate_accuracy
)




stanford_path = r'/Users/wanglei/Documents/programs/other/stanford-corenlp-full-2018-02-27'
# 259 22
data_list = SemEval2010Data.objects.filter(~Q(trigger_words=''))

with StanfordCoreNLP('http://127.0.0.1', 9000, logging_level=logging.WARNING) as nlp:
    for data in data_list:
        data.word_list = nlp.word_tokenize(data.sent)
        data.postag_list = nlp.pos_tag(data.sent)
        data.dependency_tree = nlp.dependency_parse(data.sent)


word_frequency_dict = get_word_frequency_dict(data_list)


for data in data_list:
    data.trigger_seed = get_relation_trigger_seed(
        data.word_list, data.postag_list, data.dependency_tree, data.entity1_idx, data.entity2_idx,
        beta=0.5
    )
    data.trigger_list = get_trigger_idx_list_by_waf(
        data.word_list, data.trigger_seed, data.entity1_idx, data.entity2_idx, data_list, word_frequency_dict, data.postag_list
    )

micro_accuracy = calculate_accuracy(data_list)
macro_accuracy = calculate_accuracy(data_list, 'macro')
seed_micro_accuracy = calculate_accuracy(data_list, 'seed_micro')
seed_macro_accuracy = calculate_accuracy(data_list, 'seed_macro')
seed_first_accuracy = calculate_accuracy(data_list, 'seed_first')

print('触发词种子微准确率：', seed_micro_accuracy)
print('触发词种子宏准确率：', seed_macro_accuracy)
print('触发词整体微准确率：', micro_accuracy)
print('触发词整体宏准确率：', macro_accuracy)
print('触发词种子为第一触发词概率：', seed_first_accuracy)


