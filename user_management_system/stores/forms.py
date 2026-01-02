from django import forms
from django.core.exceptions import ValidationError
from .models import Category, Product, Store, CartItem, ProductSizeStock


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
    # حقل المقاسات مع الكميات
    size_stocks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'أدخل المقاسات والكميات، مثال:\nS:5\nM:10\nL:8\nXL:3\nXXL:2'
        }),
        help_text='أدخل المقاسات والكميات، كل سطر: المقاس:الكمية'
    )
    
    class Meta:
        model = Product
        fields = ["name", "image", "price", "sizes", "description"]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المنتج'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'وصف المنتج'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'السعر'}),
            'sizes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: S, M, L, XL, XXL'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        # إذا كان هناك منتج موجود، املأ حقل size_stocks
        if instance and instance.pk:
            size_stocks_list = []
            for size_stock in instance.size_stocks.all().order_by('size'):
                size_stocks_list.append(f"{size_stock.size}:{size_stock.stock}")
            self.fields['size_stocks'].initial = '\n'.join(size_stocks_list)
    
    def clean_size_stocks(self):
        """تنظيف وتف Parse حقل المقاسات والكميات"""
        size_stocks_data = self.cleaned_data.get('size_stocks', '')
        if not size_stocks_data:
            return {}
        
        size_stocks_dict = {}
        for line in size_stocks_data.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                parts = line.split(':', 1)
                size = parts[0].strip()
                try:
                    stock = int(parts[1].strip())
                    if stock < 0:
                        raise ValidationError(f'الكمية للمقاس {size} يجب أن تكون أكبر من أو تساوي صفر.')
                    size_stocks_dict[size] = stock
                except ValueError:
                    raise ValidationError(f'الكمية للمقاس {size} غير صحيحة.')
        
        return size_stocks_dict
    
    def save(self, commit=True):
        product = super().save(commit=False)
        
        # حساب إجمالي الكمية
        size_stocks_dict = self.cleaned_data.get('size_stocks', {})
        total_stock = sum(size_stocks_dict.values())
        product.stock = total_stock
        
        if commit:
            product.save()
            
            # حفظ الكميات حسب المقاس
            if size_stocks_dict:
                # حذف المقاسات القديمة
                product.size_stocks.all().delete()
                
                # إضافة المقاسات الجديدة
                for size, stock in size_stocks_dict.items():
                    ProductSizeStock.objects.create(
                        product=product,
                        size=size,
                        stock=stock
                    )
        
        return product


class AddToCartForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control', 'style':'width:80px; display:inline-block;'}))

    class Meta:
        model = CartItem
        fields = ['quantity']