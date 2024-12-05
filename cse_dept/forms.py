import re
from django import forms
from .models import  Book, Magazine,Users


class Login(forms.Form):
    email = forms.CharField(label="email", max_length=20)
    password = forms.CharField(label='password', max_length=20)


class SearchForm(forms.Form):
    query = forms.CharField()


class UserForm(forms.ModelForm):
    name = forms.CharField(label='Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter name'}))
    email = forms.CharField(label='Email', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter email'}))
    id_number = forms.CharField(label='id_number', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter ID Number'}))
    phone = forms.IntegerField(label='Phone', widget=forms.NumberInput(attrs={'min': '1'}))
    class Meta:
        model = Users
        fields = ['name', 'email', 'id_number', 'phone', 'fine']


class BookForm(forms.ModelForm):
    name = forms.CharField(label='Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter book name'}))
    isbn = forms.CharField(label='ISBN', max_length=13, widget=forms.NumberInput(attrs={'placeholder': 'Enter ISBN'}))
    category = forms.CharField(label='category', max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Enter category'}))
    author = forms.CharField(label='Author', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter author name'}))
    issue_date = forms.DateField(label='issue_date', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    ret_date = forms.DateField(label='ret_date', widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    edition = forms.IntegerField(label='Edition', widget=forms.NumberInput(attrs={'min': '1'}) )
    class Meta:
        model = Book
        fields = ['name','isbn', 'edition', 'category', 'author', 'issue_date', 'ret_date', ]


class MagForm(forms.ModelForm):
    name = forms.CharField(label='Magazine Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter magazine name'}))
    isbn = forms.CharField(label='ISBN', max_length=13, widget=forms.TextInput(attrs={'placeholder': 'Enter ISBN'}))
    author = forms.CharField(label='Author', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter author name'}))
    category = forms.CharField(label='category', max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Enter category'}))
    edition = forms.IntegerField(label='Edition', widget=forms.NumberInput(attrs={'min': '1'}) )
    class Meta:
        model = Magazine
        fields = ['name', 'edition', 'isbn', 'author', 'category' ]
"""
class StaffForm(forms.ModelForm):
    name = forms.CharField(label='Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter name'}))
    staff_id = forms.CharField(label='staff_id', max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Enter staff ID'}))
    email = forms.CharField(label='Email', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter email'}))
    phone = forms.IntegerField(label='Phone', widget=forms.NumberInput())
    fine = forms.IntegerField(label='Fine', widget=forms.NumberInput(), required=False)
    #issued_book = forms.IntegerField(label='Issued Books', widget=forms.NumberInput(), required=False)
    # issued_magazine = forms.IntegerField(label='Issued Magazines', widget=forms.NumberInput(attrs={'min': '0'}))
    
    class Meta:
        model = Staff
        fields = ['name', 'staff_id', 'email', 'phone', 'fine']


class StudentForm(forms.ModelForm):
    name = forms.CharField(label='Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter name'}))
    usn = forms.CharField(label='USN', max_length=7, widget=forms.TextInput(attrs={'placeholder': 'Enter USN'}))
    email = forms.CharField(label='Email', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter email'}))
    phone = forms.IntegerField(label='Phone', widget=forms.NumberInput(attrs={'min': '1'}))
    fine = forms.IntegerField(label='Fine', widget=forms.NumberInput(attrs={'min': '0'}))
    #issued_book = forms.IntegerField(label='Issued Books', widget=forms.NumberInput(attrs={'min': '0'}))
    # issued_magazine = forms.IntegerField(label='Issued Magazines', widget=forms.NumberInput(attrs={'min': '0'}))
    
    class Meta:
        model = Student
        fields = ['name', 'usn', 'email', 'phone', 'fine']


class ReferenceForm(forms.ModelForm):
    name = forms.CharField(label='Reference Name', max_length=100, widget=forms.TextInput(attrs={'class': 'table-form', 'placeholder': 'Enter reference name'}))
    category = forms.CharField(label='category', max_length=200, widget=forms.TextInput(attrs={'class': 'table-form', 'placeholder': 'Enter category'}))
    isbn = forms.CharField(label='ISBN', max_length=13, widget=forms.TextInput(attrs={'placeholder': 'Enter ISBN'}))
    author = forms.CharField(label='Author', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter author name'}))
    copies = forms.IntegerField(label='Copies', widget=forms.NumberInput(attrs={'min': '1'}))
    # available = forms.BooleanField(label='Available', required=False)
    
    class Meta:
        model = Reference
        fields = ['name', 'category', 'isbn', 'author', 'copies',]


class addStudent(forms.ModelForm):
    name = forms.CharField(label='name', max_length=200, widget=forms.TextInput(attrs={
        'rows': '1'
    }))
    usn = forms.CharField(label='usn',widget=forms.TextInput(attrs={
        'rows': 1
    }))

    email = forms.CharField(label='email',widget=forms.TextInput(attrs={
        'rows': '1'
    }))
    password = forms.CharField(label='password',widget=forms.TextInput(attrs={
        'rows': 1
    }))
    phone = forms.CharField(label='phone',widget=forms.TextInput(attrs={
        'rows': 1
    }))

    class Meta:
        model = Student
        fields = [
            'name',
            'usn',
            'email',
            'password',
            'phone'
        ]


class addBook(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
    }))
    isbn = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    author = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
    }))
    copies = forms.CharField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
    }))
    category = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    edition = forms.CharField(widget=forms.NumberInput(attrs={
        'class': 'form-control',
    }))

    class Meta:
        model = Book
        fields = [
            'name',
            'isbn',
            'author',
            'category',
            'copies',
            'edition',
            
        ]
"""

class addMagazine(forms.ModelForm):
    name = forms.CharField(widget=forms.Textarea(attrs={
        'class': "name-field",
        'rows': '1'
    }))
    isbn = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'isbn-field',
        'rows': 1
    }))
    author = forms.CharField(widget=forms.Textarea(attrs={
        'class': "author-field",
        'rows': '1'
    }))
    copies = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'copies-field',
        'rows': 1
    }))
    
    category = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'category-field',
        'rows': 1
    }))

    class Meta:
        model = Magazine
        fields = [
            'name',
            'isbn',
            'author',
            'copies',
            'category',
        ]

"""
class addStaff(forms.ModelForm):
    name = forms.CharField(label='name', widget=forms.Textarea(attrs={
    'rows': 1}))
    staff_id = forms.CharField(label='staff_id', widget=forms.Textarea(attrs={
    'rows': 1
    }))
    email = forms.CharField(label='email', widget=forms.Textarea(attrs={
      'rows': 1  
    }))
    password = forms.CharField(label='password', widget=forms.Textarea(attrs={
    'rows': 1}))
    phone = forms.CharField(label='phone', widget=forms.Textarea(attrs={
        'rows': 1
    }))

    class Meta:
        model = Staff
        fields = [
            'name',
            'staff_id',
            'email',
            'phone',
            'password',
        ]


class addReference(forms.ModelForm):
    name = forms.CharField(widget=forms.Textarea(attrs={
        'class': "name-field",
        'rows': '1'
    }))
    isbn = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'isbn-field',
        'rows': 1
    }))
    author = forms.CharField(widget=forms.Textarea(attrs={
        'class': "author-field",
        'rows': '1'
    }))
    copies = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'copies-field',
        'rows': 1
    }))
    
    category = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'category-field',
        'rows': 1
    }))
    edition = forms.IntegerField(widget=forms.Textarea(attrs={
        'class': 'edition-field',
        'rows': 1
    }))

    class Meta:
        model = Reference
        fields = [
            'name',
            'isbn',
            'author',
            'copies',
            'category',
            'edition',
        ]
"""