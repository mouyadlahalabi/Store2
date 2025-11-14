from django import forms
from django.core.exceptions import ValidationError
from .models import Category, Product, Store,CartItem


class StoreCreationForm(forms.ModelForm):
    """نموذج إنشاء متجر جديد"""

    class Meta:
        model = Store
        fields = ('name', 'description', 'logo', 'address', 'phone', 'email', 'website')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        """منع إنشاء متجر بنفس الاسم لنفس المستخدم"""
        name = self.cleaned_data.get('name')
        if self.user:
            existing = Store.objects.filter(owner=self.user, name__iexact=name).exists()
            if existing:
                raise ValidationError("لديك متجر بنفس هذا الاسم بالفعل.")
        return name

    def clean(self):
        """تحقق عام: يمكن منع المستخدم من إنشاء أكثر من متجر"""
        cleaned_data = super().clean()
        if self.user:
            existing_store = Store.objects.filter(owner=self.user).count()
            if existing_store >= 1:
                raise ValidationError("لا يمكنك إنشاء أكثر من متجر واحد في الوقت الحالي.")
        return cleaned_data

    def save(self, commit=True):
        store = super().save(commit=False)
        if self.user:
            store.owner = self.user
        if commit:
            store.save()
        return store


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم القسم'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف القسم'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "image", "price", "stock", "sizes", "description"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المنتج'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'وصف المنتج'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'السعر'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'الكمية في المخزون'}),
            'sizes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: S, M, L'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class AddToCartForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control', 'style':'width:80px; display:inline-block;'}))

    class Meta:
        model = CartItem
        fields = ['quantity']