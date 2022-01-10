# -*- coding: utf-8 -*-

# See LICENSE file for full copyright and licensing details.


import base64
import re
import time
import itertools
import datetime
from lxml import etree
# 2 :  imports of openerp
import openerp
from openerp import api, fields, models,_
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class TimeTable(models.Model):
    """Defining model for time table."""

    _description = 'Time Table'
    _name = 'time.table'


    name = fields.Char('Description')
    
    standard_ids = fields.Many2one('cesag.allocation.enseignant', 'Classe',
                                  required=True,
                                  help="Select Standard")
    program_id = fields.Many2one('sm.program', string=u"Programme de Formation", required=True)
    level_id = fields.Many2one('sm.level', string=u"Niveau")
    year_id = fields.Many2one('sm.year', 'Année academique', 
                              help="Anné academique")
    semestre_id= fields.Many2one('sm.semester', 'Semestre', 
                              )
    timetable_ids = fields.One2many('time.table.line', 'table_id', 'TimeTable')
    timetable_type = fields.Selection([('regular', 'Cours')],
                                      'Type de planification', default="Cours",
                                      inivisible=True)
   
    class_room_id = fields.Many2one('sm.room', 'Salle de classe')

    
   
    
  
    
   

    
    @api.constrains('timetable_ids')
    def _check_lecture(self):
        '''Method to check same lecture is not assigned on same day.'''
        if self.timetable_type == 'regular':
            domain = [('table_id', 'in', self.ids)]
            line_ids = self.env['time.table.line'].search(domain)
            for rec in line_ids:
                records = [rec_check.id for rec_check in line_ids
                           if (rec.week_day == rec_check.week_day and
                               rec.start_time == rec_check.start_time and
                               rec.end_time == rec_check.end_time and
                               rec.teacher_id.id == rec.teacher_id.id)]
                if len(records) > 1:
                    raise ValidationError(_('''Vous ne pouvez pas choisir le même cours %s à la même heure \
 %s  au même jour %s pour le même professeur \
%s..!''') % (rec.subject_ids,rec.start_time,rec.week_day,rec.teacher_id.name))
           

class TimeTableLine(models.Model):
    """Defining model for time table."""

    _description = 'Time Table Line'
    _name = 'time.table.line'
    _rec_name = 'table_id'

#     @api.constrains('teacher_id', 'subject_id')
#     def check_teacher(self):
#         '''Check if lecture is not related to teacher than raise error.'''
#         if (self.teacher_id.id not in self.subject_id.teacher_ids.ids and
#                 self.table_id.timetable_type == 'regular'):
#             raise ValidationError(_('''The subject %s is not assigned to \
# teacher %s.''') % (self.subject_id.name, self.teacher_id.name))

    teacher_id = fields.Many2one('sm.faculty', 'Professeur',
                                 )
    subject_ids = fields.Many2one('classroom.allocation.module', 'Modules',
                                 )
    table_id = fields.Many2one('time.table', 'TimeTable')
    start_time = fields.Float('Heure de Debut', required=True,
                              )
    end_time = fields.Float('heure de fin', required=True,
                            )
    week_day = fields.Selection([('lundi   ', 'Lundi'),
                                 ('mardi', 'Mardi'),
                                 ('mercredi', 'Mercredi'),
                                 ('jeudi', 'Jeudi'),
                                 ('vendredi', 'Vendredi'),
                                 ('samedi', 'Samedi'),
                                 ('dimanche', 'Sunday')], "Horaires",)
    class_room_id = fields.Many2one('sm.room', 'Salle de classe')
    
    
    @api.onchange("subject_ids")
    def module_inf(self):
        for rec in self:
            if rec.subject_ids:
                search_element = self.env['classroom.allocation.module']
                search_element = search_element.search([('id', '=', rec.subject_ids.id)])
                if search_element.id:
                    rec.teacher_id = search_element.teacher_id.id
    

    @api.constrains('teacher_id', 'class_room_id')
    def check_teacher_room(self):
        """Check available room for teacher."""
        timetable_rec = self.env['time.table'].search([('id', '!=',
                                                        self.table_id.id)])
        if timetable_rec:
            for data in timetable_rec:
                for record in data.timetable_ids:
                    if (data.timetable_type == 'regular' and
                            self.table_id.timetable_type == 'regular' and
                            self.teacher_id == record.teacher_id and
                            self.week_day == record.week_day and
                            self.start_time == record.start_time):
                        raise ValidationError(_('''On à le cours de \
qu même moment!'''))
                    if (data.timetable_type == 'regular' and
                            self.table_id.timetable_type == 'regular' and
                            self.class_room_id == record.class_room_id and
                            self.start_time == record.start_time):
                        raise ValidationError(_("La salle est deja occupée."))
                    if (data.timetable_type == 'regular' and
                            self.table_id.timetable_type == 'regular' and
                            self.class_room_id == record.class_room_id and
                            self.start_time == record.start_time and
                            self.week_day == record.week_day):
                        raise ValidationError(_("La salle est deja occupée."))
                        
                        
   
   


