# -*- coding: utf-8 -*-

from datetime import date, datetime
from openerp import models, fields, tools, api, _
import time
import openerp.addons.decimal_precision as dp
from time import gmtime, strftime
from openerp.exceptions import Warning, ValidationError
from openerp.tools.translate import _




class ExtendedTimeTable(models.Model):
    _inherit = 'time.table'

    # def unlink(self):
    #     exam = self.env['exam.exam']
    #     schedule_line = self.env['exam.schedule.line']
    #     for rec in self:
    #         exam_search = exam.search([('state', '=', 'running')])
    #         for data in exam_search:
    #             schedule_line_search = schedule_line.search([('exam_id', '=',
    #                                                           data.id),
    #                                                          ('timetable_id',
    #                                                           '=', rec.id)])
    #             if schedule_line_search:
    #                 raise ValidationError(_('''You cannot delete schedule of
    #                 exam which is in running!'''))
    #     return super(ExtendedTimeTable, self).unlink()

    timetable_type = fields.Selection(selection_add=[('exam', 'Examen')],
                                      string='type de Planification', required=True,
                                      inivisible=False)
    exam_timetable_line_ids = fields.One2many('time.table.line', 'table_id',
                                              'TimeTable Lines')
    exam_id = fields.Many2one('exam.exam', 'Exam')

    @api.constrains('exam_timetable_line_ids')
    def _check_exam(self):
        '''Method to check same exam is not assigned on same day.'''
        if self.timetable_type == 'exam':
            if not self.exam_timetable_line_ids:
                raise ValidationError(_(''' Please Enter Exam Timetable!'''))
            domain = [('table_id', 'in', self.ids)]
            line_ids = self.env['time.table.line'].search(domain)
            for rec in line_ids:
                records = [rec_check.id for rec_check in line_ids
                           if (rec.day_of_week == rec_check.day_of_week and
                               rec.start_time == rec_check.start_time and
                               rec.end_time == rec_check.end_time and
                               rec.teacher_id.id == rec.teacher_id.id and
                               rec.exm_date == rec.exm_date)]
                if len(records) > 1:
                    raise ValidationError(_('''You cannot set exam at same
                                            time %s  at same day %s for
                                            teacher %s!''') %
                                           (rec.start_time, rec.day_of_week,
                                            rec.teacher_id.name))


class ExtendedTimeTableLine(models.Model):
    _inherit = 'time.table.line'

    exm_date = fields.Date('Date')
    day_of_week = fields.Char('Jour')
    class_room_id = fields.Many2one('sm.room', 'Salle de classe')
    

    @api.multi
    @api.onchange('exm_date')
    def onchange_date_day(self):
        '''Method to get weekday from date'''
        for rec in self:
            rec.day_of_week = False
            if rec.exm_date:
                ex_dt = datetime.strptime(rec.exm_date, "%Y-%m-%d")
                rec.day_of_week = ex_dt.strftime("%A").lower()


    @api.multi
    def _check_date(self):
        '''Method to check constraint of start date and end date'''
        for line in self:
            if line.exm_date:
                dt = datetime.strptime(line.exm_date, "%Y-%m-%d")
                if line.week_day != dt.strptime("%A").lower():
                    return False
                elif dt.__str__() < datetime.strptime(date.today().__str__(),
                                                      "%Y-%m-%d").__str__():
                    raise ValidationError(_('''Invalid Date Error !\
                        Either you have selected wrong day\
for the date or you have selected invalid date!'''))

    # @api.constrains('teacher_id')
    # def check_supervisior_exam(self):
    #     """Method to check supervisor in exam."""
    #     for rec in self:
    #         if (rec.table_id.timetable_type == 'exam' and
    #                 not rec.teacher_id):
    #                 raise ValidationError(_('''PLease Enter Supervisior!'''))

    @api.constrains('start_time', 'end_time')
    def check_time(self):
        '''Method to check constraint of start time and end time.'''
        for rec in self:
            if rec.start_time >= rec.end_time:
                raise ValidationError(_('''Start time should be less than end \
time!'''))

    @api.constrains('teacher_id', 'class_room_id')
    def check_teacher_room(self):
        """Method to Check room."""
        timetable_rec = self.env['time.table'].search([('id', '!=',
                                                        self.table_id.id)])
        if timetable_rec:
            for data in timetable_rec:
                for record in data.timetable_ids:
                    if (data.timetable_type == 'exam' and
                            self.table_id.timetable_type == 'exam' and
                            self.class_room_id == record.class_room_id and
                            self.start_time == record.start_time):
                            raise ValidationError(_("The room is occupied!"))

    @api.constrains('subject_ids', 'class_room_id')
    def check_exam_date(self):
        """Method to Check Exam Date."""
        for rec in self.table_id.exam_timetable_line_ids:
            record = self.table_id
            if rec.id not in self.ids:
                if (record.timetable_type == 'exam' and
                        self.exm_date == rec.exm_date and
                        self.start_time == rec.start_time):
                    raise ValidationError(_('''There is already Exam at
                        same Date and Time!'''))
                if (record.timetable_type == 'exam' and
                        self.table_id.timetable_type == 'exam' and
                        self.subject_ids == rec.subject_ids):
                        raise ValidationError(_('''%s Subject Exam Already
                        Taken''') % (self.subject_id.name))
                if (record.timetable_type == 'exam' and
                        self.table_id.timetable_type == 'exam' and
                        self.exm_date == rec.exm_date and
                        self.class_room_id == rec.class_room_id and
                        self.start_time == rec.start_time):
                    raise ValidationError(_('''%s is occupied by '%s' for %s
                    class!''') % (self.class_room_id.name, record.name,
                                  record.standard_ids.name))

