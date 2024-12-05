from rest_framework import serializers
from .models import Users, Book, Book_Copies, Magazine, File, Notification


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = 'name', 'id_number', 'email', 'issued_book', 'user_type', 'fine'
