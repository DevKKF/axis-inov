from django import forms
from django.contrib.auth.models import Permission
from .models import Tarif, Compagnie, Banque, Branche, Garantie, GarantieBranche, Formule, GarantieFormule


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = '__all__'
        widgets = {
            'permissions': forms.CheckboxSelectMultiple(),  # Utiliser le widget CheckboxSelectMultiple pour les cases à cocher
        }


class ActeAdminForm(forms.ModelForm):
    class Meta:
        model = Compagnie
        exclude = ['delais_carence']  # Excluez le champ bureau du formulaire

class TarifForm(forms.ModelForm):
    class Meta:
        model = Tarif
        exclude = ['code_acte']  # Exclude the 'code' field from the form


class CompagnieAdminForm(forms.ModelForm):
    class Meta:
        model = Compagnie
        exclude = ['bureau']  # Excluez le champ bureau du formulaire


class BanqueAdminForm(forms.ModelForm):
    class Meta:
        model = Banque
        exclude = ['bureau', 'created_by']  # Excluez le champ bureau du formulaire


class GarantieBrancheForm(forms.ModelForm):
    branche = forms.ModelChoiceField(
        queryset=Branche.objects.filter(status=True),
        label="Branche",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    garanties = forms.ModelMultipleChoiceField(
        queryset=Garantie.objects.all(),
        label="Garanties",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = GarantieBranche
        fields = ['branche', 'status']


class GarantieFormuleForm(forms.ModelForm):
    formule = forms.ModelChoiceField(
        queryset=Formule.objects.filter(status=True),
        label="formule",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    garanties = forms.ModelMultipleChoiceField(
        queryset=Garantie.objects.all(),
        label="Garanties",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = GarantieFormule
        fields = ['formule', 'status']
