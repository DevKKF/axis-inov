from django import forms

from configurations.models import Apporteur
from production.models import Contact, Filiale, Acompte, Document, Aliment, Police , Courrier


class ClientForm(forms.ModelForm):
    def clean(self):

        prenoms = self.cleaned_data.get('prenoms')
        date_naissance = self.cleaned_data.get('date_naissance')

        type_personne = self.cleaned_data.get('type_personne')
        if type_personne.id == 1 and prenoms == None:
            self.cleaned_data['prenoms'] = "Le champs prénoms est obligatoire."
            raise forms.ValidationError("Le champs prénoms est obligatoire.")

        if type_personne.id == 1 and date_naissance == None:
            self.cleaned_data['date_naissance'] = "Le champs Date de naissance est obligatoire."
            #raise forms.ValidationError("Le champs Date de naissance est obligatoire.")

        return self.cleaned_data
        

class PoliceForm(forms.ModelForm):
    class Meta:
        model = Police
        fields = ['produit', ]


    def __init__(self, *args, **kwargs):
        super(PoliceForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        #if instance and instance.pk:
        '''self.fields['commission_gestion'].widget.attrs['readonly'] = True
        self.fields['commission_apport'].widget.attrs['readonly'] = True
        self.fields['commission_annuelle'].widget.attrs['readonly'] = True
        self.fields['verif'].widget.attrs['readonly'] = True'''



#
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['nom', 'prenoms','fonction','telephone','email',]

#
class FilialeForm(forms.ModelForm):
    class Meta:
        model = Filiale
        fields = ['nom', 'adresse', 'pays', 'ville', ]

#
# class CourrierForm(forms.ModelForm):
#     class Meta:
#         model = Courrier
#         fields = ['code', 'designation', 'service', 'status']

#
class AcompteForm(forms.ModelForm):
    class Meta:
        model = Acompte
        fields = ['debit', 'credit', 'date_versement' ]


#
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['nom', 'fichier', 'type_document','confidentialite', 'commentaire', ]


#
class AlimentForm(forms.ModelForm):
    class Meta:
        model = Aliment
        fields = []




class ApporteurAdminForm(forms.ModelForm):
    class Meta:
        model = Apporteur
        exclude = ['bureau', 'created_by', 'id_per']  # Excluez le champ bureau du formulaire



class PhotoUploadForm(forms.Form):
    file = forms.ImageField()
