import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, StandardScaler

def get_label_encoded():
    df = pd.read_csv('./BankApp/data/TrainingData.csv')
    le = LabelEncoder()
    df['Profession'] = le.fit_transform(df['Profession'])
    # keep track of the string and their corresponding value using dict
    profession_dict = dict(zip(le.transform(le.classes_), le.classes_))

    df['CITY'] = le.fit_transform(df['CITY'])
    city_dict = dict(zip(le.transform(le.classes_), le.classes_))

    df['STATE'] = le.fit_transform(df['STATE'])
    state_dict = dict(zip(le.transform(le.classes_), le.classes_))
    
    return profession_dict, city_dict, state_dict


def load_data():
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv('./BankApp/data/TrainingData.csv')
    df['Married/Single'] = df['Married/Single'].replace({'single': 0, 'married': 1})
    df['House_Ownership'] = df['House_Ownership'].replace({'norent_noown': 0, 'owned':1, 'rented': 2})
    df['Car_Ownership'] = df['Car_Ownership'].replace({'no': 0, 'yes':1})
    df = df.drop('Id', axis=1)
    # Print the first few rows of the DataFrame
    le = LabelEncoder()
    df['Profession'] = le.fit_transform(df['Profession'])
    df['CITY'] = le.fit_transform(df['CITY'])
    df['STATE'] = le.fit_transform(df['STATE'])

    

    # df.to_csv('new_filename.csv', index=False)
    DATA_SET = df.values


    return DATA_SET[:, :11], DATA_SET[:, -1].reshape(-1, 1)
    # print(df.dtypes)

def intialize_parameters(num_of_features):
    w = np.random.randn(num_of_features, 1) * np.sqrt(2./num_of_features)
    b = np.zeros((1, 1))
    return w, b

def normalize(matrix):
    scaler = StandardScaler()
    X_train_norm = scaler.fit_transform(matrix)
    return X_train_norm

def calculate_pred(X, w, b, is_sigmoid=True):
    z = np.dot(X, w) + b
    # z = np.clip(z, -5, 5)
    if is_sigmoid:
        g = 1/(1+np.exp(-z))
        return g
    return z


def compute_cost(X, Y, w, b, lambda_=2):
    number_of_examples = X.shape[0]
    f = calculate_pred(X, w, b)
    j = np.sum(Y * np.log(f) + (1 - Y) * np.log(1 - f)) / (-number_of_examples)
    reg_term = np.sum(w**2, axis=0)
    reg_term = (lambda_ * reg_term) / (2 * number_of_examples)
    return j + reg_term

def calculate_derivatives(X, Y, w, b, lambda_=2):
    number_of_examples = X.shape[0]
    f = calculate_pred(X, w, b)
    dw = np.sum((f - Y) * X) / number_of_examples
    reg_term = (lambda_ * w) / number_of_examples
    dw = dw + reg_term
    db = np.sum(f - Y)/ number_of_examples
    return dw, db

def fit(X, Y, w, b, learning_rate=0.1, iterations = 700):
    j_history = []
    iteration_his = []
    dw_his = []
    db_his = []
    for i in range(iterations):
        cost = compute_cost(X, Y, w, b)
        dw, db = calculate_derivatives(X, Y, w, b)
        w = w - learning_rate * dw
        b = b - learning_rate * db
        if i % 100 == 0:
            j_history.append(cost)
            iteration_his.append(i)
            dw_his.append(dw)
            db_his.append(db)

    return j_history, iteration_his, w, b


def get_trained_parameters(X, Y):
    w, b = intialize_parameters(X.shape[1])
    j_his, i_his, trained_w, trained_b = fit(X, Y, w, b)
    return j_his, i_his, trained_w, trained_b




def plot_cost_per_iterations(iteration_history, cost_history):
    plt.plot(iteration_history, cost_history)
    plt.xlabel('iterations')
    plt.ylabel('Cost')
    plt.title(f"Cost function during iterations")
    plt.show()




# ================================================================
def load_test_data():
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv('./BankApp/data/TestData.csv')
    df['Married/Single'] = df['Married/Single'].replace({'single': 0, 'married': 1})
    df['House_Ownership'] = df['House_Ownership'].replace({'norent_noown': 0, 'owned':1, 'rented': 2})
    df['Car_Ownership'] = df['Car_Ownership'].replace({'no': 0, 'yes':1})
    df = df.drop('ID', axis=1)
    # Print the first few rows of the DataFrame
    le = LabelEncoder()
    df['Profession'] = le.fit_transform(df['Profession'])
    df['CITY'] = le.fit_transform(df['CITY'])
    df['STATE'] = le.fit_transform(df['STATE'])

    # df.to_csv('new_filename.csv', index=False)
    DATA_SET = df.values
    return DATA_SET


def load_test_y():
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv('./BankApp/data/SamplePredictionDataset.csv')
    df = df.drop('id', axis=1)
    # df.to_csv('new_filename.csv', index=False)
    DATA_SET = df.values
    return DATA_SET


