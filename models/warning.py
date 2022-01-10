# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions

WARNING_TYPES = [('warning','Attention'),('info','Information'),('error','Erreur')]


class warning(models.TransientModel):
    _name = 'warning'
    _description = 'warning'
    # _req_name = 'title'

    type_msg = fields.Selection(WARNING_TYPES, string='Type', readonly=True)
    title = fields.Char(string="Title", size=100, readonly=True)
    message_w = fields.Text(string="Message", readonly=True)
    motif_reject = fields.Text(string="Motif de rejet", required=True, default="")
    request_id = fields.Integer(string="Demande de vaccation")

    def _get_view_id(self):
        """Get the view id
        @return: view id, or False if no view found
        """
        res = self.env['ir.model.data'].get_object_reference('school_mgmt', 'warning_form')
        return res and res[1] or False

    @api.multi
    def message(self, ids):
        message = self.browse(ids)
        message_type = [t[1] for t in WARNING_TYPES if message.type_msg == t[0]][0]
        print '%s: %s' % (message_type, message.title)
        res = {
            'name': '%s: %s' % (message_type, message.title),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self._get_view_id(),
            'res_model': 'warning',
            'domain': [],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': message.id
        }
        return res

    @api.multi
    def warning(self, title, message):
        record = self.create({'title': title, 'message_w': message, 'type_msg': 'warning'})
        res = self.message(record.id)
        return res

    @api.multi
    def info(self, title, message, request_id):
        record = self.create({'title': title, 'message_w': message, 'type_msg': 'info', 'request_id': request_id})
        res = self.message(record.id)
        return res

    @api.multi
    def error(self, title, message):
        record = self.create({'title': title, 'message_w': message, 'type_msg': 'error'})
        res = self.message(record.id)
        return res

    @api.multi
    def action_confirm_reject(self):
        for rec in self:
            return self.env['vaccation.ask'].search([('id', '=', rec.request_id)]).write({'motif_reject': rec.motif_reject, 'state': 'reject'})





