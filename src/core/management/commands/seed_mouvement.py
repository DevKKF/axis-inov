from django.core.management.base import BaseCommand
from production.models import Mouvement  # adapte ce chemin si besoin

class Command(BaseCommand):
    help = 'Seed initial data for Mouvement'

    def handle(self, *args, **kwargs):
        data = [
            {"code": "OUVSIN", "type_mouvement_id": "2", "libelle": "Ouverture Sinistre", "type": "SINISTRE"},
            {"code": "VERIGARANTIE", "type_mouvement_id": "2", "libelle": "Vérification de la garantie", "type": "SINISTRE"},
            {"code": "ACCRECEPCLIENT", "type_mouvement_id": "2", "libelle": "Accusé réception client", "type": "SINISTRE"},
            {"code": "TRANSCIE", "type_mouvement_id": "2", "libelle": "Transmission à la compagnie", "type": "SINISTRE"},
            {"code": "SAISPROV", "type_mouvement_id": "2", "libelle": "Saisie d'une provision", "type": "SINISTRE"},
            {"code": "DEMDOCCLT", "type_mouvement_id": "2", "libelle": "Demande de documents au client", "type": "SINISTRE"},
            {"code": "RECEPDOCLCT", "type_mouvement_id": "2", "libelle": "Réception des documents du client", "type": "SINISTRE"},
            {"code": "NOMMEXPERT", "type_mouvement_id": "2", "libelle": "Nomination d'un expert", "type": "SINISTRE"},
            {"code": "TRANSDOCEXPERT", "type_mouvement_id": "2", "libelle": "Transmission de document à l'expert", "type": "SINISTRE"},
            {"code": "RELANCEXPERT", "type_mouvement_id": "2", "libelle": "Relance de l'expert", "type": "SINISTRE"},
            {"code": "RELANCCIE", "type_mouvement_id": "2", "libelle": "Relance de la compagnie", "type": "SINISTRE"},
            {"code": "AUTRES", "type_mouvement_id": "2", "libelle": "Autres", "type": "SINISTRE"},
            {"code": "RECEPREG", "type_mouvement_id": "2", "libelle": "Réception du réglement / Prise en charge", "type": "SINISTRE"},
            {"code": "TRANSREG", "type_mouvement_id": "2", "libelle": "Transmission règlement", "type": "SINISTRE"},
            {"code": "SAISIREG", "type_mouvement_id": "2", "libelle": "Saisie du règlement", "type": "SINISTRE"},
            {"code": "VERISUPPROV", "type_mouvement_id": "2", "libelle": "Vérification / Suppression provision", "type": "SINISTRE"},
            {"code": "CLOTSIN", "type_mouvement_id": "2", "libelle": "Clôture du sinistre", "type": "SINISTRE"},
        ]

        for item in data:
            obj, created = Mouvement.objects.get_or_create(
                code=item["code"],
                type_mouvement_id=item["type_mouvement_id"],
                libelle=item["libelle"],
                type=item["type"],
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"{item['libelle']} ajouté avec succès."))
            else:
                self.stdout.write(self.style.WARNING(f"{item['libelle']} existe déjà."))
