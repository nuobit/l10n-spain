# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    aeat_perception_key_id = fields.Many2one(
        comodel_name="l10n.es.aeat.report.perception.key",
        string="Clave percepción",
        help="Se consignará la clave alfabética que corresponda a las "
        "percepciones de que se trate.",
        compute="_compute_aeat_perception_keys",
        store=True,
    )
    aeat_perception_subkey_id = fields.Many2one(
        comodel_name="l10n.es.aeat.report.perception.subkey",
        string="Subclave",
        help="""Tratándose de percepciones correspondientes a las claves
                    B, E, F, G, H, I, K y L, deberá consignarse, además, la
                    subclave numérica de dos dígitos que corresponda a las
                    percepciones de que se trate, según la relación de
                    subclaves que para cada una de las mencionadas claves
                    figura a continuación.
                    En percepciones correspondientes a claves distintas de las
                    mencionadas, no se cumplimentará este campo.
                    Cuando deban consignarse en el modelo 190
                    percepciones satisfechas a un mismo perceptor que
                    correspondan a diferentes claves o subclaves de
                    percepción, deberán cumplimentarle tantos apuntes o
                    registros de percepción como sea necesario, de forma que
                    cada uno de ellos refleje exclusivamente los datos de
                    percepciones correspondientes a una misma clave y, en
                    su caso, subclave.""",
        compute="_compute_aeat_perception_keys",
        store=True,
    )

    @api.depends("move_id.aeat_perception_key_id")
    def _compute_aeat_perception_keys(self):
        if not self:
            return

        line_ids = tuple(self.ids)
        update_query = """
            WITH filtered_lines AS (
                SELECT line.id AS line_id,
                       move.aeat_perception_key_id,
                       move.aeat_perception_subkey_id
                FROM account_move_line AS line
                JOIN account_move AS move ON line.move_id = move.id
                WHERE line.id IN %(line_ids)s
                  AND move.move_type IN ('out_invoice', 'out_refund', 'in_refund', 'in_invoice')
                  AND COALESCE(line.exclude_from_invoice_tab, FALSE) = FALSE
                  AND move.aeat_perception_key_id IS NOT NULL
            ),
            updated_keys AS (
                UPDATE account_move_line AS line
                SET aeat_perception_key_id = filtered_lines.aeat_perception_key_id,
                    aeat_perception_subkey_id = filtered_lines.aeat_perception_subkey_id
                FROM filtered_lines
                WHERE line.id = filtered_lines.line_id
                RETURNING line.id AS updated_line_id
            )
            UPDATE account_move_line
            SET aeat_perception_key_id = NULL,
                aeat_perception_subkey_id = NULL
            WHERE id IN %(line_ids)s
            AND id NOT IN (SELECT updated_line_id FROM updated_keys);
        """
        self.env.cr.execute(update_query, {"line_ids": line_ids})
