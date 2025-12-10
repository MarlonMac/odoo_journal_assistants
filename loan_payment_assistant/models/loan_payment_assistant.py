# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class LoanPaymentAssistant(models.Model):
    _name = 'loan.payment.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Pago de Préstamos'

    # Seguridad: Solo editable en borrador
    READONLY_STATES = {
        'to_approve': [('readonly', True)], 
        'approved': [('readonly', True)], 
        'posted': [('readonly', True)], 
        'cancelled': [('readonly', True)]
    }

    # Campos específicos
    loan_id = fields.Many2one(
        'loan.loan', 
        string='Préstamo a Pagar', 
        required=True,
        states=READONLY_STATES,
        domain="[('company_id', '=', company_id)]"
    )
    principal_amount = fields.Float(
        string='Monto de Capital', 
        required=True, 
        states=READONLY_STATES,
        tracking=True
    )
    interest_amount = fields.Float(
        string='Monto de Intereses', 
        required=True, 
        states=READONLY_STATES,
        tracking=True
    )
    payment_journal_id = fields.Many2one(
        'account.journal', 
        string='Pagado desde (Diario)', 
        required=True, 
        states=READONLY_STATES,
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]"
    )
    
    amount = fields.Float(string='Monto Total Pagado', compute='_compute_amount', store=True, readonly=True)

    # ELIMINADO: attachment y attachment_filename (heredados del base)

    @api.depends('principal_amount', 'interest_amount')
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.principal_amount + rec.interest_amount

    @api.constrains('principal_amount', 'loan_id')
    def _check_principal_amount(self):
        for rec in self:
            # Validamos solo si el préstamo está activo para permitir correcciones
            if rec.loan_id and rec.loan_id.state == 'active':
                # Usamos una pequeña tolerancia para flotantes
                if rec.principal_amount > (rec.loan_id.outstanding_balance + 0.01):
                    raise ValidationError(_(
                        "El monto de capital a pagar (%.2f) no puede ser mayor que el saldo pendiente del préstamo (%.2f)."
                    ) % (rec.principal_amount, rec.loan_id.outstanding_balance))
    
    # CONSTRAINT DE FECHAS
    @api.constrains('date', 'loan_id')
    def _check_payment_date(self):
        for rec in self:
            if rec.loan_id and rec.loan_id.date_start and rec.date:
                if rec.date < rec.loan_id.date_start:
                    raise ValidationError(_(
                        "Error de Coherencia Temporal:\n"
                        "La fecha del pago (%s) no puede ser anterior a la fecha de inicio del préstamo (%s)."
                    ) % (rec.date, rec.loan_id.date_start))

    def action_post(self):
        # El super() base ya maneja el guardado del attachment
        res = super(LoanPaymentAssistant, self).action_post()
        
        # Variable para el efecto visual
        rainbow_effect = False

        for rec in self:
            # ELIMINADO: Lógica manual de ir.attachment.create

            # ACTUALIZACIÓN DE SALDO Y ESTADO
            if rec.loan_id:
                new_balance = rec.loan_id.outstanding_balance - rec.principal_amount
                
                # Tolerancia para errores de redondeo (menos de 1 centavo se considera 0)
                if new_balance <= 0.01:
                    new_balance = 0.0
                    # CAMBIO DE ESTADO AUTOMÁTICO
                    rec.loan_id.write({
                        'outstanding_balance': new_balance,
                        'state': 'paid'
                    })
                    # GAMIFICACIÓN: ¡Préstamo Pagado!
                    rainbow_effect = {
                        'effect': {
                            'fadeout': 'slow',
                            'message': '¡Felicidades! El préstamo ha sido pagado totalmente.',
                            'img_url': '/web/static/img/smile.svg',
                            'type': 'rainbow_man',
                        }
                    }
                else:
                    rec.loan_id.write({'outstanding_balance': new_balance})

        # Si se completó un préstamo, retornamos el efecto para la UI
        if rainbow_effect:
            return rainbow_effect
        
        return res

    def action_cancel(self):
        # 1. Identificar registros confirmados antes de cancelar
        posted_records = self.filtered(lambda r: r.state == 'posted')
        
        # 2. Llamar al método padre
        res = super(LoanPaymentAssistant, self).action_cancel()
        
        # 3. Revertir saldo y estado
        for rec in posted_records:
            if rec.loan_id:
                new_balance = rec.loan_id.outstanding_balance + rec.principal_amount
                vals = {'outstanding_balance': new_balance}
                
                # Si el préstamo estaba pagado y ahora tiene deuda, lo reactivamos
                if rec.loan_id.state == 'paid' and new_balance > 0.01:
                    vals['state'] = 'active'
                    rec.loan_id.message_post(body=_("El préstamo se ha reactivado debido a la cancelación de un pago."))
                
                rec.loan_id.write(vals)
                
                rec.loan_id.message_post(body=_(
                    "El pago %s fue cancelado. Se restauró el saldo por un monto de %s."
                ) % (rec.name, rec.principal_amount))
        
        return res

    def _get_journal(self):
        self.ensure_one()
        return self.payment_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('El monto total pagado debe ser positivo.'))
        if self.principal_amount < 0 or self.interest_amount < 0:
            raise UserError(_('Los montos de capital e interés no pueden ser negativos.'))

        lines = []
        # Línea de Débito 1 (Capital)
        lines.append((0, 0, {
            'name': f"{self.description} - Capital",
            'account_id': self.loan_id.principal_account_id.id,
            'debit': self.principal_amount,
            'credit': 0.0,
            'partner_id': self.loan_id.partner_id.id,
        }))
        
        # Línea de Débito 2 (Intereses)
        if self.interest_amount > 0:
            lines.append((0, 0, {
                'name': f"{self.description} - Intereses",
                'account_id': self.loan_id.interest_account_id.id,
                'debit': self.interest_amount,
                'credit': 0.0,
                'partner_id': self.loan_id.partner_id.id,
            }))

        # Línea de Crédito (Banco)
        lines.append((0, 0, {
            'name': self.description,
            'account_id': self.payment_journal_id.default_account_id.id,
            'debit': 0.0,
            'credit': self.amount,
            'partner_id': self.loan_id.partner_id.id,
        }))

        return lines