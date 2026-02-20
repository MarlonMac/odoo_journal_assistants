# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ExpenseAssistant(models.Model):
    _name = 'expense.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Gastos Corporativos'

    READONLY_STATES = {
        'to_approve': [('readonly', True)], 
        'approved': [('readonly', True)], 
        'posted': [('readonly', True)], 
        'cancelled': [('readonly', True)]
    }

    # --- CAMPOS PARA ABSORCIÓN DE SALDOS ---
    document_total = fields.Monetary(
        string='Total del Documento Físico',
        states=READONLY_STATES,
        tracking=True,
        help="Monto total impreso en la factura. Si incluye saldos de meses anteriores, use la pestaña de 'Saldos Absorbidos'."
    )
    
    absorbed_expense_ids = fields.Many2many(
        'expense.assistant',
        'expense_assistant_absorbed_rel',
        'expense_id',
        'absorbed_id',
        string='Saldos Anteriores a Absorber',
        domain="[('partner_id', '=', partner_id), ('state', '=', 'posted'), ('payment_status', 'in', ['unpaid', 'partial']), ('id', '!=', id), ('is_reimbursement', '=', True)]",
        states=READONLY_STATES,
        help="Seleccione facturas/gastos anteriores que vienen cobrados y serán cancelados por este nuevo documento."
    )
    
    absorbed_total = fields.Monetary(
        string='Total Absorbido',
        compute='_compute_absorbed_total',
        currency_field='currency_id'
    )

    # --- REDECLARACIÓN PARA CORREGIR WARNINGS (SUDO Y RECURSIVIDAD) ---
    amount_paid = fields.Monetary(
        string='Monto Pagado', 
        compute='_compute_payment_amounts', 
        store=False,
        compute_sudo=True
    )
    
    amount_due = fields.Monetary(
        string='Saldo Pendiente', 
        compute='_compute_payment_amounts', 
        store=False,
        recursive=True,
        compute_sudo=True
    )

    payment_notification_sent = fields.Boolean(
        string='Notificación de Pago Enviada',
        compute='_compute_payment_amounts',
        store=True,
        copy=False,
        compute_sudo=True,
        help="Semáforo técnico para evitar envío duplicado de notificaciones."
    )

    # --- CAMPOS ESPECÍFICOS DE GASTOS (Originales) ---
    amount = fields.Monetary(
        string='Gasto Real del Periodo', 
        required=True, 
        states=READONLY_STATES, 
        tracking=True,
        currency_field='currency_id'
    )
    due_date = fields.Date(string='Fecha de Vencimiento', states=READONLY_STATES)
    payment_method = fields.Selection(
        [('cash', 'Efectivo'), ('credit_card', 'Tarjeta de Crédito'), ('debit_card', 'Tarjeta de Débito'), ('transfer', 'Transferencia'), ('other', 'Otro')], 
        string='Método de Pago Original', tracking=True, states=READONLY_STATES
    )
    is_reimbursement = fields.Boolean(string='Es Cuenta por Pagar / Reembolso', default=False, states=READONLY_STATES)
    reimburse_partner_id = fields.Many2one('res.partner', string='Pagar A', states=READONLY_STATES)
    payable_account_id = fields.Many2one(
        'account.account', string='Cuenta por Pagar', 
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", states=READONLY_STATES
    )
    responsible_employee_ids = fields.Many2many('hr.employee', string='Empleados Responsables', states=READONLY_STATES)
    category_id = fields.Many2one('expense.category', string='Categoría de Gasto', required=True, states=READONLY_STATES, domain="[('company_id', '=', company_id)]")
    expense_account_id = fields.Many2one('account.account', string='Cuenta de Gasto', related='category_id.expense_account_id', store=True, readonly=True)
    payment_journal_id = fields.Many2one('account.journal', string='Diario de Pago', domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]", states=READONLY_STATES)
    partner_id = fields.Many2one('res.partner', string='Proveedor/Contacto Original', states=READONLY_STATES)
    
    document_type = fields.Selection([
        ('invoice', 'Factura'), ('receipt', 'Recibo/Comprobante'), ('forecast', 'Gasto Previsto (Borrador)')
    ], string='Tipo de Documento', required=True, default='receipt', tracking=True, states=READONLY_STATES)
    
    dte_number = fields.Char(string='Número DTE', tracking=True, states=READONLY_STATES)
    dte_series = fields.Char(string='Serie DTE', tracking=True, states=READONLY_STATES)
    dte_authorization = fields.Char(string='Autorización DTE', tracking=True, states=READONLY_STATES)
    document_number = fields.Char(string='Número de Documento', tracking=True, states=READONLY_STATES)

    payment_status = fields.Selection([
        ('not_payable', 'No Aplica Pago'),
        ('unpaid', 'Pendiente de Pago'),
        ('partial', 'Parcialmente Pagado'),
        ('paid', 'Pagado'),
    ], string='Estado de Pago', compute='_compute_payment_status', store=True, default='not_payable')

    @api.depends('absorbed_expense_ids.amount_due')
    def _compute_absorbed_total(self):
        for rec in self:
            rec.absorbed_total = sum(rec.absorbed_expense_ids.mapped('amount_due'))

    # --- UX: AUTOCOMPLETADO INTELIGENTE DE MONTOS ---
    @api.onchange('document_total', 'absorbed_expense_ids')
    def _onchange_document_total(self):
        if self.document_total > 0:
            self.amount = self.document_total - self.absorbed_total

    @api.onchange('amount')
    def _onchange_amount(self):
        if self.amount > 0 and self.document_total == 0:
            self.document_total = self.amount + self.absorbed_total

    # --- SOBRESCRITURA DEL CÁLCULO DE PAGOS Y NOTIFICACIONES ---
    @api.depends('amount', 'absorbed_expense_ids.amount_due', 'move_id.line_ids.amount_residual', 'move_id.line_ids.reconciled', 'is_reimbursement', 'state')
    def _compute_payment_amounts(self):
        super(ExpenseAssistant, self)._compute_payment_amounts()
        for rec in self:
            current_notification_status = rec.payment_notification_sent
            rec.payment_notification_sent = current_notification_status
            
            if rec.state == 'posted' and rec.move_id:
                if rec.is_reimbursement:
                    total_liability = rec.amount + rec.absorbed_total
                    payable_lines = rec.move_id.line_ids.filtered(
                        lambda l: l.account_id == rec.payable_account_id and l.credit > 0
                    )
                    if payable_lines:
                        if rec.currency_id != rec.company_currency_id:
                            due = abs(sum(payable_lines.mapped('amount_residual_currency')))
                        else:
                            due = abs(sum(payable_lines.mapped('amount_residual')))
                        rec.amount_due = due
                        rec.amount_paid = total_liability - due

                    if rec.amount_due <= 0 and rec.amount_paid > 0 and not current_notification_status:
                        rec.payment_notification_sent = True
                        rec._send_paid_notification()
                else:
                    rec.amount_due = 0.0
                    rec.amount_paid = rec.amount

    @api.depends('state', 'amount_due', 'amount_paid', 'move_id.line_ids.amount_residual', 'move_id.line_ids.reconciled', 'is_reimbursement')
    def _compute_payment_status(self):
        super(ExpenseAssistant, self)._compute_payment_status()
        for rec in self:
            if rec.state == 'posted' and rec.move_id:
                if rec.is_reimbursement:
                    if rec.amount_due <= 0 and rec.amount_paid > 0:
                        rec.payment_status = 'paid'
                    elif rec.amount_due > 0 and rec.amount_paid > 0:
                        rec.payment_status = 'partial'
                    else:
                        rec.payment_status = 'unpaid'
                else:
                    rec.payment_status = 'paid'

    def _send_paid_notification(self):
        for rec in self:
            creator = rec.create_uid.partner_id
            monto_str = f"{rec.currency_id.symbol} {rec.amount_paid}"
            
            body = f"""
                <div style="margin: 0px; padding: 0px;">
                    <p style="margin: 0px; font-size: 13px;">
                        ¡Hola <a href="#" data-oe-model="res.partner" data-oe-id="{creator.id}">@{creator.name}</a>! 👋<br/><br/>
                        Te notificamos que el área encargada ha realizado el pago total de este gasto por <b>{monto_str}</b>.<br/>
                        El estado del registro se ha actualizado a <b>Pagado</b>. ✅
                    </p>
                </div>
            """
            rec.sudo().message_post(
                body=body,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[creator.id]
            )

    @api.constrains('is_reimbursement', 'reimburse_partner_id', 'payable_account_id', 'payment_journal_id')
    def _check_reimbursement_fields(self):
        for rec in self:
            if rec.is_reimbursement:
                if not rec.reimburse_partner_id or not rec.payable_account_id:
                    raise ValidationError(_('Para una cuenta por pagar, debe especificar a quién pagar y la cuenta por pagar.'))
            else:
                if not rec.payment_journal_id:
                    raise ValidationError(_('Para un pago directo, debe especificar el diario de pago.'))

    @api.constrains('state', 'document_type', 'dte_number', 'dte_series', 'dte_authorization', 'document_number')
    def _check_document_requirements(self):
        for rec in self:
            if rec.state in ['to_approve', 'approved', 'posted'] and rec.document_type == 'forecast':
                raise ValidationError(_('No se puede enviar a aprobación un "Gasto Previsto".'))
            if rec.state in ['to_approve', 'approved', 'posted'] and rec.document_type == 'invoice':
                if not rec.dte_number or not rec.dte_series or not rec.dte_authorization:
                    raise ValidationError(_('Faltan datos DTE obligatorios para la Factura.'))
            if rec.state in ['to_approve', 'approved', 'posted'] and rec.document_type == 'receipt':
                if not rec.document_number:
                    raise ValidationError(_('Falta el Número de Documento.'))

    def _get_journal(self):
        self.ensure_one()
        if self.is_reimbursement:
            journal = self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', self.company_id.id)], limit=1)
            if not journal:
                 raise UserError(_('No se encuentra un diario de "Operaciones Varias" para esta compañía.'))
            return journal
        return self.payment_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0 and not self.absorbed_expense_ids:
            raise UserError(_('El monto del gasto real debe ser positivo.'))

        if not self.message_attachment_count > 0 and not self.attachment:
            raise UserError(_('¡Adjunto Requerido! Debe adjuntar un documento de respaldo.'))

        ref_prefix = f"FAC {self.dte_series}-{self.dte_number}: " if self.document_type == 'invoice' else f"DOC {self.document_number}: " if self.document_type == 'receipt' else ""
        full_ref = f"{ref_prefix}{self.description}"

        company_currency = self.company_currency_id
        transaction_currency = self.currency_id
        lines = []

        expense_balance = transaction_currency._convert(self.amount, company_currency, self.company_id, self.date or fields.Date.today())
        if expense_balance > 0:
            debit_line_vals = {
                'name': full_ref,
                'account_id': self.expense_account_id.id,
                'debit': expense_balance,
                'credit': 0.0,
                'partner_id': self.partner_id.id,
            }
            if transaction_currency != company_currency:
                debit_line_vals.update({'currency_id': transaction_currency.id, 'amount_currency': self.amount})
            lines.append((0, 0, debit_line_vals))

        absorbed_balance = 0.0
        if self.absorbed_expense_ids and self.is_reimbursement:
            absorbed_balance = transaction_currency._convert(self.absorbed_total, company_currency, self.company_id, self.date or fields.Date.today())
            if absorbed_balance > 0:
                absorb_debit_vals = {
                    'name': f"{full_ref} (Absorción Saldos Anteriores)",
                    'account_id': self.payable_account_id.id,
                    'debit': absorbed_balance,
                    'credit': 0.0,
                    'partner_id': self.reimburse_partner_id.id,
                }
                if transaction_currency != company_currency:
                    absorb_debit_vals.update({'currency_id': transaction_currency.id, 'amount_currency': self.absorbed_total})
                lines.append((0, 0, absorb_debit_vals))

        total_credit_balance = expense_balance + absorbed_balance
        total_credit_amount = self.amount + self.absorbed_total

        if self.is_reimbursement:
            credit_account_id = self.payable_account_id.id
            credit_partner_id = self.reimburse_partner_id.id
        else:
            credit_account_id = self.payment_journal_id.default_account_id.id
            credit_partner_id = self.partner_id.id
            
        credit_line_vals = {
            'name': full_ref,
            'account_id': credit_account_id,
            'debit': 0.0,
            'credit': total_credit_balance,
            'partner_id': credit_partner_id,
        }
        if transaction_currency != company_currency:
            credit_line_vals.update({'currency_id': transaction_currency.id, 'amount_currency': -total_credit_amount})
        lines.append((0, 0, credit_line_vals))

        return lines

    def action_post(self):
        for rec in self:
            if rec.document_total == 0 and rec.amount > 0:
                rec.document_total = rec.amount + rec.absorbed_total
                
        res = super(ExpenseAssistant, self).action_post()
        for rec in self:
            if rec.absorbed_expense_ids and rec.move_id and rec.is_reimbursement:
                absorb_line = rec.move_id.line_ids.filtered(lambda l: l.account_id == rec.payable_account_id and l.debit > 0)
                if absorb_line:
                    lines_to_reconcile = absorb_line
                    for absorbed_exp in rec.absorbed_expense_ids:
                        if absorbed_exp.move_id:
                            open_credit_lines = absorbed_exp.move_id.line_ids.filtered(
                                lambda l: l.account_id == rec.payable_account_id and l.credit > 0 and not l.reconciled
                            )
                            lines_to_reconcile |= open_credit_lines
                    if len(lines_to_reconcile) > 1:
                        lines_to_reconcile.reconcile()
                        
                rec.absorbed_expense_ids._compute_payment_amounts()
                rec.absorbed_expense_ids._compute_payment_status()
        return res