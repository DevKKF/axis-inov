from django.core.management.base import BaseCommand
from production.models import Motif  # adapte ce chemin si besoin

class Command(BaseCommand):
    help = 'Seed initial data for Motif'

    def handle(self, *args, **kwargs):
        data = [
            {"code": "OUVSIN", "mouvement_id": "17", "libelle": "Ouverture Sinistre", "etat_police": "En cours"},
            {"code": "VERIGARANTIE", "mouvement_id": "18", "libelle": "Vérification de la garantie", "etat_police": "Vérifaction garantie"},
            {"code": "ACCRECEPCLIENT", "mouvement_id": "19", "libelle": "Accusé réception client", "etat_police": "Réception client"},
            {"code": "TRANSCIE", "mouvement_id": "20", "libelle": "Transmission à la compagnie", "etat_police": "Transmission compagnie"},
            {"code": "SAISPROV", "mouvement_id": "21", "libelle": "Saisie d'une provision", "etat_police": "Provisionnement"},
            {"code": "DEMDOCCLT", "mouvement_id": "22", "libelle": "Demande de documents au client", "etat_police": "Documentation client"},
            {"code": "RECEPDOCLCT", "mouvement_id": "23", "libelle": "Réception des documents du client", "etat_police": "Réception document"},
            {"code": "NOMMEXPERT", "mouvement_id": "24", "libelle": "Nomination d'un expert", "etat_police": "Nomination expert"},
            {"code": "TRANSDOCEXPERT", "mouvement_id": "25", "libelle": "Transmission de document à l'expert", "etat_police": "Transmission document"},
            {"code": "RELANCEXPERT", "mouvement_id": "26", "libelle": "Relance de l'expert", "etat_police": "Relance expert"},
            {"code": "RELANCCIE", "mouvement_id": "27", "libelle": "Relance de la compagnie", "etat_police": "Relance compagnie"},
            {"code": "AUTRES", "mouvement_id": "28", "libelle": "Autres", "etat_police": "Autres"},
            {"code": "RECEPREG", "mouvement_id": "29", "libelle": "Réception du réglement / Prise en charge", "etat_police": "Réception réglement"},
            {"code": "TRANSREG", "mouvement_id": "30", "libelle": "Transmission règlement", "etat_police": "Transmission règlement"},
            {"code": "SAISIREG", "mouvement_id": "31", "libelle": "Saisie du règlement", "etat_police": "Saisie règlement"},
            {"code": "VERISUPPROV", "mouvement_id": "32", "libelle": "Vérification / Suppression provision", "etat_police": "Vérif / Supp provision"},
            {"code": "CLOTSIN", "mouvement_id": "33", "libelle": "Clôture du sinistre", "etat_police": "Clôture"},
        ]

        for item in data:
            obj, created = Motif.objects.get_or_create(
                code=item["code"],
                mouvement_id=item["mouvement_id"],
                libelle=item["libelle"],
                etat_police=item["etat_police"],
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"{item['libelle']} ajouté avec succès."))
            else:
                self.stdout.write(self.style.WARNING(f"{item['libelle']} existe déjà."))
