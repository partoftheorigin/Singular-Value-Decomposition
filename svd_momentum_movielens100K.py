import sys
sys.path.append('/home/linux/Dropbox/Curioso/phd-work/recommendation-systems/curioso')
import pandas as pd
import numpy as np
import math
import csv
from small_programs.calculate_rmse import rmse
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
import time

df = pd.read_csv('/home/linux/Documents/Curioso/RecommenderSystem/Datasets/MovieLens/MovieLens100KDataset/ml-100k/u.data', sep='\t', names=['user_id', 'item_id', 'rating', 'timestamp'], engine='python')

n_users = df.user_id.nunique()
n_items = df.item_id.nunique()

print('Number of Users: ' + str(n_users) + ' | Number of Items: ' + str(n_items))

training_data, testing_data = train_test_split(df, test_size=0.25, random_state=42)

train_data_matrix = np.zeros((n_users, n_items))
for line in training_data.itertuples():
    train_data_matrix[line[1]-1, line[2]-1] = line[3]

test_data_matrix = np.zeros((n_users, n_items))
for line in testing_data.itertuples():
    test_data_matrix[line[1]-1, line[2]-1] = line[3]

def matrix_factorization(R, P, Q, K, steps=1000, alpha=0.001, gamma=0.9):
    Q = Q.T
    PW = np.zeros((n_users, K))
    QW = np.zeros((K, n_items))
    for step in range(steps):
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] > 0:
                    eij = R[i][j] - np.dot(P[i,:], Q[:,j])
                    for k in range(K):
                        PW[i][k] = (gamma * PW[i][k]) - (2 * alpha * eij * Q[k][j])
                        P[i][k] = P[i][k] - PW[i][k]
                        QW[k][j] = (gamma * QW[k][j]) - (2 * alpha * eij * P[i][k])
                        Q[k][j] = Q[k][j] - QW[k][j]
                        #print('PW[%d][%d]: ' % (i, k) + str(PW[i][k]) + ' | QW[%d][%d]: ' % (k, j) + str(QW[k][j]))
                        #print('P[%d][%d]: ' % (i, k) + str(P[i][k]) + ' | Q[%d][%d]: ' % (k, j) + str(Q[k][j]))
        eR = np.dot(P, Q)
        e = 0
        for i in range(len(R)):
            for j in range(len(R[i])):
                if R[i][j] > 0:
                    e = e + pow(R[i][j] - eR[i][j], 2)
        if e < 0.001:
            break
        l1 = ['momentum', K, step+1, e]
        with open(r'/home/linux/Dropbox/Curioso/phd-work/recommendation-systems/curioso/data/svd_step_error_results_movielens100K_943x1682_momentum.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(l1)
        if (step+1) % 100 == 0:
            X_pred = np.dot(P, Q)

            #print('Step: '+ str(step) + ' | Error: ' + str(ce))

            # RMSE
            rmse_training = rmse(X_pred, train_data_matrix)
            rmse_testing = rmse(X_pred, test_data_matrix)
            #print('SVD Training RMSE: ' + str(rmse_training) + ' | SVD Testing RMSE: ' + str(rmse_testing))

            # MAE
            mae_training = mean_absolute_error(train_data_matrix, X_pred)
            mae_testing = mean_absolute_error(test_data_matrix, X_pred)
            #print('SVD Training MAE: ' + str(mae_training) + ' | SVD Testing MAE: ' + str(mae_testing))

            l = ['momentum', n_users, n_items, K, step+1, e, rmse_training, rmse_testing, mae_training, mae_testing]

            with open(r'/home/linux/Dropbox/Curioso/phd-work/recommendation-systems/curioso/data/svd_results_movielens100K_943x1682_momentum.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(l)

if __name__ == "__main__":
    start_time = time.time()
    R = train_data_matrix
    for K in [10, 20, 30, 40, 50]:
        P = np.loadtxt('/home/linux/Dropbox/Curioso/phd-work/recommendation-systems/curioso/data/P_random_943x%d.txt' % K)
        Q = np.loadtxt('/home/linux/Dropbox/Curioso/phd-work/recommendation-systems/curioso/data/Q_random_1682x%d.txt' % K)

        matrix_factorization(R, P, Q, K)

    end_time = time.time()
    print("Elapsed time was %g seconds" % (end_time - start_time))
