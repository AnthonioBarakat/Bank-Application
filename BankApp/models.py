from django.db import models
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator

def upload_path(instance, filename):
    return '/'.join([filename])

# Create your models here.

class Address(models.Model):
    zip_code = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name


class Country(models.Model):
    country_code = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class User(models.Model):
    SSN = models.IntegerField(primary_key=True, db_index=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=100, db_index=True)
    password = models.CharField(max_length=40)
    passport_file = models.FileField(blank=True, null=True, 
                                    upload_to=upload_path
                                    )
    # validators=[
    #                                             FileExtensionValidator(allowed_extensions=['pdf']), 
    #                                             FileValidator(max_size=1024 * 100)]
    DOB = models.DateField()
    DOJ = models.DateField(auto_now_add=True)
    gender = models.CharField(max_length=1)
    balance = models.DecimalField(decimal_places=2, max_digits=14)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    nationality = models.ForeignKey(Country, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class DebitCard(models.Model):
    card_number = models.IntegerField(primary_key=True, db_index=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    date_obtained = models.DateField(auto_now_add=True)
    user_SSN = models.ForeignKey(User, on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.card_number} obtained by {self.user_SSN}"


class Transactions(models.Model):
    Id = models.AutoField(primary_key=True, db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    sender_SSN = models.ForeignKey(User, on_delete=models.PROTECT)
    receiver_SSN = models.IntegerField()
    def __str__(self):
        return f"{self.Id} sended by {self.sender_SSN}"


class Admin(models.Model):
    a_id = models.IntegerField(primary_key=True, db_index=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=40)
    DOJ = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name

class Loan(models.Model):
    l_number = models.AutoField(primary_key=True, db_index=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    duration = models.CharField(max_length=40)
    user_SSN = models.ForeignKey(User, on_delete=models.PROTECT)
    admin_id = models.ForeignKey(Admin, on_delete=models.PROTECT, default=1)
    status = models.SmallIntegerField()
    def __str__(self):
        return f"{self.l_number} requested by {self.user_SSN}"

class Service(models.Model):
    s_number = models.AutoField(primary_key=True, db_index=True)
    s_type = models.CharField(max_length=80, unique=True)
    is_freezed = models.BooleanField()
    def __str__(self):
        return self.s_type

class Ask(models.Model):
    a_number = models.AutoField(primary_key=True, db_index=True)
    user_SSN = models.ForeignKey(User, on_delete=models.PROTECT)
    s_number_fk = models.ForeignKey(Service, on_delete=models.PROTECT)
    def __str__(self):
        return f"Service {self.s_number_fk} asked by {self.user_SSN}"
    

