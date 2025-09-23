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

    # --- CAMPOS COMUNES ---
    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default=lambda self: _('Nuevo'))
    description = fields.Char(string='Descripción', required=True, states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]}, tracking=True)
    date = fields.Date(string='Fecha Contable', required=True, default=fields.Date.context_today, states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]}, tracking=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('posted', 'Registrado'),
        ('cancelled', 'Cancelado'),
    ], string='Estado', default='draft', copy=False, tracking=True)
    move_id = fields.Many2one('account.move', string='Asiento Contable', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Compañía', required=True, default=lambda self: self.env.company)

    # --- LÓGICA DE SECUENCIA ---
    @api.model
    def create(self, vals):
        # Usamos el _name del modelo hijo para buscar la secuencia correcta
        sequence_code = self._name
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code) or _('Nuevo')
        return super(AssistantJournalEntryBase, self).create(vals)

    # --- LÓGICA DE BOTONES (ACCIONES) ---
    def action_post(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Solo se pueden registrar documentos en estado borrador.'))

        # Llamada al método que deben implementar los hijos
        move_vals = self._prepare_move_vals()

        move = self.env['account.move'].create(move_vals)
        move.action_post()
        
        return self.write({
            'state': 'posted',
            'move_id': move.id,
        })

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