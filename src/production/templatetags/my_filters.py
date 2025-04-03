import re
import base64
import datetime
from pprint import pprint
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from datetime import date
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import math
from django.utils.text import slugify

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from num2words import num2words

register = template.Library()

@register.filter
def money_field(montant):
    if montant == "" or montant is None: montant = 0
    money = intcomma(int(montant))
    money = money.replace(',', ' ')
    return money


@register.filter
def round_value(value, decimal_places=0):
    """Arrondit la valeur à un certain nombre de décimales."""
    try:
        return round(float(value), decimal_places)
    except (ValueError, TypeError):
        return value  # En cas d'erreur, retourner la valeur sans modification 


@register.filter
def multiply(a, b):
    return a * b

@register.filter
def diviser(a, b):
    return a / b


@register.filter
def today_utc():
    return datetime.datetime.now(tz=datetime.timezone.utc)


@register.filter(name='subtract')
def subtract(value, arg):
    if value is not None and arg is not None:
        return Decimal(value) - Decimal(arg)
    else:
        return value


@register.filter(name='addition')
def addition(value, arg):
    value = value if value is not None else 0
    arg = arg if arg is not None else 0
    return value + arg


@register.filter
def with_user(total_part_compagnie_medicament, user):
    return total_part_compagnie_medicament(user)


@register.filter
def truncate_last_word(value, max_length):
    """
    Truncate a string to a maximum length, keeping the last word intact.
    """
    if len(value) <= max_length:
        return value

    # Split the string into words
    words = value.split()

    # Join all words except the last one
    truncated_text = ' '.join(words[:-1])

    # Add an ellipsis to indicate that the text has been truncated
    truncated_text += '...'

    return truncated_text


@register.filter
def index(List, i):
    return List[int(i)]


@register.filter
def entry_num_array(List):
    return range(len(List))


@register.filter
def replace_espace(value):
    return value.replace(' ', '-')


@register.filter
def replace_custom(value, arg):
    return value.replace(arg, '-')


@register.filter
def date_heure_locale(date_heure_gmt, fuseau_horaire):
    dhl = date_heure_gmt + timedelta(hours=fuseau_horaire)
    return dhl


@register.filter
def nombre_en_lettre(nombre):
    try:
        return num2words(nombre, lang='fr')
    except Exception as e:
        return ''


@register.filter
def subdiviser_mots(chaine, longueur=10):

    if chaine is None or chaine == "":
        return ""
    # Séparer la chaîne en mots
    mots = chaine.split()
    
    # Liste pour stocker les résultats
    resultat = []
    
    for mot in mots:
        # Si le mot est plus long que 'longueur', le subdiviser
        if len(mot) > longueur:
            segments = [mot[i:i+longueur] for i in range(0, len(mot), longueur)]
            resultat.append(' '.join(segments))
        else:
            # Ajouter le mot tel quel s'il est plus court ou égal à 'longueur'
            resultat.append(mot)
    
    # Reconstituer la chaîne avec des espaces entre les mots
    return ' '.join(resultat)


@register.filter(name='to_base64')
def to_base64(file):
    try:
        # Lire le fichier binaire
        print('file.path')
        print(file.path)
        value = open(file.path, 'rb')
        print('value')
        print(value)
        fichier_binaire = value.read()
        # Encoder en base64
        fichier_base64 = base64.b64encode(fichier_binaire)
        # Retourner en tant que chaîne (utf-8)
        return fichier_base64.decode('utf-8')
    except Exception as e:
        return ''  # Retourne une chaîne vide si quelque chose échoue


@register.filter
def money_format_mille(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (ValueError, TypeError):
        return value


@register.filter
def format_montant(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (ValueError, TypeError):
        return value


@register.simple_tag
def date_du_jour():
    """
    Retourne la date du jour.
    """
    return date.today()


# Suppression des espaces entre les mots
def supprimer_espaces(chaine):
    return ''.join(str(chaine).split())


#Convertir une date en format AAAA-MM-JJ
def convertir_date_multiformat(date_str):
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None


#Convertir une date en format JJ/MM/AAAA
@register.filter
def convertir_date_jj_mm_aaaa(date_str):
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%d/%m/%Y')
        except ValueError:
            continue
    return None


@register.filter
def rendre_html(value):
    if not value:
        return ''
    return mark_safe(value)


def arrondis_nombre(value: float) -> int:
    """
    Arrondit un nombre à l'entier supérieur ou inférieur en fonction des décimales.

    - Si la partie décimale est >= 0.5, arrondit à l'entier supérieur.
    - Sinon, arrondit à l'entier inférieur.

    Args:
        value (float): Le nombre à arrondir.

    Returns:
        int: Le nombre arrondi.
    """
    integer_part = math.floor(value)  # Partie entière
    decimal_part = value - integer_part  # Partie décimale

    if decimal_part >= 0.5:
        return math.ceil(value)  # Arrondi à l'entier supérieur
    return integer_part  # Arrondi à l'entier inférieur



def transformer_statut(statut):
    """Transforme un statut en minuscules avec des tirets."""
    if statut:
        return slugify(statut)
    else:
        return ""  # Retourne une chaîne vide si le statut est None


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

