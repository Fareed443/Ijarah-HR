#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from datetime import date
from openerp.tools.translate import _
from osv import osv, fields


class hr_holidays(osv.osv):

    _name = 'hr.holidays.public'
    _description = 'Public Holidays'

    _columns = {
        'year': fields.char("calendar Year", required=True),
        'line_ids': fields.one2many('hr.holidays.public.line', 'holidays_id', 'Holiday Dates'),
        'line_ids2': fields.one2many('hr.rest.line', 'rest_id', 'Rest Days Dates'),

    }

    _rec_name = 'year'
    _order = "year"

    _sql_constraints = [
        ('year_unique', 'UNIQUE(year)', _('Duplicate year!')),
    ]

    def is_public_holiday(self, cr, uid, dt, context=None):

        ph_obj = self.pool.get('hr.holidays.public')
        ph_ids = ph_obj.search(cr, uid, [
            ('year', '=', dt.year),
        ],
            context=context)
        if len(ph_ids) == 0:
            return False

        for line in ph_obj.browse(cr, uid, ph_ids[0], context=context).line_ids:
            if date.strftime(dt, "%Y-%m-%d") >= line.date_from and date.strftime(dt, "%Y-%m-%d") <= line.date_to:
                return True

        return False

    def get_holidays_list(self, cr, uid, year, context=None):

        res = []
        ph_ids = self.search(cr, uid, [('year', '=', year)], context=context)
        if len(ph_ids) == 0:
            return res
        [res.append(l.date)
         for l in self.browse(cr, uid, ph_ids[0], context=context).line_ids]
        return res
    
    def get_rest_list(self, cr, uid, year, context=None):

        res = []
        ph_ids = self.search(cr, uid, [('year', '=', year)], context=context)
        if len(ph_ids) == 0:
            return res
        
        [res.append(l.name)
         for l in self.browse(cr, uid, ph_ids[0], context=context).line_ids2]
        return res    


class hr_holidays_line(osv.osv):

    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'date_from': fields.date('Start Date', required=True),
        'date_to': fields.date('End Date', required=True),
        'holidays_id': fields.many2one('hr.holidays.public', 'Holiday Calendar Year'),
        'variable': fields.boolean('Date may change'),
    }

    _order = "date_from, name desc"

hr_holidays_line()
    
class hr_rest_line(osv.osv):

    _name = 'hr.rest.line'
    _description = 'Rest Days Lines'

    _columns = {
        'name': fields.selection([('6','Sunday'),('0', 'Monday'),('1','Tuesday'),('2', 'Wednesday'),('3','Thursday'),('4', 'Friday'),('5','Saturday')], 'Days', required=True),
        'rest_id': fields.many2one('hr.holidays.public', 'Rest Calendar Year'),
    }

hr_rest_line()
