from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.contrib.auth.forms import UserCreationForm  # admin panelde 'add user' formasin qayta jaziw ushin 

from .models import User


# superadmin admin-lerdi jaratiw ushin jana forma jarattiq, sebebi magluwmatlar toliq boliwi kerek
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # add user formasinda koriniw kerek fieldlar usi jerge jaziliwi shart
        fields = ('phone_number', 'first_name', 'last_name', 'address', 'role', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Usi 3 field toltiriw majburiy qildim, sebebi adminlerdin magluwmatlari toliq boliwi ushin
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['address'].required = True

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    # jaratilgan taza formani UserAdmin-ge tanistirdim, taza formadagi shartler menen isleydi endi
    add_form = CustomUserCreationForm
 
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('User info', {'fields': ('first_name', 'last_name', 'address', 'telegram_id')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('last_login', 'created_at', 'updated_at')})
    )

    add_fieldsets = (
        (None, {'fields': ('phone_number', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'address')}),
        ('Role $ Status', {'fields': ('role', 'is_active')}),
    )
    
    list_display = ['phone_number', 'first_name', 'last_name', 'role', 'id', 'is_active']
    list_filter = ['role', 'created_at', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['phone_number', 'first_name', 'last_name', 'id', 'address']
    readonly_fields = ['is_staff', 'is_superuser', 'role', 'phone_number', 'first_name', 'last_name', 'created_at', 'updated_at', 'last_login', 'date_joined', 'telegram_id', 'address']


    # add_fieldset islewi ushin
    def get_fieldsets(self, request, obj = None):
        if not obj: # eger obekt joq bolsa. taza user qosilip atirgan bolsa
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
    

    # read_only fields taza user qosip atirganda kesent etpew ushin, olardi aylanip otiw ushin
    def get_readonly_fields(self, request, obj = None):
        
        # taza user qosilip atirganda hesh narse read_only bolmasin
        if not obj:
            return ()
        
        # eger admin panelge kirip turgan superuser bolsa
        if request.user.is_superuser:

            # eger (change user) qayttan bir jerlerdi orgertirmekshi bolgan user admin yamasa superadmin rolindegi user bolsa
            if obj.role == User.ADMIN or obj.role == User.SUPER_ADMIN:
                # tek gana o'zgertiwip bomaytugin fieldlardi qaytaramiz, sonda qalganlarin o'zgertiwge boladi
                return ('telegram_id', 'role', 'is_staff', 'is_superuser', 'last_login', 'created_at', 'updated_at')
        
            # eger (change user) client bolsa
            elif obj.role == User.CLIENT:
                # tek password ozgerte aladi
                # qalgan bari ozgetiwge qadagan
                return ('phone_number', 'first_name', 'last_name', 'address', 'telegram_id', 'role', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'created_at', 'updated_at')
        
        return super().get_readonly_fields(request, obj)
        # return self.readonly_fields
    


    # taza user jaratip atirganda Roleler diziminen Clientti alip taslaydi, sebebi admin panelden tek superuser ham admin jaratiw mumkin
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "role":
            # URL di teksiremiz. eger aqiri '_add' penen tawsilse, yaza user qosiw  aynasi bildiredi
            if request.resolver_match and request.resolver_match.url_name.endswith('_add'):
                kwargs['choices'] = (
                    (User.ADMIN, 'Admin'),
                    # (User.SUPER_ADMIN, 'Super_admin'),
                )
        return super().formfield_for_choice_field(db_field, request, **kwargs)
    




    
    # admin panelde modeldi korsetiwge ruxsat
    def has_module_permission(self, request):
        if request.user.is_authenticated and request.user.role == User.ADMIN:
            return True
        return super().has_module_permission(request)

    # listin koriwge ruxsat
    def has_view_permission(self, request, obj=None):
        if request.user.is_authenticated and request.user.role == User.ADMIN:
            return True
        return super().has_view_permission(request, obj)





    # kiritilgen paroldi heshlab saqlaw ushin
    def save_model(self, request, obj, form, change):   # bul metod tek action orinlaydi return shart emes

        # User Rolleri boyinsha ruxsatlardi belgilew logikasi
        if obj.role == User.SUPER_ADMIN:
            obj.is_staff =True
            obj.is_superuser = True

        elif obj.role == User.ADMIN:
            obj.is_staff = True
            obj.is_superuser = False

        elif obj.role == User.CLIENT:
            obj.is_staff = False
            obj.is_superuser = False
            

        """
        password bar bolsa ham hash qilinbagan bolsa hashlaydi
        pbkdf2 - hashing algoritmi
        sha256 - hash funksiya
        $ - ajratqish
        """
        if obj.password and not obj.password.startswith('pbkdf2_sha256$'):
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
    





