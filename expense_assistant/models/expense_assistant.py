# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ExpenseAssistant(models.Model):
    _name = 'expense.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Gastos Corporativos'

    # --- CAMPOS ESPECÍFICOS DE GASTOS ---
    amount = fields.Float(string='Monto', required=True, states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]}, tracking=True)
    due_date = fields.Date(string='Fecha de Vencimiento', states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]}, help="Fecha límite para pagar la factura o recibo asociado.")
    payment_method = fields.Selection([('cash', 'Efectivo'), ('credit_card', 'Tarjeta de Crédito'), ('debit_card', 'Tarjeta de Débito'), ('transfer', 'Transferencia Bancaria'), ('other', 'Otro')], string='Método de Pago Original', tracking=True, states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]}, help="Método de pago utilizado originalmente para el gasto.")
    is_reimbursement = fields.Boolean(string='Es Cuenta por Pagar / Reembolso', default=False, help="Marque esta casilla si el gasto debe ser reembolsado o si es una factura que aún no ha sido pagada.")
    reimburse_partner_id = fields.Many2one('res.partner', string='Pagar A', help="El empleado o proveedor al que se le debe el dinero.")
    payable_account_id = fields.Many2one('account.account', string='Cuenta por Pagar', domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", help="Cuenta de pasivo que se usará para registrar la deuda.")
    responsible_employee_ids = fields.Many2many('hr.employee', string='Empleados Responsables')
    category_id = fields.Many2one('expense.category', string='Categoría de Gasto', required=True, states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]}, domain="[('company_id', '=', company_id)]")
    expense_account_id = fields.Many2one('account.account', string='Cuenta de Gasto', related='category_id.expense_account_id', store=True, readonly=True)
    payment_journal_id = fields.Many2one('account.journal', string='Diario de Pago (Empresa)', domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]", help="Diario de la empresa utilizado para realizar el pago directo.")
    partner_id = fields.Many2one('res.partner', string='Proveedor/Contacto Original', states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]})
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analítica / Sucursal', states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]})

    # --- VALIDACIONES ---
    @api.constrains('is_reimbursement', 'reimburse_partner_id', 'payable_account_id', 'payment_journal_id')
    def _check_reimbursement_fields(self):
        for rec in self:
            if rec.is_reimbursement:
                if not rec.reimburse_partner_id or not rec.payable_account_id:
                    raise ValidationError(_('Para una cuenta por pagar, debe especificar a quién pagar y la cuenta por pagar.'))
            else:
                if not rec.payment_journal_id:
                    raise ValidationError(_('Para un pago directo, debe especificar el diario de pago.'))

    # --- IMPLEMENTACIÓN DE MÉTODOS HEREDADOS ---
    def _get_journal(self):
        self.ensure_one()
        if self.is_reimbursement:
            # Para Cuentas por Pagar, usamos un diario de "Operaciones Varias"
            journal = self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', self.company_id.id)], limit=1)
            if not journal:
                 raise UserError(_('No se encuentra un diario de "Operaciones Varias" para esta compañía.'))
            return journal
        else:
            return self.payment_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('El monto del gasto debe ser positivo.'))
        if not self.message_attachment_count > 0:
            raise UserError(_('¡Adjunto Requerido! Debe adjuntar al menos un documento de respaldo.'))

        # Línea de Débito (El Gasto)
        debit_line_vals = (0, 0, {
            'name': self.description,
            'account_id': self.expense_account_id.id,
            'debit': self.amount,
            'credit': 0.0,
            'partner_id': self.partner_id.id,
            'analytic_account_id': self.analytic_account_id.id,
        })

        # Línea de Crédito (La Contrapartida)
        if self.is_reimbursement:
            credit_account_id = self.payable_account_id.id
            credit_partner_id = self.reimburse_partner_id.id
        else:
            credit_account_id = self.payment_journal_id.default_account_id.id
            credit_partner_id = self.partner_id.id
            
        credit_line_vals = (0, 0, {
            'name': self.description,
            'account_id': credit_account_id,
            'debit': 0.0,
            'credit': self.amount,
            'partner_id': credit_partner_id,
        })

        return [debit_line_vals, credit_line_vals]