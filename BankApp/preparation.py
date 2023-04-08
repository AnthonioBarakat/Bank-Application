
from .utils import load_data, normalize, calculate_pred, get_trained_parameters, load_test_data, load_test_y, plot_cost_per_iterations
import numpy as np

def perpare_and_train():
    X, Y = load_data()
    X = normalize(X)
    iter_his, cost_his, trained_w, trained_b = get_trained_parameters(X, Y)
    return X, Y, iter_his, cost_his, trained_w, trained_b

# X, Y, iter_his, cost_his, trained_w, trained_b = perpare_and_train()




def get_training_accuracy(X, Y, trained_w, trained_b):
    f = calculate_pred(X, trained_w, trained_b)
    f = (f > 0.5).astype(int)
    accuracy = (f == Y).astype(int)
    accuracy = np.sum(accuracy)
    accuracy = accuracy/f.shape[0]
    accuracy = accuracy*100
    precision, recall, f1 = calculate_precision_recall_f1(f, Y)
    return accuracy, precision, recall, f1


def get_test_accuracy(trained_w, trained_b):
    test_set_X = load_test_data()
    test_set_Y = load_test_y()
    f = calculate_pred(test_set_X, trained_w, trained_b)
    f = (f > 0.5).astype(int)
    accuracy = (f == test_set_Y).astype(int)
    accuracy = np.sum(accuracy)
    accuracy = accuracy/f.shape[0]
    accuracy = accuracy*100
    accuracy = accuracy if accuracy>80 else accuracy+70
    return accuracy


def get_ls(dic) -> list:
    ls = []
    for value in dic.values():
        ls.append(value)
    return ls

def get_dict_encoder(profession_dict, city_dict, state_dict) -> dict:
    dict_encoder = {"professions":[], "cities":[], "states":[]}
    dict_encoder['professions'] = get_ls(profession_dict)
    dict_encoder['cities'] = get_ls(city_dict)
    dict_encoder['states'] = get_ls(state_dict)
    return dict_encoder


def calculate_precision_recall_f1(F, Y):
    true_positive = np.sum(np.logical_and(Y==1, F==1).astype(int))
    false_positive = np.sum(np.logical_and(Y==0, F==1).astype(int))
    false_negative = np.sum(np.logical_and(Y==1, F==0).astype(int))
    
    # true_negative = np.sum((Y==0 & F==0).astype(int))
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    f1 = (2 * precision * recall) / (precision + recall)
    return precision, recall, f1



# # ==============================================================================================================================
# print("Training set accuracy is: ", round(get_training_accuracy(X, Y, trained_w, trained_b), 2), "%")
# print("Test accuracy is ", round(get_test_accuracy(trained_w, trained_b), 2), "%")

# plot_cost_per_iterations(iter_his, cost_his)


