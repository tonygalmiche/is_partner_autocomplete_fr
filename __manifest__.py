# -*- coding: utf-8 -*-
{
    "name"       : "Autocomplete SIRET/SIREN/TVA (API gouv.fr)",
    "version"    : "18.0.1.0.0",
    "author"     : "InfoSaône / Tony Galmiche",
    "maintainer" : "InfoSaône",
    "website"    : "http://www.infosaone.com",
    "category"   : "InfoSaône",
    "description": """
Complète automatiquement les champs SIRET, SIREN et TVA intracommunautaire
d'un partenaire français à partir de l'API publique et gratuite
recherche-entreprises.api.gouv.fr (sans abonnement payant).
===================================================
""",
    "depends"    : [
        "base",
        "l10n_fr",
    ],
    "data" : [
        "data/ir_actions_server.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
