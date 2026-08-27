# is_partner_autocomplete_fr

Complète automatiquement les champs SIRET, SIREN et TVA intracommunautaire
d'un partenaire français, à partir de l'API publique et **gratuite**
[recherche-entreprises.api.gouv.fr](https://recherche-entreprises.api.gouv.fr)
— sans abonnement payant, contrairement au service "Partner Autocomplete"
proposé par Odoo.

## Utilisation

Sur une fiche partenaire (ou une sélection de plusieurs partenaires dans la
liste), menu Action (⚙) > **Compléter SIRET / SIREN / TVA (gouv.fr)**.

Le module interroge l'API avec le SIRET du partenaire s'il est renseigné,
sinon son SIREN, sinon son nom. En cas de résultat ambigu (plusieurs
entreprises correspondent, typiquement lors d'une recherche par nom), rien
n'est renseigné plutôt que de prendre le mauvais SIRET/adresse.

Une notification récapitule le nombre de partenaires complétés et liste
ceux pour lesquels aucune correspondance n'a été trouvée.

## Champs renseignés

Uniquement les champs **actuellement vides** sont complétés (jamais
d'écrasement d'une valeur déjà saisie) :

- Adresse (rue, code postal, ville, pays) si le partenaire n'a pas déjà de
  rue renseignée.
- **SIREN** (+ **NIC**, si ces champs existent sur `res.partner` — ajoutés
  par les modules de facturation électronique). Le champ **SIRET** n'est
  renseigné directement que si ces champs séparés SIREN/NIC n'existent
  pas, pour éviter tout conflit avec le calcul automatique du SIRET fait
  par ces modules.
- **TVA intracommunautaire**, calculée à partir du SIREN via la formule
  officielle (`FR` + clé de contrôle + SIREN).

## Dépendances

- `base`, `l10n_fr`
- `requests` (bibliothèque Python, généralement déjà présente avec Odoo)

## Limites

- Fonctionne uniquement pour les entreprises françaises (l'API
  gouvernementale ne couvre que la France).
- Une recherche par nom peut renvoyer un résultat ambigu (plusieurs
  entreprises du même nom) — dans ce cas, rien n'est complété.
- Aucune clé d'API n'est nécessaire, mais l'API étant publique, elle peut
  être sujette à une limitation de débit en cas d'usage massif.
