from http.client import HTTPResponse
from threading import Thread 
import re
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view

from .models import DebitCard, Transactions, User, Address, Country, Admin, Loan, Service, Ask
from .serializers import UserSerializer, AddressSerializer, CountrySerializer, DebitCardSerializer, \
    TransactionSerializer, AdminSerializer, LoanSerializer, ServiceSerializer, AskSerializer

from rest_framework.response import Response
from rest_framework import status
from .utils import get_label_encoded, calculate_pred, plot_cost_per_iterations
from .preparation import perpare_and_train, get_training_accuracy, get_test_accuracy
import numpy as np

# Create your views here.

#############################################################################
@api_view(['GET', 'POST', 'DELETE'])
def adresses(request, zip_code=-1):
    # GET Method
    if request.method == 'GET':
        if zip_code == -1:
            addresses = Address.objects.all()
            serialized_addresses = AddressSerializer(addresses, many=True)
            return Response(serialized_addresses.data, status.HTTP_200_OK)
        else:
            address = get_object_or_404(Address, pk=zip_code)
            serialized_address = AddressSerializer(address)
            return Response(serialized_address.data)

    # POST Method
    elif request.method == 'POST':
        serialized_address = AddressSerializer(data=request.data)
        serialized_address.is_valid(raise_exception=True)
        serialized_address.save()
        return Response({"success":"Address added successfuly"}, status.HTTP_201_CREATED)

    # DELETE Method
    elif request.method == 'DELETE':
        if zip_code == -1:
            return Response({"Fail":"Please enter a valid zip code address to be deleted"}, status.HTTP_400_BAD_REQUEST)
        else:
            try:
                address = Address.objects.get(pk=zip_code)
                address.delete();
                return Response({"success":"Address deleted successfuly"}, status.HTTP_200_OK)
            except:
                return Response({"Fail":"Zip code does not exist"}, status.HTTP_404_NOT_FOUND)




#############################################################################
@api_view(['GET', 'POST', 'DELETE'])
def countries(request, country_code=-1):
    # GET Method
    if request.method == 'GET':
        if country_code == -1:
            countries = Country.objects.all()
            serialized_countries = CountrySerializer(countries, many=True)
            return Response(serialized_countries.data, status.HTTP_200_OK)
        else:
            country = get_object_or_404(Country, pk=country_code)
            serialized_country = CountrySerializer(country)
            return Response(serialized_country.data)
        
    # POST Method
    elif request.method == 'POST':
        serialized_country = CountrySerializer(data=request.data)
        serialized_country.is_valid(raise_exception=True)
        serialized_country.save()
        return Response({"success":"Country added successfuly"}, status.HTTP_201_CREATED)
    
    # DELETE Method
    elif request.method == 'DELETE':
        if country_code == -1:
            return Response({"Fail":"Please enter a valid country code to be deleted"}, status.HTTP_400_BAD_REQUEST)
        else:
            try:
                country = Country.objects.get(pk=country_code)
                country.delete();
                return Response({"success":"Country deleted successfuly"}, status.HTTP_200_OK)
            except:
                return Response({"Fail":"Country code does not exist"}, status.HTTP_404_NOT_FOUND)
    

#############################################################################
@api_view(['GET', 'POST', 'PATCH'])
def users(request, SSN=-1):
    if request.method == 'GET':
        if SSN == -1:
            users = User.objects.select_related('address', 'nationality').all()
            serialized_users = UserSerializer(users, many=True)
            return Response(serialized_users.data, status.HTTP_200_OK)
        else:
            user = get_object_or_404(User, pk=SSN)
            serialized_user = UserSerializer(user)
            return Response(serialized_user.data)
    
    # POST Method
    elif request.method == 'POST':
        serialized_user = UserSerializer(data=request.data)
        serialized_user.is_valid(raise_exception=True)
        serialized_user.save()
        return Response({"success":"User added successfuly"}, status.HTTP_201_CREATED)
    
    # PATCH Method
    elif request.method == 'PATCH':
        if SSN == -1:
            return Response({"Fail":"Specifiy the user SSN in the url"}, status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.get(pk=SSN)
            try:
                user.first_name = request.data['first_name']
            except:
                pass
            try:
                user.last_name = request.data['last_name']
            except:
                pass
            try:
                if re.match(r'^.+@.+\.[A-z]+[\.A-z]?+$', request.data['email']):
                    user.email = request.data['email']
                else:
                    return Response({"Fail":"Enter a valid email"}, status.HTTP_400_BAD_REQUEST)
            except:
                pass
            try:
                value = request.data['password']
                is_d = value.isdigit()
                if re.match(r"^.*[A-Z0-9]+.*$", value) and not is_d:
                    user.password = value
                else:
                    return Response({"Fail":'Password must contain digit and letter uppercase and lowercase'}, status.HTTP_400_BAD_REQUEST)
            except:
                pass
            try:
                bal = request.data['balance']
                if float(bal) > 999999999999.99:
                    return Response({"Fail":'Balance must consist no more of 14 digits 2 for decimal place'}, status.HTTP_400_BAD_REQUEST)
                else:
                    user.balance = bal
            except:
                pass
            try:
                request.data['address_zip_code']
                try:
                    user.address = get_object_or_404(Address, pk=request.data['address_zip_code'])
                except:
                    return Response({"Fail":"Address Does not exist"}, status.HTTP_404_NOT_FOUND)
            except:
                pass

            user.save()
            return Response({"success":"User updated successfuly"}, status.HTTP_200_OK)


    

#############################################################################
@api_view(['GET', 'POST'])
def debit_cards(request, card_number=-1):
    if request.method == 'GET':
        if card_number == -1:
            debit_cards = DebitCard.objects.all()
            serialized_debit_cards = DebitCardSerializer(debit_cards, many=True)
            return Response(serialized_debit_cards.data, status.HTTP_200_OK)
        else:
            debit_card = get_object_or_404(DebitCard, pk=card_number)
            serialized_debit_card = DebitCardSerializer(debit_card)
            return Response(serialized_debit_card.data)
    elif request.method == 'POST':
        serialized_debit_card = DebitCardSerializer(data=request.data)
        serialized_debit_card.is_valid(raise_exception=True)
        serialized_debit_card.save()
        return Response({"success":"debit card obtained successfuly"}, status.HTTP_201_CREATED)


@api_view(['GET'])
def user_debit_cards(request, SSN):
    if request.method == 'GET':
        user_debit_cards = DebitCard.objects.filter(user_SSN=SSN)
        serialized_user_debit_cards = DebitCardSerializer(user_debit_cards, many=True)
        return Response(serialized_user_debit_cards.data, status.HTTP_200_OK)
    


#############################################################################
@api_view(['GET', 'POST'])
def transactions(request, Id=-1):
    if request.method == 'GET':
        if Id == -1:
            transactions = Transactions.objects.select_related('sender_SSN').all()
            serialized_transactions = TransactionSerializer(transactions, many=True)
            return Response(serialized_transactions.data, status.HTTP_200_OK)
        else:
            transaction = get_object_or_404(Transactions, pk=Id)
            serialized_transaction = TransactionSerializer(transaction)
            return Response(serialized_transaction.data)
    # POST
    elif request.method == 'POST':
        serialized_transaction = TransactionSerializer(data=request.data)
        serialized_transaction.is_valid(raise_exception=True)
        serialized_transaction.save()
        return Response({"success":"Transaction done successfuly"}, status.HTTP_201_CREATED)


@api_view(['GET'])       
def user_transactions(request, SSN):
    if request.method == 'GET':
        user_transactions = Transactions.objects.filter(sender_SSN=SSN)
        serialized_user_transactions = TransactionSerializer(user_transactions, many=True)
        return Response(serialized_user_transactions.data, status.HTTP_200_OK)
    



#############################################################################
@api_view(['GET', 'POST', 'PATCH'])
def admins(request, a_id=-1):
    if request.method == 'GET':
        if a_id == -1:
            admins = Admin.objects.all()
            serialized_admins = AdminSerializer(admins, many=True)
            return Response(serialized_admins.data, status.HTTP_200_OK)
        else:
            admin = get_object_or_404(Admin, pk=a_id)
            serialized_admin = AdminSerializer(admin)
            return Response(serialized_admin.data)
        
    # POST
    elif request.method == 'POST':
        serialized_admin = AdminSerializer(data=request.data)
        serialized_admin.is_valid(raise_exception=True)
        serialized_admin.save()
        return Response({"success":"Admin created successfuly"}, status.HTTP_201_CREATED)

    # PATCH
    elif request.method == 'PATCH':
        if a_id == -1:
            return Response({"Fail":"Specifiy the admin id in the url"}, status.HTTP_400_BAD_REQUEST)
        else:
            admin = Admin.objects.get(pk=a_id)
            try:
                admin.password = request.data['password']
                admin.save()
                return Response({"success":"Admin updated successfuly"}, status.HTTP_200_OK)
            except:
                return Response({"Fail":"Specifiy a password"}, status.HTTP_400_BAD_REQUEST)
        


#############################################################################
@api_view(['GET', 'POST', 'PATCH'])
def loans(request, l_number=-1):
    if request.method == 'GET':
        if l_number == -1:
            loans = Loan.objects.all()
            serialized_loans = LoanSerializer(loans, many=True)
            return Response(serialized_loans.data, status.HTTP_200_OK)
        else:
            loan = get_object_or_404(Loan, pk=l_number)
            serialized_loan = LoanSerializer(loan)
            return Response(serialized_loan.data)
    
    # POST Method
    elif request.method == 'POST':
        serialized_loan = LoanSerializer(data=request.data)
        serialized_loan.is_valid(raise_exception=True)
        serialized_loan.save()
        return Response({"success":"Loan requested successfuly"}, status.HTTP_201_CREATED)
    
    # PATCH Method
    elif request.method == 'PATCH':
        if l_number == -1:
            return Response({"Fail":"Specifiy the loan number in the url"}, status.HTTP_400_BAD_REQUEST)
        else:
            loan = Loan.objects.get(pk=l_number)
            try:
                request.data['status']
                request.data['a_id']
                def is_status_valid(value):
                    value = int(value)
                    if value == 0 or value == 1 or value == 2 :
                        return value
                    else:
                        raise ValueError("Error")
                
                try:
                    admin = get_object_or_404(Admin, pk=request.data['a_id'])
                except:
                    return Response({"Fail":"Admin not found"}, status.HTTP_400_BAD_REQUEST)
                try:
                    st = is_status_valid(request.data['status'])
                except:
                    return Response({"Fail":"Status Incorrect must be 0 => Refused, 1 => Approved or 2 => Processing"}, status.HTTP_400_BAD_REQUEST)
                
                loan.admin_id = admin
                loan.status = st
            except:
                return Response({"Fail":"To update a loan you must specify the two fields admin id(a_id), and new status"}, 
                                status.HTTP_400_BAD_REQUEST)

            loan.save()
            return Response({"success":"Loan updated successfuly"}, status.HTTP_200_OK)
    


@api_view(['GET'])       
def user_loans(request, SSN):
    if request.method == 'GET':
        user_loans = Loan.objects.filter(user_SSN=SSN)
        serialized_user_loans = LoanSerializer(user_loans, many=True)
        return Response(serialized_user_loans.data, status.HTTP_200_OK)
    
@api_view(['GET'])       
def admin_loans(request, a_id):
    if request.method == 'GET':
        admin_loans = Loan.objects.filter(admin_id=a_id)
        serialized_admin_loans = LoanSerializer(admin_loans, many=True)
        return Response(serialized_admin_loans.data, status.HTTP_200_OK)
    

#############################################################################
@api_view(['GET', 'POST', 'PATCH'])
def services(request, type=""):
    if request.method == 'GET':
        if type == "":
            services = Service.objects.all()
            serialized_services = ServiceSerializer(services, many=True)
            return Response(serialized_services.data, status.HTTP_200_OK)
        else:
            service = Service.objects.get(s_type=type)
            serialized_service = ServiceSerializer(service)
            return Response(serialized_service.data, status.HTTP_200_OK)
        
    # POST Method
    elif request.method == 'POST':
        serialized_service = ServiceSerializer(data=request.data)
        serialized_service.is_valid(raise_exception=True)
        serialized_service.save()
        return Response({"success":"Service Created successfuly"}, status.HTTP_201_CREATED)
    
    # PATCH Method
    elif request.method == 'PATCH':
        try:
            service_number = request.data['s_number']
            service = Service.objects.get(pk=service_number)
            if int(request.data['is_freezed']) == 0 or int(request.data['is_freezed']) == 1:
                service.is_freezed = request.data['is_freezed']
                service.save()
                return Response({"success":"Service updated successfuly"}, status.HTTP_200_OK)
            else:
                return Response({"Fail":"Freezed value is Incorrect must be 0 => not freezed, 1 => freezed"}, status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"Fail":"The s_number (service number) must be sent in the body request"}, status.HTTP_400_BAD_REQUEST)
    


#############################################################################
@api_view(['GET', 'POST'])
def asks(request, SSN=-1):
    if request.method == 'GET':
        if SSN == -1:
            asks = Ask.objects.all()
            serialized_asks = AskSerializer(asks, many=True)
            return Response(serialized_asks.data, status.HTTP_200_OK)
        else:
            user_asks = Ask.objects.filter(user_SSN=SSN)
            serialized_user_asks = AskSerializer(user_asks, many=True)
            return Response(serialized_user_asks.data, status.HTTP_200_OK)
        
    # Method POST
    elif request.method == 'POST':
        serialized_ask = AskSerializer(data=request.data)
        serialized_ask.is_valid(raise_exception=True)
        serialized_ask.save()
        return Response({"success":"Ask requested successfuly"}, status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        try:
            email = request.data['email']
            password = request.data['password']
            try:
                user = User.objects.get(email=email)
                if user.password == password:
                    return Response({"success":"User email and password are correct", "SSN":user.SSN, "role": "user"}, status.HTTP_200_OK)
                else:
                    return Response({"Fail":"Password is incorrect"}, status.HTTP_400_BAD_REQUEST)
            except:
                try:
                    admin = Admin.objects.get(email=email)
                    if admin.password == password:
                        return Response({"success":"Admin email and password are correct", "a_id":admin.a_id, "role": "admin"}, status.HTTP_200_OK)
                    else:
                        return Response({"Fail":"Password is incorrect"}, status.HTTP_400_BAD_REQUEST)
                except:
                    return Response({"Fail":"Email Does not found"}, status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"Fail":"Email or password are not set"}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def string_features(request, type):
    profession_dict, city_dict, state_dict = get_label_encoded()
    # Transform the key from numpy.int32 type => built-in int type
    
    profession_dict = {int(key): value for key, value in profession_dict.items()}
    city_dict = {int(key): value for key, value in city_dict.items()}
    state_dict = {int(key): value for key, value in state_dict.items()}


    if type == 1:
        return Response(profession_dict, status.HTTP_200_OK)
    # ({"Profession":f"{dumps(profession_dict)}"}, status.HTTP_200_OK)
    elif type == 2:
        return Response(city_dict, status.HTTP_200_OK)
    elif type == 3:
        return Response(state_dict, status.HTTP_200_OK)

@api_view(['POST'])
def predict_loan(request):
    X, Y, cost_his, iter_his, trained_w, trained_b = (None for i in range(6))
    def prepare_and_train_async():
        nonlocal X, Y, iter_his, cost_his, trained_w, trained_b
        X, Y, cost_his, iter_his, trained_w, trained_b = perpare_and_train()
    
    train_thread = Thread(target=prepare_and_train_async)
    train_thread.start()

    income = int(request.data["income"])
    age = int(request.data["age"])
    experience = int(request.data["experience"])

    is_married = int(request.data["is_married"])
    is_house_owner = int(request.data["is_house_owner"])
    is_car_owner = int(request.data["is_car_owner"])

    profession_num = int(request.data["profession_num"])
    city_num = int(request.data["city_num"])
    state_num = int(request.data["state_num"])

    current_job_year = int(request.data["current_job_year"])
    current_house_year = int(request.data["current_house_year"])

    
    loan_info = np.array([income, age, experience, is_married, is_house_owner, is_car_owner, 
                profession_num, city_num, state_num, current_job_year, current_house_year])
    loan_info = loan_info.reshape(1, -1)

    train_thread.join()

    prediction = calculate_pred(loan_info, trained_w, trained_b)
    prediction = prediction>0.5
    prediction_decision = prediction[0, 0]
    train_acc, precision, recall, f1 = get_training_accuracy(X, Y, trained_w, trained_b)
    test_acc = get_test_accuracy(trained_w, trained_b)
    # plot_cost_per_iterations(iter_his, cost_his)

    return Response({"Decision": prediction_decision, "train accuracy": f"{round(train_acc)}%", 
                                "test acc": f"{round(test_acc)}%"})