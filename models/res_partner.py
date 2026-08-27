# -*- coding: utf-8 -*-
import logging

import requests

from odoo import models

_logger = logging.getLogger(__name__)

API_RECHERCHE_ENTREPRISES = "https://recherche-entreprises.api.gouv.fr/search"


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _is_rechercher_entreprise_gouv(self):
        """Interroge l'API publique et gratuite recherche-entreprises.api.gouv.fr
        et renvoie le premier résultat correspondant (ou None)."""
        self.ensure_one()
        query = self.siret or ('siren' in self._fields and self.siren) or self.name
        if not query:
            return None
        try:
            response = requests.get(
                API_RECHERCHE_ENTREPRISES,
                params={'q': query, 'per_page': 1},
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException:
            _logger.warning("Echec de l'appel à l'API recherche-entreprises.api.gouv.fr pour %s", self.display_name, exc_info=True)
            return None
        data = response.json()
        # En cas de résultat ambigu (plusieurs entreprises correspondent, typiquement
        # lors d'une recherche par nom), on préfère ne rien renseigner plutôt que de
        # prendre le mauvais SIRET/adresse.
        if data.get('total_results') != 1:
            return None
        resultats = data.get('results') or []
        return resultats[0] if resultats else None

    @staticmethod
    def _is_calculer_tva_intracom(siren):
        """Calcule le numéro de TVA intracommunautaire français à partir du SIREN (formule officielle)."""
        if not siren or not siren.isdigit() or len(siren) != 9:
            return False
        cle = (12 + 3 * (int(siren) % 97)) % 97
        return "FR%02d%s" % (cle, siren)

    def action_is_completer_siret_siren_tva(self):
        """Action serveur : renseigne les champs SIRET (+ SIREN si ce champ existe déjà
        sur res.partner, via les modules de facturation électronique) et TVA (s'ils
        sont vides) à partir de l'API gratuite recherche-entreprises.api.gouv.fr."""
        a_le_champ_siren = 'siren' in self._fields
        a_le_champ_nic = 'nic' in self._fields
        partenaires_non_trouves = self.env['res.partner']
        partenaires_completes = self.env['res.partner']
        for partner in self:
            resultat = partner._is_rechercher_entreprise_gouv()
            if not resultat:
                partenaires_non_trouves |= partner
                continue

            siege = resultat.get('siege') or {}
            siren = resultat.get('siren')
            siret = siege.get('siret')
            vals = {}
            if not partner.street:
                adresse = siege.get('adresse')
                code_postal = siege.get('code_postal')
                commune = siege.get('libelle_commune')
                if adresse:
                    vals['street'] = adresse
                if code_postal:
                    vals['zip'] = code_postal
                if commune:
                    vals['city'] = commune
                if adresse or code_postal or commune:
                    vals['country_id'] = self.env.ref('base.fr').id
            if a_le_champ_siren:
                # Le champ siret est calculé à partir de siren (+ nic) par les modules
                # de facturation électronique : on ne renseigne que siren/nic pour
                # éviter tout conflit d'écriture avec le siret.
                if siren and not partner.siren:
                    vals['siren'] = siren
                if a_le_champ_nic and siret and len(siret) == 14 and not partner.nic:
                    vals['nic'] = siret[9:]
            elif siret and not partner.siret:
                vals['siret'] = siret
            if siren and not partner.vat:
                vals['vat'] = partner._is_calculer_tva_intracom(siren)

            if vals:
                partner.write(vals)
                partenaires_completes |= partner
            else:
                partenaires_non_trouves |= partner

        if partenaires_non_trouves:
            message = "%s partenaire(s) complété(s). Aucune correspondance pour : %s" % (
                len(partenaires_completes),
                ", ".join(partenaires_non_trouves.mapped('display_name')),
            )
            notif_type = 'warning'
        else:
            message = "%s partenaire(s) complété(s) avec succès." % len(partenaires_completes)
            notif_type = 'success'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Complétion SIRET / SIREN / TVA",
                'message': message,
                'type': notif_type,
                'sticky': False,
                # Rafraîchit la vue courante (formulaire ou liste) pour afficher
                # les champs qui viennent d'être renseignés par l'action.
                'next': {
                    'type': 'ir.actions.client',
                    'tag': 'soft_reload',
                },
            },
        }
