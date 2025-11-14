from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import User






class CustomUserCreationForm(UserCreationForm):
    """نموذج تسجيل مستخدم جديد، مع دعم إنشاء المدير"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'البريد الإلكتروني'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأخير'})
    )

    # خيارات نوع المستخدم للتسجيل (بدون admin للأمان)
    REGISTRATION_USER_TYPE_CHOICES = [
        ('user', 'مستخدم عادي'),
        ('store_owner', 'صاحب متجر'),
        
    ]
    user_type = forms.ChoiceField(
        choices=REGISTRATION_USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='ملاحظة: لا يمكن إنشاء حساب مدير من خلال التسجيل العام لأسباب أمنية'
    )

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'رقم الهاتف (اختياري)'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'user_type', 
                  'phone_number', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'اسم المستخدم'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'كلمة المرور'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'تأكيد كلمة المرور'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.user_type = self.cleaned_data['user_type']
        user.phone_number = self.cleaned_data['phone_number']

        # إذا كان admin، اجعل المستخدم superuser و staff
        if user.user_type == 'admin':
            user.is_staff = True
            user.is_superuser = True

        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """نموذج تسجيل الدخول المخصص بالبريد الإلكتروني أو اسم المستخدم"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'اسم المستخدم أو البريد الإلكتروني'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'كلمة المرور'})

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # البحث عن المستخدم بالبريد الإلكتروني إذا كان الإدخال يحتوي على @
            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    pass

            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )

            if self.user_cache is None:
                raise forms.ValidationError('اسم المستخدم أو كلمة المرور غير صحيحة.', code='invalid_login')
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class UserProfileForm(forms.ModelForm):
    """نموذج تحديث الملف الشخصي"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 
                  'address', 'date_of_birth', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


# class StoreCreationForm(forms.ModelForm):
#     """نموذج إنشاء متجر جديد"""

#     class Meta:
#         model = Store
#         fields = ('name', 'description', 'logo', 'address', 'phone', 'email', 'website')
#         widgets = {
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
#             'logo': forms.FileInput(attrs={'class': 'form-control'}),
#             'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#             'phone': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'website': forms.URLInput(attrs={'class': 'form-control'}),
#         }

#     def __init__(self, *args, **kwargs):
#         self.user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)

#     def save(self, commit=True):
#         store = super().save(commit=False)
#         if self.user:
#             store.owner = self.user
#         if commit:
#             store.save()
#         return store


class PasswordChangeForm(forms.Form):
    """نموذج تغيير كلمة المرور"""

    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور الحالية'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور الجديدة'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'تأكيد كلمة المرور الجديدة'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('كلمة المرور الحالية غير صحيحة.')
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError('كلمات المرور الجديدة غير متطابقة.')

        return cleaned_data

    def save(self):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        self.user.save()
        return self.user
