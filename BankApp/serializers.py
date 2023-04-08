from decimal import Decimal
from pickletools import read_long1
import re
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from .models import Address, Country, User, DebitCard, Transactions, Admin, Loan, Service, Ask

from rest_framework.response import Response

#############################################################################################
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['zip_code', 'name']

#############################################################################################

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['country_code', 'name']
#############################################################################################


#############################################################################################
class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(method_name="display_name")

    first_name = serializers.CharField(max_length=200, write_only=True)
    last_name = serializers.CharField(max_length=200, write_only=True)
    password = serializers.CharField(max_length=40, write_only=True)
    DOB = serializers.DateField(write_only=True)
    gender = serializers.CharField(max_length=1, write_only=True)

    address = AddressSerializer(read_only=True)
    nationality = CountrySerializer(read_only=True)

    address_zip_code = serializers.IntegerField(write_only=True)
    nationality_country_code = serializers.IntegerField(write_only=True)

    class Meta:
        model = User
        fields = ['SSN', 'name', 'email', 'balance', 'passport_file', 'address', 'nationality', 
                    'first_name', 'last_name', 'password', 'DOB', 'gender',
                    'address_zip_code', 'nationality_country_code']
        
        # depth = 1
    def display_name(self, user:User):
        return f"{user.first_name} {user.last_name}"
    
    def validate_passport_file(self, value):
        # size returned will be in bytes
        file_size = value.size
        limit_mb = 5
        if file_size > limit_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Max size of file is 5MB, Your size is {round(file_size/1024/1024, 2)} MB")
        #limit_kb = 150
        #if file_size > limit_kb * 1024:
        #    raise ValidationError("Max size of file is %s MB" % limit_mb)

        # Get the file extension
        file_type = value.name.split(".")[-1]
        if file_type.upper() != 'PDF':
            raise serializers.ValidationError(f"Extension allowed .pdf, Your extension is .{file_type}")
        return value


    def validate_SSN(self, value):
        if len(str(value)) != 9:
            raise serializers.ValidationError('SSN should be 9 digits')
        else:
            return value
    
    def validate_password(self, value):
        is_d = value.isdigit()
        if re.match(r"^.*[A-Z0-9]+.*$", value) and not is_d:
            return value
        else:
            raise serializers.ValidationError('Password must contain digit and letter uppercase and lowercase')

    def validate_address_zip_code(self, value):
        try:
            Address.objects.get(pk=value)
            return value
        except:
            raise serializers.ValidationError('zip code address not exist')
    
    def validate_nationality_country_code(self, value):
        try:
            Country.objects.get(pk=value)
            return value
        except:
            raise serializers.ValidationError('country code not exist')
        
    def validate_gender(self, value):
        if value.upper() == 'M' or value.upper() == 'F':
            return value
        else:
            raise serializers.ValidationError('Gender must be: m or M => male, f or F => Female ')

    def save(self):
        ad = Address.objects.get(pk=self.validated_data['address_zip_code'])
        na = Country.objects.get(pk=self.validated_data['nationality_country_code'])
        
        user = User.objects.create(
                SSN=self.validated_data['SSN'], 
                first_name=self.validated_data["first_name"], 
                last_name=self.validated_data['last_name'],
                email=self.validated_data['email'], 
                password=self.validated_data['password'], 
                passport_file=self.validated_data['passport_file'],
                DOB=self.validated_data['DOB'], 
                gender=self.validated_data['gender'], 
                balance=self.validated_data['balance'], 
                address=ad, 
                nationality=na)
        user = user.save();
        return user
#############################################################################################
        
        

#############################################################################################
    
class DebitCardSerializer(serializers.ModelSerializer):
    user_SSN = UserSerializer(read_only=True)
    u_SSN = serializers.IntegerField(write_only=True)
    amount_with_interest = serializers.SerializerMethodField(method_name="calculate_bank_interest")
    date_paid_before = serializers.SerializerMethodField(method_name="calculate_date_to_paid")
    class Meta:
        model = DebitCard
        fields = ['card_number', 'amount', 'date_obtained', 'user_SSN', 
                    'amount_with_interest', 'date_paid_before',
                    'u_SSN']
        
    def calculate_bank_interest(self, card:DebitCard):
        if (card.amount <= 100):
            return round(card.amount * Decimal(1.03), 0)
        elif (card.amount <= 300):
            return round(card.amount * Decimal(1.05), 0)
        elif (card.amount <= 500):
            return round(card.amount * Decimal(1.08), 0)
        elif (card.amount <= 700):
            return round(card.amount * Decimal(1.1), 0)
        elif (card.amount <= 900):
            return round(card.amount * Decimal(1.15), 0)
        elif (card.amount <= 1000):
            return round(card.amount * Decimal(1.2), 0)
        elif (card.amount <= 2000):
            return round(card.amount * Decimal(1.3), 0)
        
    def calculate_date_to_paid(self, card:DebitCard):
        o_date = card.date_obtained
        pay_date = o_date.replace(o_date.year, o_date.month + 1)
        return pay_date

    def validate_card_number(self, value):
        if len(str(value)) != 50:
            raise serializers.ValidationError('card number must be 5 digits')
        else:
            return value
        
    def validate_u_SSN(self, value):
        try:
            User.objects.get(pk=value)
            return value
        except:
            raise serializers.ValidationError('user SSN does not exist')
        
    def save(self):
        u = User.objects.get(pk=self.validated_data['u_SSN'])
        dc = DebitCard.objects.create(
                card_number=self.validated_data['card_number'], 
                amount=self.validated_data["amount"], 
                user_SSN=u)
        dc = dc.save()
        return dc
    
#############################################################################################


class TransactionSerializer(serializers.ModelSerializer):
    sender_SSN = UserSerializer(read_only=True)
    s_SSN = serializers.IntegerField(write_only=True)
    r_SSN = serializers.IntegerField(write_only=True)
    reciever_details = serializers.SerializerMethodField(method_name="check_reciever")
    class Meta:
        model = Transactions
        fields = ['Id', 'amount', 'date', 'sender_SSN', 'reciever_details', 
                    's_SSN', 'r_SSN']
    def check_reciever(self, receiver:User):
        try:
            rec = User.objects.get(pk=receiver.receiver_SSN)
            serialized_rec = UserSerializer(rec)
            return serialized_rec.data
        except:
            return receiver.receiver_SSN
        
    def validate_amount(self, value):
        if value>0:
            return value
        else:
            raise serializers.ValidationError('You cannot transfer zero or negative amount')
    
    def validate_r_SSN(self, value):
        if len(str(value)) != 9:
            raise serializers.ValidationError('Enter a valid SSN of 9 digits for the receiver')
        else:
            return value
    
    def validate_s_SSN(self, value):
        if len(str(value)) != 9:
            raise serializers.ValidationError('Enter a valid SSN of 9 digits for the sender')
        else:
            return value
    
    def save(self):
        u = User.objects.get(pk=self.validated_data['s_SSN'])
        t = Transactions.objects.create(
                amount=self.validated_data["amount"], 
                sender_SSN=u,
                receiver_SSN=self.validated_data['r_SSN'])
        t = t.save()
        return t


#######################################################################################


class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=40, write_only=True)
    class Meta:
        model = Admin
        fields = ['a_id', 'name', 'email', 'password']

#######################################################################################

class LoanSerializer(serializers.ModelSerializer):
    user_SSN = UserSerializer(read_only=True)
    admin_id = AdminSerializer(read_only=True)

    date_paid_before = serializers.SerializerMethodField(method_name="calculate_date_to_paid")
    u_SSN = serializers.IntegerField(write_only=True)
    a_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Loan
        fields = ['l_number', 'date', 'amount', 'duration', 'user_SSN', 'admin_id', 'status',
                        'u_SSN', 'a_id', 'date_paid_before']
    
    def validate_u_SSN(self, value):
        try:
            User.objects.get(pk=value)
            return value
        except:
            raise serializers.ValidationError('user SSN does not exist')
        
    def validate_a_id(self, value):
        try:
            Admin.objects.get(pk=value)
            return value
        except:
            raise serializers.ValidationError('Admin Id does not exist')
        
    def validate_status(self, value):
        if value == 0 or value == 1 or value == 2:
                return value 
        else:
            raise serializers.ValidationError('Status Incorrect must be 0 => Refused, 1 => Approved or 2 => Processing')
        

    def validate_duration(self, value):
        match1 = re.fullmatch(r"^[1-9][0-9]?\s(month|year)(\s|\s,\s)([1-9][0-9]?\s(month|year))?$", value)
        match2 = re.fullmatch(r"^[1-9][0-9]?\s(month|year)$", value) 
        if match1 or match2:    
            if value.count('month') > 1 or value.count('year') > 1:
                raise serializers.ValidationError("Error there you repeat a keyword 2 time")
            else:
                return value
        else:
            raise serializers.ValidationError("""Error duration.
The duration must be in the form => 2 digit number -> month or year keyword -> white space or a commun encountered by before and after white space -> maybe can be contain a second one\
Example 1 => 2 month , 1 year
Example 2 => 5 year , 36 month
Example 3 => 24 month 10 year
Remember no 's' in year or month keywords""")
        

    def calculate_date_to_paid(self, loan:Loan):
        o_date = loan.date
        duration = loan.duration.lower()
        duration = duration.split()
        # Must be written in this form 6 month , 2 year
        if "year" in duration:
            o_date = o_date.replace(o_date.year + int(duration[duration.index("year")-1]), o_date.month)
            
        if "month" in duration:
            # int(duration[duration.index("month")-1])
            if o_date.month + int(duration[duration.index("month")-1]) < 12:
                o_date = o_date.replace(o_date.year, o_date.month + int(duration[duration.index("month")-1]))
            else:
                months_remain = (o_date.month + int(duration[duration.index("month")-1])) % 12
                years = (o_date.month + int(duration[duration.index("month")-1])) // 12
                o_date = o_date.replace(o_date.year + years, months_remain)

        return o_date


    def save(self):
        u_SSN = User.objects.get(pk=self.validated_data['u_SSN'])
        a_id = Admin.objects.get(pk=self.validated_data['a_id'])
        
        loan = Loan.objects.create(
                date=self.validated_data['date'], 
                amount=self.validated_data["amount"], 
                duration=self.validated_data['duration'],
                user_SSN=u_SSN, 
                admin_id=a_id, 
                status=self.validated_data['status'])
        loan = loan.save();
        return loan

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['s_number', 's_type', 'is_freezed',]
    
    def validate_is_freezed(self, value):
        if value == 0 or value == 1:
                return value 
        else:
            raise serializers.ValidationError('Freezed value is Incorrect must be 0 => not freezed, 1 => freezed')
        

class AskSerializer(serializers.ModelSerializer):
    user_SSN = UserSerializer(read_only=True)
    s_number_fk = ServiceSerializer(read_only=True)
    u_SSN = serializers.IntegerField(write_only=True)
    s_n = serializers.IntegerField(write_only=True)
    class Meta:
        model = Ask
        fields = ['a_number', 'user_SSN', 's_number_fk', 'u_SSN', 's_n']
    
    def validate_u_SSN(self, value):
        try:
            User.objects.get(pk=value)
            return value
        except:
            raise serializers.ValidationError('user SSN does not exist')
        
    def validate_s_n(self, value):
        try:
            Service.objects.get(pk=value)
            return value
        except:
            raise serializers.ValidationError('Service does not exist')


    def save(self):
        u_SSN = User.objects.get(pk=self.validated_data['u_SSN'])
        s_n = Service.objects.get(pk=self.validated_data['s_n'])
        
        ask = Ask.objects.create(user_SSN=u_SSN, s_number_fk=s_n)
        ask = ask.save();
        return ask
