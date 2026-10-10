# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _


class Agreement(models.Model):
    _inherit = "agreement"

    def _copy_content_from_template(self, template):
        """Copia consideraciones, secciones, cláusulas y anexos desde la plantilla."""
        self.ensure_one()
        if not template:
            return

        # Limpiar contenido previo si existiera
        self.recital_ids.unlink()
        self.sections_ids.unlink()
        self.clauses_ids.unlink()
        self.appendix_ids.unlink()
        self.line_ids.unlink()

        # 1. Copiar Recitals (Consideraciones)
        for recital in template.recital_ids:
            recital.copy({"agreement_id": self.id})

        # 2. Copiar Secciones
        section_map = {}
        for section in template.sections_ids:
            new_section = section.copy({
                "agreement_id": self.id,
                "clauses_ids": False,
            })
            section_map[section.id] = new_section.id

        # 3. Copiar Cláusulas asociadas a las secciones
        for clause in template.clauses_ids:
            values = {
                "agreement_id": self.id,
                "temp_agreement_id": self.id,
            }
            if clause.section_id:
                values["section_id"] = section_map.get(clause.section_id.id)
            clause.copy(values)

        # 4. Copiar Apéndices y Líneas
        for appendix in template.appendix_ids:
            appendix.copy({"agreement_id": self.id})
        for line in template.line_ids:
            line.copy({"agreement_id": self.id})

        self.message_post(
            body=_("Cláusulas y secciones cargadas automáticamente desde la plantilla %s") % template.display_name
        )

    @api.onchange("partner_id")
    def _onchange_partner_id_auto_contact(self):
        """Al seleccionar o cambiar el cliente, autoseleccionar su contacto primario."""
        if self.partner_id:
            if not self.partner_id.is_company:
                self.partner_contact_id = self.partner_id
            else:
                contact = self.env["res.partner"].search([
                    ("parent_id", "=", self.partner_id.id),
                ], limit=1, order="type asc, id asc")
                if contact:
                    self.partner_contact_id = contact

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.partner_id and not rec.partner_contact_id:
                if not rec.partner_id.is_company:
                    rec.partner_contact_id = rec.partner_id
                else:
                    contact = self.env["res.partner"].search([
                        ("parent_id", "=", rec.partner_id.id),
                    ], limit=1, order="type asc, id asc")
                    if contact:
                        rec.partner_contact_id = contact

            if rec.template_id and not rec.is_template and not rec.sections_ids:
                rec._copy_content_from_template(rec.template_id)
        return records

    def write(self, vals):
        res = super().write(vals)
        if "template_id" in vals and vals.get("template_id"):
            for rec in self:
                if not rec.is_template and not rec.sections_ids:
                    rec._copy_content_from_template(rec.template_id)
        return res

    implementation_order_id = fields.Many2one(
        "sale.order",
        string="Cotización de Implementación",
        domain="[('partner_id', 'child_of', partner_id)]",
        help="Cotización de servicios de implementación asociada a este contrato.",
    )
    monthly_order_id = fields.Many2one(
        "sale.order",
        string="Cotización Recurrente / Mensual",
        domain="[('partner_id', 'child_of', partner_id)]",
        help="Cotización recurrente o mensual asociada a este contrato.",
    )

    def _get_signature_date_text(self):
        """Retorna la fecha de firma en formato legal en español."""
        self.ensure_one()
        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        fecha = self.signature_date or self.start_date
        if fecha:
            return f"a los {fecha.day} días del mes de {meses[fecha.month - 1]} de {fecha.year}"
        return "a los _____ días del mes de _____________ de 2026"

    def _get_implementation_total(self):
        self.ensure_one()
        return self.implementation_order_id.amount_total or 0.0

    def _get_monthly_total(self):
        self.ensure_one()
        return self.monthly_order_id.amount_total or 0.0


