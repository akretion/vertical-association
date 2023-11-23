# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# Copyright 2019 Onestein - Andrea Stirpe
# Copyright 2023 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MembershipLine(models.Model):
    _inherit = "membership.membership_line"
    _order = "date_to desc, id desc"

    category_id = fields.Many2one(
        comodel_name="membership.membership_category",
        related="membership_id.membership_category_id",
    )
    date_from = fields.Date(readonly=False)
    date_to = fields.Date(readonly=False)
    state = fields.Selection(compute="_compute_state", readonly=False)
    partner = fields.Many2one(ondelete="restrict")
    member_price = fields.Float(
        compute="_compute_member_price", readonly=False, store=True
    )

    _sql_constraints = [
        (
            "start_date_greater",
            "check(date_to >= date_from)",
            "Error ! Ending Date cannot be set before Beginning Date.",
        ),
    ]

    @api.constrains("date_from", "date_to")
    def _check_mandatory_dates(self):
        # This is a rather dirty mechanism to skip this check. It can be used
        # when creating a membership line and later writing date_from and
        # date_to to it in the same workflow. It is not used in this module an
        # sich.
        if self.env.context.get("skip_mandatory_dates"):
            return
        for line in self:
            if not line.date_from or not line.date_to:
                raise ValidationError(
                    _("Error: the start and end dates are mandatory.")
                )

    @api.depends("membership_id")
    def _compute_member_price(self):
        for partner in self:
            partner.member_price = partner.membership_id.list_price

    @api.onchange("date", "membership_id")
    def _onchange_membership_date(self):
        if self.date and self.membership_id:
            self.date_from = self.date
            next_date = self.membership_id._get_next_date(self.date)
            if next_date:
                date_to = next_date - timedelta(1)
                if date_to >= self.date:
                    self.date_to = date_to

    def _compute_state(self):
        no_invoice_lines = self.filtered(
            lambda line: isinstance(line.id, models.NewId)
            or not line.account_invoice_id
        )
        cancelled_lines = self.filtered(
            lambda line: line.account_invoice_id.state == "posted"
            and line.account_invoice_id.payment_state == "reversed"
        )
        cancelled_lines.state = "canceled"
        for line in no_invoice_lines:
            line.state = line.state or "none"
        return super(
            MembershipLine, self - no_invoice_lines - cancelled_lines
        )._compute_state()

    def unlink(self):
        allow = self.env.context.get("allow_membership_line_unlink", False)
        if self.filtered("account_invoice_id") and not allow:
            raise UserError(
                _(
                    "Can not remove membership line related to an "
                    "invoice. Please, cancel invoice or remove invoice "
                    "line instead"
                )
            )
        return super().unlink()  # pragma: no cover
