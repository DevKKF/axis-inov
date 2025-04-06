from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.models import InfoActe
from configurations.models import KeyValueData, User, TypePrestataire, Prestataire, Acte, Bureau, ModeReglement, \
    TypeActe, Civilite, QualiteBeneficiaire, Pays, Profession
from production.models import Aliment, Carte, Client, FormuleGarantie, Bareme, CarteDigitalDematerialisee
from sinistre.models import Sinistre, DemandeRemboursementMobile

from grh.models import Prospect



class InfoActeSerialiser(ModelSerializer):
    class Meta:
        model = InfoActe
        fields = ['numero_assure', 'medecin', 'acte', 'affection', 'rc']
        managed = False

class TypeActeSerialiser(ModelSerializer):
    class Meta:
        model = TypeActe
        fields = ['id', 'code', 'libelle']
        managed = False

class CiviliteSerializer(ModelSerializer):
    class Meta:
        model = Civilite
        fields = ['id', 'code', 'name']
        managed = False


class QualiteBeneficiaireSerializer(ModelSerializer):
    class Meta:
        model = QualiteBeneficiaire
        fields = ['id', 'code', 'libelle']
        managed = False

class PaysSerializer(ModelSerializer):
    class Meta:
        model = Pays
        fields = ['id', 'nom', 'indicatif']
        managed = False
        # depth = 1


class ProfessionSerializer(ModelSerializer):
    class Meta:
        model = Profession
        fields = ['id', 'code', 'name']
        managed = False
        # depth = 1



# APPLICATION MOBILE SANTE API REST SERIALIZER
class KeyValueDataSerializer(ModelSerializer):
    class Meta:
        model = KeyValueData
        fields = "__all__"
        managed = False


class CarteSerializer(ModelSerializer):
    class Meta:
        model = Carte
        fields = "__all__"
        # depth = 3
        # extra_kwargs = {'user_extranet': {'write_only': True}}


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"
        # depth = 3
        # extra_kwargs = {'user_extranet': {'write_only': True}}

# class CourrierSerializer(ModelSerializer):
#     class Meta:
#         model = Courrier
#         fields = "__all__"


class FormuleGarantieSerializer(ModelSerializer):
    class Meta:
        model = FormuleGarantie
        fields = "__all__"
        depth = 1
        # extra_kwargs = {'user_extranet': {'write_only': True}}


class BarremeSerializer(ModelSerializer):
    class Meta:
        model = Bareme
        fields = "__all__"
        depth = 1
        # extra_kwargs = {'user_extranet': {'write_only': True}}

class TypePrestataireSerializer(ModelSerializer):
    class Meta:
        model = TypePrestataire
        fields = "__all__"
        # depth = 1

class PrestataireSerializer(ModelSerializer):
    class Meta:
        model = Prestataire
        fields = "__all__"
        depth = 1

class PrestataireWebSerializer(ModelSerializer):
    class Meta:
        model = Prestataire
        fields = "__all__"
        depth = 1

class AlimentSerializer(ModelSerializer):
    carte = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()
    formule = serializers.SerializerMethodField()
    # formules = FormuleGarantieSerializer(many=True)
    class Meta:
        model = Aliment
        fields = ["id",
                  "sms_active",
                  "veos_id_npol",
                  "veos_code_aliment",
                  "veos_adherent_principal",
                  "veos_adherent_principal_id_per",
                  "veos_code_qualite_beneficiaire",
                  "veos_code_formule",
                  "veos_code_college",
                  "veos_numero_carte",
                  "observation",
                  "nom",
                  "prenoms",
                  "nom_jeune_fille",
                  "date_naissance",
                  "lieu_naissance",
                  "genre",
                  "email",
                  "numero_securite_sociale",
                  "numero",
                  "numero_famille",
                  "matricule_employe",
                  "matricule_cie",
                  "date_affiliation",
                  "date_sortie",
                  "photo",
                  "statut_familiale",
                  "numero_piece",
                  "code_postal",
                  "ville",
                  "adresse",
                  "telephone_fixe",
                  "telephone_mobile",
                  "rib",
                  "surprime_ht",
                  "surprime_ttc",
                  "plafond_extra",
                  "apci_ald",
                  "plafond_individuel",
                  "plafond_famille",
                  "commentaire",
                  "statut",
                  "created_at",
                  "updated_at",
                  "bureau",
                  "adherent_principal",
                  "qualite_beneficiaire",
                  "civilite",
                  "pays_naissance",
                  "pays_residence",
                  "pays_activite_professionnelle",
                  "profession",
                  "user_extranet",
                  "carte",
                  "client",
                  "formule",
                  "photo",
                  ]
        depth = 1
        # extra_kwargs = {'user_extranet': {'write_only': True}}

    def get_carte(self, obj):
        try:
            carte = obj.carte_active()
            return CarteSerializer(carte).data
        except Carte.DoesNotExist:
            return None

    def get_client(self, obj):
        try:
            client = obj.client()
            return ClientSerializer(client).data
        except Client.DoesNotExist:
            return None

    def get_formule(self, obj):
        try:
            formule = obj.formule
            return FormuleGarantieSerializer(formule).data
        except FormuleGarantie.DoesNotExist:
            return None


class UserDataSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}
        # depth = 1

class PrestataireDataSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {'password': {'write_only': True}}
        depth = 2


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, required=False, write_only=True)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data.get('password', user.password))
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        if validated_data.get('password', None):
            instance.set_password(validated_data.get('password', instance.password))
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance


class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)

    def create(self, validated_data):
        user = User(email=validated_data.get('email', None),
                    username=validated_data.get('username', None))
        user.set_password(validated_data.get('password', user.password))
        return user


class ResetPasswordUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        if validated_data.get('password', None):
            instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance


class SinisteSerializer(ModelSerializer):
    class Meta:
        model = Sinistre
        fields = "__all__"
        depth = 1
        # extra_kwargs = {'user_extranet': {'write_only': True}}


class ActeSerializer(ModelSerializer):
    class Meta:
        model = Acte
        fields = "__all__"
        # exclude = ['rubrique','regroupement_acte','type_acte',]
        # depth = 1
        # extra_kwargs = {'user_extranet': {'write_only': True}}


class BureauSerializer(ModelSerializer):
    class Meta:
        model = Bureau
        fields = "__all__"
        # exclude = ['rubrique','regroupement_acte','type_acte',]
        # depth = 1
        # extra_kwargs = {'user_extranet': {'write_only': True}}

class ModeRemboursementSerializer(ModelSerializer):
    class Meta:
        model = ModeReglement
        fields = ['id', 'libelle']

class DemandeRemboursementSerializer(ModelSerializer):
    class Meta:
        model = DemandeRemboursementMobile
        fields = "__all__"

class ProspectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        fields = '__all__'


class CarteDigitalDematerialiseeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarteDigitalDematerialisee
        fields = ['id', 'user', 'has_digital_card', 'digital_card_url', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'user': {'required': True},
            'digital_card_url': {'required': True}
        }

    def create(self, validated_data):
        user = validated_data.pop('user', None)
        digital_card = CarteDigitalDematerialisee.objects.create(user=user, **validated_data)
        return digital_card