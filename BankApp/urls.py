from django import views
from django.urls import path
from . import views

urlpatterns = [
    path('addresses/', views.adresses),
    path('addresses/<int:zip_code>', views.adresses),

    
    path('countries/', views.countries),
    path('countries/<int:country_code>', views.countries),


    path('users/', views.users),
    path('users/<int:SSN>', views.users),


    path('debit-cards/', views.debit_cards),
    path('debit-cards/<int:card_number>', views.debit_cards),
    path('user-debit-cards/<int:SSN>', views.user_debit_cards),


    path('transactions/', views.transactions),
    path('transactions/<int:Id>', views.transactions),
    path('user-transactions/<int:SSN>', views.user_transactions),


    path('admins/', views.admins),
    path('admins/<int:a_id>', views.admins),


    path('loans/', views.loans),
    path('loans/<int:l_number>', views.loans),
    path('user-loans/<int:SSN>', views.user_loans),
    path('admin-loans/<int:a_id>', views.admin_loans),


    path('services/', views.services),
    path('services/<type>', views.services),


    path('asks/', views.asks),
    path('asks/<int:SSN>', views.asks),


    path('login/', views.login),

    path('features/<int:type>', views.string_features),
    path('predict/', views.predict_loan),
]