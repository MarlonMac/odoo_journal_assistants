# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AssistantJournalEntryBase(models.AbstractModel):
    """
    Modelo Abstracto que sirve como base para todos los asistentes de asientos de diario.
    """
    _name = 'assistant.journal.entry.base'
    _description = 'Asistente de Asientos de Diario (Base)'
    _order = 'date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Definimos el patrón de bloqueo de seguridad
    # Los campos serán de solo lectura en cualquier estado que no sea 'draft'
    READONLY_STATES = {
        'to_approve': [('readonly', True)], 
        'approved': [('readonly', True)], 
        'posted': [('readonly', True)], 
        'cancelled': [('readonly', True)]
    }

    # --- CAMPO DE ESTADO ---
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('to_approve', 'Para Aprobar'),
        ('approved', 'Aprobado'),
        ('posted', 'Registrado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', copy=False, tracking=True)

    # --- CAMPOS COMUNES ---
    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default=lambda self: _('Nuevo'))
    
    description = fields.Char(
        string='Descripción', 
        required=True, 
        states=READONLY_STATES, 
        tracking=True
    )
    
    date = fields.Date(
        string='Fecha Contable', 
        required=True, 
        default=fields.Date.context_today, 
        states=READONLY_STATES, 
        tracking=True
    )
    
    move_id = fields.Many2one('account.move', string='Asiento Contable', readonly=True, copy=False)
    
    company_id = fields.Many2one(
        'res.company', 
        string='Compañía', 
        required=True, 
        default=lambda self: self.env.company,
        states=READONLY_STATES
    )

    partner_id = fields.Many2one(
        'res.partner', 
        string='Contacto',
        states=READONLY_STATES
    )
    
    partner_bank_ids = fields.One2many(related='partner_id.bank_ids', string="Cuentas Bancarias del Contacto")

    # --- CAMPOS DE PAGO ---
    # El currency_id se hereda de company_id para asegurar que los pagos se registren en la moneda correcta
    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda', 
        related='company_id.currency_id', 
        store=True
    )   

    # --- MODIFICACIÓN: 'payment_ids' AHORA ES COMPUTADO ---
    # Debe ser computado para buscar los pagos usando la sintaxis del campo Reference.
    payment_ids = fields.One2many('account.payment', compute='_compute_payments', string='Pagos')
    
    # === FIX PARA MOSTRAR SALDOS EN LA VISTA SIN ALMACENARLOS ===
    amount_paid = fields.Monetary(string='Monto Pagado', compute='_compute_payment_amounts', store=False)
    amount_due = fields.Monetary(string='Saldo Pendiente', compute='_compute_payment_amounts', store=False)
    
    payment_status = fields.Selection([
        ('not_payable', 'No Aplica Pago'),
        ('unpaid', 'Pendiente de Pago'),
        ('partial', 'Parcialmente Pagado'),
        ('paid', 'Pagado'),
    ], string='Estado de Pago', compute='_compute_payment_status', store=True, default='not_payable')

    def _compute_payments(self):
        """ Encuentra los pagos asociados a este asistente. """
        for rec in self:
            rec.payment_ids = self.env['account.payment'].search([
                ('assistant_id', '=', f'{rec._name},{rec.id}')
            ])

    @api.depends('state', 'payment_ids.state', 'amount_due')
    def _compute_payment_status(self):
        for rec in self:
            is_payable_model = hasattr(rec, 'is_reimbursement') or hasattr(rec, 'is_pending_payment')
            is_payable_flag = False
            if hasattr(rec, 'is_reimbursement'):
                is_payable_flag = rec.is_reimbursement
            elif hasattr(rec, 'is_pending_payment'):
                is_payable_flag = rec.is_pending_payment

            if rec.state != 'posted':
                rec.payment_status = 'not_payable'
            elif not is_payable_model or not is_payable_flag:
                rec.payment_status = 'paid'
            else:
                amount_total = rec.amount if hasattr(rec, 'amount') else 0
                # Se añade chequeo de 'payment_ids' para el estado 'unpaid'
                if not rec.payment_ids and rec.amount_due == amount_total:
                    rec.payment_status = 'unpaid'
                elif rec.amount_due > 0:
                    rec.payment_status = 'partial'
                else:
                    rec.payment_status = 'paid'

    # El 'amount' total es necesario para calcular el saldo pendiente
    @api.depends('payment_ids.state', 'amount')
    def _compute_payment_amounts(self):
        for rec in self:
            # Esta lógica funcionará siempre que el modelo hijo tenga un campo llamado 'amount'
            amount_total = rec.amount if hasattr(rec, 'amount') else 0
            paid = sum(rec.payment_ids.filtered(lambda p: p.state == 'posted').mapped('amount'))
            rec.amount_paid = paid
            rec.amount_due = amount_total - paid

    def action_register_payment(self):
        self.ensure_one()
        return {
            'name': _('Registrar Pago'),
            'res_model': 'account.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.move_id.ids,
                # Esto permitirá que el pago se vincule automáticamente al asistente.
                'default_assistant_id': f'{self._name},{self.id}',
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.model
    def create(self, vals):
        # Usamos el _name del modelo hijo para buscar la secuencia correcta
        sequence_code = self._name
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code) or _('Nuevo')
        return super(AssistantJournalEntryBase, self).create(vals)

    # --- LÓGICA DE BOTONES (ACCIONES) ---
    def action_submit_for_approval(self):
        self.write({'state': 'to_approve'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        # Podríamos añadir un wizard para pedir el motivo del rechazo en el futuro
        self.write({'state': 'draft'})

    def action_post(self):
        # --- MODIFICACIÓN: Iterar con 'for rec in self' ---
        # (Tu código original usaba self.ensure_one(), pero iterar es más seguro)
        for rec in self: 
            # === APROBACIÓN: Ahora solo se postea desde Aprobado ===
            if rec.state != 'approved':
                raise UserError(_('Solo se pueden registrar documentos en estado Aprobado.'))

            move_vals = rec._prepare_move_vals()
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            
            # --- MODIFICACIÓN: Asignación correcta al campo Reference ---
            # En lugar de 'move.assistant_id = self', usamos la sintaxis 'modelo,id'
            move.assistant_id = f'{rec._name},{rec.id}'
            
            rec.write({'state': 'posted', 'move_id': move.id})
            rec.invalidate_recordset(['payment_status'])
        return True

    def action_cancel(self):
        for rec in self:
            if rec.move_id:
                if rec.move_id.state == 'posted':
                    rec.move_id._reverse_moves([{'date': fields.Date.today(), 'ref': _('Reversión de %s') % rec.name}])
                rec.move_id.button_cancel()
        return self.write({'state': 'cancelled'})

    def action_to_draft(self):
        if any(rec.state != 'cancelled' for rec in self):
             raise UserError(_('Solo los asientos cancelados pueden volver a borrador.'))
        # Eliminamos el asiento de reversión y el original para empezar de cero
        if self.move_id:
            self.move_id.line_ids.remove_move_reconcile()
            self.move_id.button_draft()
            self.move_id.with_context(force_delete=True).unlink()
        return self.write({'state': 'draft', 'move_id': False})

    # --- MÉTODOS A SER IMPLEMENTADOS POR LOS HIJOS ---
    def _prepare_move_vals(self):
        """
        Este método debe ser implementado por cada módulo asistente.
        Debe devolver un diccionario con los valores para crear el account.move.
        """
        self.ensure_one()
        return {
            'journal_id': self._get_journal().id,
            'date': self.date,
            'ref': self.description,
            'line_ids': self._prepare_move_lines(),
            'move_type': 'entry',
        }

    def _prepare_move_lines(self):
        """
        Este método debe ser implementado por cada módulo asistente.
        Debe devolver una lista de tuplas (0, 0, {...}) para las líneas del asiento.
        """
        raise NotImplementedError(_('El método _prepare_move_lines no ha sido implementado en el modelo hijo.'))

    def _get_journal(self):
        """
        Este método puede ser implementado por el hijo si necesita una lógica
        especial para determinar el diario a usar.
        """
        raise NotImplementedError(_('El método _get_journal no ha sido implementado en el modelo hijo.'))