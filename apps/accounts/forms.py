from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

STYLE_CLASS = 'w-full bg-slate-900/50 border border-slate-700 rounded-xl px-4 py-3 outline-none focus:border-indigo-500 transition-colors text-white placeholder-slate-500'

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply style to all fields (email, password, confirmation)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': STYLE_CLASS,
                'placeholder': field.label
            })

class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.TextInput(attrs={
        'class': STYLE_CLASS,
        'placeholder': 'Email address'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': STYLE_CLASS,
        'placeholder': 'Password'
    }))
