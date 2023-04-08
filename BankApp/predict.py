# import numpy as np
# from threading import Thread 
# from preparation import perpare_and_train, get_training_accuracy, get_test_accuracy
# from utils import calculate_pred, get_label_encoded


# def prepare_and_train_async():
#     global X, Y, iter_his, cost_his, trained_w, trained_b
#     X, Y, cost_his, iter_his, trained_w, trained_b = perpare_and_train()

# # Start the prepare_and_train function in a separate thread
# train_thread = Thread(target=prepare_and_train_async)
# train_thread.start()

# profession_dict, city_dict, state_dict = get_label_encoded()
# # dict = get_dict_encoder(profession_dict, city_dict, state_dict)

# print("Please Specifiy the given form:")
# income = int(input("Your income: "))
# age = int(input("Your age: "))
# experience = int(input("Your experience: "))
# married = int(input("Are you married?[1 => yes, 0 => no]: "))
# is_house_owner = int(input("Are you a house owner?[1 => yes, 0 => no] : "))
# is_car_owner = int(input("Are you a car owner?[1 => yes, 0 => no] : "))

# print("="*80)
# for key, value in profession_dict.items():
#     print(key, " => ", value)
# profession_num = int(input("Your profession num: "))

# print("="*80)
# for key, value in city_dict.items():
#     print(key, " => ", value)
# city_num = int(input("Your city num: "))

# print("="*80)
# for key, value in state_dict.items():
#     print(key, " => ", value)
# state_num = int(input("Your state num: "))

# current_job_year = int(input("Your current_job_year: "))
# current_house_year = int(input("Your current_house_year: "))


# loan = np.array([income, age, experience, married, is_house_owner, is_car_owner, 
#                 profession_num, city_num, state_num, current_job_year, current_house_year])
# loan = loan.reshape(1, -1)

# print("Processing...")
# train_thread.join()

# prediction = calculate_pred(loan, trained_w, trained_b)
# prediction = prediction>0.5
# # print(loan.shape)
# # print(trained_w.shape)
# print(prediction[0, 0])
# print(get_training_accuracy(X, Y, trained_w, trained_b))
# print(get_test_accuracy(trained_w, trained_b))
