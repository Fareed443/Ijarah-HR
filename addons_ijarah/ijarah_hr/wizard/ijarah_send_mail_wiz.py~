# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import fields,osv
import datetime
from openerp.tools.translate import _
import re

class ijarah_sales_com_import(osv.osv_memory):

	def _get_doc_attach(self,cr, uid, context=None):

		active_ids = context.get('active_ids')
		cr.execute("""SELECT attachment_id from excel_attachments_payslip_run where name = %s """,active_ids)
		a = cr.fetchone()
#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(active_ids))					
		return a

	_name='ijarah.send.mail.wiz'
	_columns = {       
		'emp_ids': fields.many2many('hr.employee','ijarah_employee_mail_message','wizard_id', 'employee_id', 'Employee Mail',domain="[('cont_id.type_id_char','=','Ijarah'),('work_email','!=','NULL')]"),
		'attach_ids': fields.many2many('ir.attachment','ijarah_salary_sheet_wiz','wizard_id', 'attachment_id', 'Attachments'),		
	}
	_defaults = {
		'attach_ids':_get_doc_attach,		
	}

		
	def ijarah_send_mail(self, cr, uid,ids,data,context=None):
	
		this = self.browse(cr,uid, ids[0], context=None)
		if not this.emp_ids: 

			raise osv.except_osv(_('Configuration Error!'),_('Please select an Employee'))
		
		cr.execute("""SELECT id from ir_mail_server WHERE smtp_user='hr_system' AND name='Ijarah Email Configuration' """)
		mail_id = cr.fetchone()
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(mail_id))							
		for wiz_obj in self.read(cr,uid,ids):
			if 'form' not in data:
				data['form'] = {}
			data['form']['emp_ids'] = wiz_obj['emp_ids']
			xx = data['form']['emp_ids']
			sub_obj = self.pool.get('hr.employee')
			ids = sub_obj.search(cr,uid,[('is_ijarah','=',True),('id','in',xx)])	
			res = sub_obj.read(cr, uid, ids,['work_email'],context)
			res = [(r['work_email']) for r in res ]							
			z = ""			
			for item in res:
				z = z+""+item+","

			#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(ids[0]))								
				
			mail_mail = self.pool.get('mail.mail')
			mail_ids = []
			try:
				#for val in sub_obj.browse(cr, uid, ids):			
					email_to = ''.join([str(i[0]) for i in z])
					print email_to
					print ids[0]
					email_from = 'hr_system@ijarah.sa'
	#				email_cc = ', '.join([str(i[0]) for i in x])
					subject = (" HR Salary Sheet: \n")
					body = ("")
					footer = _("Thanks & Regards \n")
					mail_ids.append(mail_mail.create(cr,uid,{'email_to':email_to,'email_from':email_from,'subject':subject,'mail_server_id':mail_id,
	'body_html':'<pre><span class="inner-pre" style="font-size":80px">%s<br>%s</span></pre>' %(body,footer)},context=context))
					cr.execute("""SELECT MAX(mail_message_id) from mail_mail""") # GEt LAST Message id from mail_message
					x = cr.fetchone()					

					cr.execute("""SELECT attachment_id from ijarah_salary_sheet_wiz where wizard_id = %s """,[this.id])
					a = cr.fetchone()
					
					cr.execute("""INSERT INTO message_attachment_rel (message_id,attachment_id) VALUES (%s,%s)""",(x,a))
					mail_mail.send(cr,uid,mail_ids,context=context)
			except Exception , e:
				print "Exception",e
			
		return None					
			
#			
			#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(z))					
			#print c
#			cr.execute("SELECT work_email from hr_employee WHERE is_ijarah=TRUE AND id IN %s",[(39721)])
#			email_id = cr.fetchall()
			#xxx = ', '.join([str(i[0]) for i in x])			            
#			raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
#			raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(email_id))
	
ijarah_sales_com_import()

