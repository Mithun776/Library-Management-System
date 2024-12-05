from django.contrib import admin
from .models import Users, Book, TransactionLog, Magazine, File, Notification, Message, Book_Copies
# from .forms import BookAdminForm


"""
class StudAdmin(admin.ModelAdmin):

    def issued_Books(self, obj):
        return ", ".join([str(book) for book in obj.issued_Book.all()])

    # def issued_References(self, obj):
     #   return ", ".join([str(magazine) for magazine in obj.issued_Reference.all()])
    search_fields = ('usn', 'email', 'name', 'issued__name')
    list_display = ('name', 'usn', 'email', 'issued_Books', 'fine')
    raw_id_fields = ('issued_Book', )
    change_form_template = 'admin/website/Student/change_form.html'
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'issued_Book':
            kwargs['queryset'] = Book.objects.filter(available=True)
            # kwargs['to_field_name'] = 'name'
        #if db_field.name == 'issued_Reference':
         #   kwargs['queryset'] = Book.objects.filter(available=True)
            # kwargs['to_field_name'] = 'name'
        return super().formfield_for_manytomany(db_field, request, **kwargs)



class BookAdmin(admin.ModelAdmin):
    search_fields = ('name', 'isbn',)
    list_display = ('name',
                    'access_code'
                    'isbn',
                    'copies',
                    'author',
                    'available',

                    # 'issue_to',
                    # 'issue_date',
                    # 'ret_date'
                    )
    
    raw_id_fields = ('issue_to',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'issue_to':
            kwargs['queryset'] = .objects.filter(issue=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # form = BookAdminForm


class StaffAdmin(admin.ModelAdmin):
    def issued_books(self, obj):
        return ", ".join([str(book) for book in obj.issued_book.all()])

    #def issued_references(self, obj):
    #    return ", ".join([str(magazine) for magazine in obj.issued_reference.all()])

    search_fields = ('name', 'email', 'phone', 'staff_id')
    list_display = ('name', 'email', 'phone', 'staff_id', 'issued_books', 'fine')
    raw_id_fields = ('issued_book',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'issued_book':
            kwargs['queryset'] = Book.objects.filter(available=True)
            # kwargs['to_field_name'] = 'name'
        #if db_field.name == 'issued_reference':
         #   kwargs['queryset'] = Book.objects.filter(available=True)
            # kwargs['to_field_name'] = 'name'
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class bookcopyadmin(admin.ModelAdmin):
    list_display = ('book', 'total_copies', 'available_copies', 'issued_copies', )

class Messageadmin(admin.ModelAdmin):
"""

class StudAdmin(admin.ModelAdmin):
    def issued_book(self, obj):
        return ", ".join([str(book) for book in obj.issued_book.all()])
    list_display = ['name', 'id_number', 'email', 'issued_book', 'fine', 'phone',]

class BookAdmin(admin.ModelAdmin):
    list_display = [ 'name', 'isbn', 'access_code', 'author', 'edition', 'issue_to', 'cost',  'issue_date', 'ret_date', 'status', 'course']

class bookcopyadmin(admin.ModelAdmin):
    list_display = [field.name for field in Book_Copies._meta.get_fields()]

class Messageadmin(admin.ModelAdmin):
    list_display = [field.name for field in Message._meta.get_fields()]

class FileAdmin(admin.ModelAdmin):
    list_display = ['file', 'title', 'description', 'date_uploaded', 'user', ]

class Notiadmin(admin.ModelAdmin):
    list_display = [field.name for field in Notification._meta.get_fields()]

class Transadmin(admin.ModelAdmin):
    list_display = [field.name for field in TransactionLog._meta.get_fields()]

class Magadmin(admin.ModelAdmin):
    list_display = [field.name for field in Magazine._meta.get_fields()]
# Register your models here.
admin.site.register(Users, StudAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Book_Copies, bookcopyadmin)
admin.site.register(Message, Messageadmin)
admin.site.register(File, FileAdmin)
admin.site.register(Notification, Notiadmin)
admin.site.register(TransactionLog, Transadmin )
admin.site.register(Magazine, Magadmin)


