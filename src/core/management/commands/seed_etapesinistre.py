from django.core.management.base import BaseCommand
from configurations.models import EtapeSinistre  # adapte ce chemin si besoin

class Command(BaseCommand):
    help = 'Seed initial data for EtapeSinistre'

    def handle(self, *args, **kwargs):
        data = [
            {"code": "OUVSIN", "numero_ordre": "1", "libelle": "Ouverture Sinistre", "type_etape": "OBLIGATOIRE"},
            {"code": "VERIGARANTIE", "numero_ordre": "2", "libelle": "Vérification de la garantie", "type_etape": "OBLIGATOIRE"},
            {"code": "ACCRECEPCLIENT", "numero_ordre": "3", "libelle": "Accusé réception client", "type_etape": "OBLIGATOIRE"},
            {"code": "TRANSCIE", "numero_ordre": "4", "libelle": "Transmission à la compagnie", "type_etape": "OBLIGATOIRE"},
            {"code": "SAISPROV", "numero_ordre": "5", "libelle": "Saisie d'une provision", "type_etape": "FACULTATIF"},
            {"code": "DEMDOCCLT", "numero_ordre": "6", "libelle": "Demande de documents au client", "type_etape": "FACULTATIF"},
            {"code": "RECEPDOCLCT", "numero_ordre": "7", "libelle": "Réception des documents du client", "type_etape": "FACULTATIF"},
            {"code": "NOMMEXPERT", "numero_ordre": "8", "libelle": "Nomination d'un expert", "type_etape": "FACULTATIF"},
            {"code": "TRANSDOCEXPERT", "numero_ordre": "9", "libelle": "Transmission de document à l'expert", "type_etape": "FACULTATIF"},
            {"code": "RELANCEXPERT", "numero_ordre": "10", "libelle": "Relance de l'expert", "type_etape": "FACULTATIF"},
            {"code": "RELANCCIE", "numero_ordre": "11", "libelle": "Relance de la compagnie", "type_etape": "FACULTATIF"},
            {"code": "AUTRES", "numero_ordre": "12", "libelle": "Autres", "type_etape": "FACULTATIF"},
            {"code": "RECEPREG", "numero_ordre": "13", "libelle": "Réception du réglement / Prise en charge", "type_etape": "FACULTATIF"},
            {"code": "TRANSREG", "numero_ordre": "14", "libelle": "Transmission règlement", "type_etape": "FACULTATIF"},
            {"code": "SAISIREG", "numero_ordre": "15", "libelle": "Saisie du règlement", "type_etape": "OBLIGATOIRE"},
            {"code": "VERISUPPROV", "numero_ordre": "16", "libelle": "Vérification / Suppression provision", "type_etape": "OBLIGATOIRE"},
            {"code": "CLOTSIN", "numero_ordre": "17", "libelle": "Clôture du sinistre", "type_etape": "OBLIGATOIRE"},
        ]

        for item in data:
            obj, created = EtapeSinistre.objects.get_or_create(
                code=item["code"],
                numero_ordre=item["numero_ordre"],
                libelle=item["libelle"],
                type_etape=item["type_etape"],
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"{item['libelle']} ajouté avec succès."))
            else:
                self.stdout.write(self.style.WARNING(f"{item['libelle']} existe déjà."))
