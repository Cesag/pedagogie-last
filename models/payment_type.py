# -*- coding: utf-8 -*-

from openerp import fields, models, api


class CesagOtherPayment(models.TransientModel):
    _name = 'cesag.other.payment'
    _description = 'Autres type de paiement'

    # name = fields.Char()

    proforma_invoice = fields.Boolean(string=u"Premier Paiement ?")
    type_payment_id = fields.Many2one(comodel_name='cesag.payment.type', string=u"Type de paiement")
    payment_date = fields.Date(string=u"Date", required=True)
    payment_amount = fields.Float(string=u"Montant", required=True)
    payment_bank_id = fields.Many2one(string=u"Banque", comodel_name='res.partner.bank', required=True)
    payment_note = fields.Text(string=u"Commentaire")
    attachment_ids = fields.Many2many('ir.attachment', 'doc_warning_rel', 'doc_id', 'attach_id4',
                                      string="Pieces jointes")


class CesagPaymentType(models.Model):
    _name = 'cesag.payment.type'

    name = fields.Char(string=u"Type de paiement")

    


# class CesagGestionFinanceOtherTypePayment(models.Model):
#     _name = 'cesag.manage.other.payment'
#     _description = 'Gestion des autres paiement'
#     _rec_name = "number"
#
#     _description = u'Paiement Facture Proforma'
#
#     number = fields.Char(u'Num', readonly=True)
#     payment_date = fields.Date(u'Date Soumission', required=True, readonly=True)
#     payment_receipt_date = fields.Date(u'Date Paiement', required=False, readonly=True)
#     payment_amount = fields.Float(u'Montant Paiement', required=True)
#     payment_bank_id = fields.Many2one('res.partner.bank', u'Banque')
#     payment_note = fields.Text(u'Commentaire Paiement', readonly=True)
#     payment_attachment_ids = fields.Many2many('ir.attachment', 'sm_admission_invoice_payment_attachment_rel', 'doc_id',
#                                               'attachment_id', string=u"Pièces Jointes", required=True, readonly=True)
#     payment_derogation_date = fields.Date(u'Date Dérogation', required=True, default=lambda self: fields.Date.today(),
#                                           readonly=True)
#     payment_derogation_note = fields.Text(u'Commentaire Dérogation', readonly=True)
#     payment_derogation_attachment_ids = fields.Many2many('ir.attachment',
#                                                          'sm_admission_derogation_invoice_payment_attachment_rel',
#                                                          'doc_id', 'attachment_id', string=u"Pièces Jointes",
#                                                          required=True, readonly=True)
#     accouting_validation = fields.Selection(
#         [('draft', u'À Valider'), ('ok', u'Validé'), ('nok', u'Rejeté'), ('done', u'Comptabilisé')], u'Validation',
#         default='draft', readonly=True)
#     proforma_invoice = fields.Boolean(u'Premier Paiement', readonly=True)
#     payment_derogation = fields.Boolean(u'Dérogation')
#     created_backend = fields.Boolean(u'Création Backend')
#     admission_id = fields.Many2one('sm.admission', string=u'Dossier', required=False, readonly=True)
#     enrollment_id = fields.Many2one('sm.enrollment', string=u'Réinscription', required=False, readonly=True)
#     invoice_id = fields.Many2one('account.invoice', u'Facture', readonly=True, compute="_compute_invoice_id",
#                                  store=True)
#     invoice_amount_total = fields.Float(u'Montant Facture', compute="_compute_invoice_total", store=False)
#     name = fields.Char(string=u"Nom & Prénom", compute="_compute_data", store=True)
#     program_id = fields.Many2one('sm.program', string=u"Programme", compute="_compute_data", store=True)
#     process_user_id = fields.Many2one('res.users', u'Traité par', readonly=True)
#     process_date = fields.Datetime(u'Traité le', readonly=True)
#     reference = fields.Char(u'Reference')
#     motif_refus = fields.Text(u'Motif')
#     payment_nature = fields.Selection([
#         ('admission', u'Préinscription'),
#         ('enrollment', u'Réinscription'),
#     ], string=u'Nature', default='admission', required=True)
#     payment_type = fields.Selection([
#         ('payment', u'Paiement'),
#         ('prise_charge', u'Prise Charge'),
#     ], string=u'Type', default='payment', required=True)
#
#     @api.model
#     def create(self, vals):
#         obj = super(SmAdmissionProformaInvoiceDetails, self).create(vals)
#         obj.write({'number': "P-%05d" % obj.id})
#         if obj.payment_attachment_ids:
#             obj.payment_attachment_ids.write({'res_id': obj.id, 'res_model': 'sm.admission.proforma.invoice.details'})
#
#     @api.multi
#     def write(self, vals):
#         res = super(SmAdmissionProformaInvoiceDetails, self).write(vals)
#         if 'payment_derogation_attachment_ids' in vals:
#             self.payment_derogation_attachment_ids.write(
#                 {'res_id': self.id, 'res_model': 'sm.admission.proforma.invoice.details'})
#         return res
#
#     @api.one
#     @api.depends("admission_id", "enrollment_id")
#     def _compute_data(self):
#         if self.payment_nature == 'admission':
#             self.name = self.admission_id.name
#             self.program_id = self.admission_id.school_program_id.id
#             self.invoice_id = self.admission_id.invoice_id and self.admission_id.invoice_id.id or False
#         elif self.payment_nature == 'enrollment':
#             self.name = self.enrollment_id.student_id.name
#             self.program_id = self.enrollment_id.program_id.id
#             self.invoice_id = self.enrollment_id.invoice_id and self.enrollment_id.invoice_id.id or False
#
#     @api.depends("admission_id", "admission_id.invoice_id", "enrollment_id", "enrollment_id.invoice_id")
#     def _compute_invoice_id(self):
#         for obj in self:
#             if obj.payment_nature == 'admission':
#                 obj.invoice_id = obj.admission_id.invoice_id and obj.admission_id.invoice_id.id or False
#             elif obj.payment_nature == 'enrollment':
#                 obj.invoice_id = obj.enrollment_id.invoice_id and obj.enrollment_id.invoice_id.id or False
#
#     def _compute_invoice_total(self):
#         for obj in self:
#             if obj.payment_nature == 'admission':
#                 obj.invoice_amount_total = obj.admission_id.invoice_id and obj.admission_id.invoice_id.amount_total or 0.00
#             elif obj.payment_nature == 'enrollment':
#                 obj.invoice_amount_total = obj.enrollment_id.invoice_id and obj.enrollment_id.invoice_id.amount_total or 0.00
#
#     @api.multi
#     def send_proforma_payment_ok_email(self):
#         user = self.env.user
#         template = self.sudo().env.ref('school_mgmt.portal_sm_admission_proforma_payment_ok')
#         ctx = self.env.context.copy()
#         res = template.with_context(ctx).send_mail(self.id)
#         return res
#
#     @api.multi
#     def send_proforma_payment_nok_email(self):
#         user = self.env.user
#         template = self.sudo().env.ref('school_mgmt.portal_sm_admission_proforma_payment_nok')
#         ctx = self.env.context.copy()
#         ctx.update({
#             'motif_refus': self.motif_refus,
#         })
#         res = template.with_context(ctx).send_mail(self.id)
#         return res
#
#     @api.multi
#     def action_accounting_ok(self):
#         if not self.reference:
#             raise Warning(_("Veuillez Remplir La Réference !"))
#         self.write(
#             {'accouting_validation': 'ok', 'process_user_id': self.env.user.id, 'process_date': fields.datetime.now()})
#         if self.payment_nature == 'admission':
#             self.admission_id.write({'payment_state': 'proforma_done'})
#         elif self.payment_nature == 'enrollment':
#             self.enrollment_id.write({'payment_state': 'proforma_done'})
#         self.send_proforma_payment_ok_email()
#         return True
#
#     @api.multi
#     def action_accounting_nok(self):
#         action = self.env.ref('school_mgmt.sm_admission_proforma_invoice_reject_action').read()[0]
#         return action
#
#     @api.multi
#     def action_accounting_done(self):
#         journal_id = False
#         if self.payment_amount <= 0:
#             raise Warning(_("Veuillez Remplir le Montant de Paiement !"))
#         if self.payment_bank_id:
#             journal_obj = self.env['account.journal'].search([('company_bank_id', '=', self.payment_bank_id.id)])
#             journal_id = journal_obj and journal_obj[0] and journal_obj[0].id or False
#         if self.payment_nature == 'admission':
#             if not self.admission_id.invoice_id:
#                 raise Warning(
#                     _("Aucune Facture Trouvé, La scolarité doit Inscrire l'étudiant pour générer la facture !"))
#             if self.admission_id.invoice_id.state == 'draft':
#                 raise Warning(_("Veuillez Valider La Facture"))
#             if self.admission_id.invoice_id.state in ('paid', 'cancel'):
#                 raise Warning(_("Facture dèjà Payé ou Annulé"))
#             res = self.admission_id.invoice_id.invoice_pay_customer()
#             res['context']['default_date'] = self.payment_receipt_date
#             res['context']['default_amount'] = self.payment_amount
#             res['context']['default_name'] = self.reference  # self.admission_id.invoice_id.number
#             res['context']['default_reference'] = "%s / %s" % (
#             self.admission_id.invoice_id.number, self.number)  # self.reference
#             res['context']['default_journal_id'] = journal_id
#             res['context']['default_payment_receipt_id'] = self.id
#             return res
#         elif self.payment_nature == 'enrollment':
#             if not self.admission_id.invoice_id:
#                 raise Warning(_("Aucune Facture Trouvé"))
#             if self.enrollment_id.invoice_id.state == 'draft':
#                 raise Warning(_("Veuillez Valider La Facture"))
#             if self.enrollment_id.invoice_id.state in ('paid', 'cancel'):
#                 raise Warning(_("Facture dèjà Payé ou Annulé"))
#             res = self.enrollment_id.invoice_id.invoice_pay_customer()
#             res['context']['default_date'] = self.payment_receipt_date
#             res['context']['default_amount'] = self.payment_amount
#             res['context']['default_name'] = self.reference  # self.enrollment_id.invoice_id.number
#             res['context']['default_reference'] = "%s / %s" % (
#             self.enrollment_id.invoice_id.number, self.number)  # self.reference
#             res['context']['default_journal_id'] = journal_id
#             res['context']['default_payment_receipt_id'] = self.id
#             return res
#         return True
#
#     @api.multi
#     def accounting_validation_nok(self):
#         self.write(
#             {'accouting_validation': 'nok', 'process_user_id': self.env.user.id, 'process_date': fields.datetime.now()})
#         self.send_proforma_payment_nok_email()
#         return True
#
#     @api.multi
#     def action_payment_derogation(self):
#         #        action = self.env.ref('school_mgmt.sm_admission_proforma_invoice_details_action').read()[0]
#         compose_form = self.env.ref('school_mgmt.sm_admission_proforma_invoice_details_form', False)
#         return {
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'sm.admission.proforma.invoice.details',
#             'views': [(compose_form.id, 'form')],
#             'view_id': compose_form.id,
#             'target': 'new',
#             'res_id': self.id,
#             'flags': {'initial_mode': 'edit'},
#         }
#         return action
#
#     @api.multi
#     def action_payment_derogation_validate(self):
#         if not self.payment_derogation_attachment_ids:
#             raise Warning(_("Veuillez Attacher les Pièces Jointes !"))
#         vals = {'payment_derogation': True}
#         self.write(vals)
#         return {'type': 'ir.actions.act_window_close'}




