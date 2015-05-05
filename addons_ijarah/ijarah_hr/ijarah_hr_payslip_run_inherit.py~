from openerp.osv import osv, fields
from datetime import datetime,time
from datetime import datetime
from dateutil import relativedelta
from lxml import etree    
import datetime
import time
import math
from openerp.tools.translate import _
from datetime import date, timedelta
from datetime import date
from openerp import netsvc
from openerp import tools
import openerp.addons.decimal_precision as dp
import time
from datetime import date
from datetime import datetime
from openerp.tools.safe_eval import safe_eval as eval
import re



class mail_compose_message(osv.TransientModel):
    
	_inherit = 'mail.compose.message'
	_log_access = True
	_description = 'Email composition wizard'
	_columns = {
	}
		
	def _get_partner_email_id(self,cr, uid, context=None):

		cr.execute("""SELECT id from res_partner where name in ('Saifulla Saheb')""")
		x = cr.fetchall()
		z1 = ', '.join(str(z) for z in x)  # Convert into String
		z2 = [int(s) for s in re.findall('\\d+',z1)]	# Convert into Ineteger
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(z2))	
		return z2
		
	def _get_doc_attach(self,cr, uid, context=None):

	        active_ids = context.get('active_ids')
		cr.execute("""SELECT attachment_id from excel_attachments_payslip_run where name = %s """,active_ids)
		a = cr.fetchone()
		return a
	
	_defaults = {
		'partner_ids':_get_partner_email_id,
		'attachment_ids':_get_doc_attach,
		
	}
	
class hr_payslip_run(osv.osv):

	def _get_journal_id(self,cr,uid,context=None):
		if context is None:
			context = {}
		res = self.pool.get('account.journal').search(cr,uid,[('name','=',' IJ/Salary Journal '),('code','=','IJ/SS')],)
		return res and res[0] or False

	def _check_uniq_name(self, cr, uid, ids, context=None):
		check_ids = self.search(cr, 1 ,[], context=context)
		lst = [x.name.lower() for x in self.browse(cr, uid, check_ids, context=context) if x.name and x.id not in ids]
		for self_obj in self.browse(cr, uid, ids, context=context):
			if self_obj.name and self_obj.name.lower() in  lst:
				return False
		return True
	_name = 'hr.payslip.run'
	_inherit = ['hr.payslip.run','mail.thread','ir.needaction_mixin']
	_columns = {
		'credit_account_id' : fields.many2one('account.account','Credit Account',domain="[('type','=','Test')]"),
		'employee_ids': fields.many2many('hr.employee', 'ijarah_hr_employee_rel', 'payslip_id', 'employee_id', 'Employees',domain="[('activate','=',True)]",),
		'ref_no':fields.char("Reference #",readonly=True),
		'account_type':fields.many2one("account.account.type","Account Type",domain="[('name','in',['Bank','Cash'])]"),
		'create_file_time':fields.char("Create Time"),
		'create_file_date':fields.date("Create Date"),
		'create_file_date_char':fields.char("Create Date Char"),  # Updating create_file_date value in create_file_date_char
		'desc':fields.char("Description"),
		'value_date':fields.date("Value Date"), # Validation Date
		'state': fields.selection([('draft', 'Draft'),('to_approve','Waiting for Approval'),('close', 'Close'),], 'Status', select=True, readonly=True),
		'excel_attach': fields.many2many('ir.attachment','excel_attachments_payslip_run','name', 'attachment_id', 'Attachments'),

	}

	_defaults = {
		'create_file_date':lambda *a: time.strftime('%Y-%m-%d'),
		'create_file_time':lambda *a: time.strftime('%H:%M:%S'),
		'desc':lambda *a: ('Salary Slip for %s') %(time.strftime('%m-%Y')),
		'create_file_date_char':lambda *a: time.strftime('%Y/%m/%d'),
	        'journal_id': _get_journal_id,
	} 

	_constraints = [(_check_uniq_name, 'Error: Name Duplication Error', ['name'])]

	
		
################################################### DELETE PAYSLIP Which Containing Payslip Run ID #####################################
	def delete_state(self, cr, uid, ids, context=None):
		payslip_id = self.pool.get('hr.payslip')
		for x in self.browse(cr, uid, ids, context=context):
		    #delete imported Data
		    old_payslip_id = payslip_id.search(cr, uid, [('payslip_run_id', '=', x.id)], context=context)
	#            old_sales_com_id
		    if old_payslip_id:
		        payslip_id.unlink(cr, uid, old_payslip_id, context=context)
		    else:
			return True
		#self.unlink(cr, uid, ids,context=None)
		return super(hr_payslip_run, self).unlink(cr, uid, ids, context=context)
			
	def unlink(self, cr, uid, ids, context=None):
		self.delete_state(cr,uid,ids,context)
		payslip_run_id = self.pool.get('hr.payslip.run').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in payslip_run_id:
		    if x['state'] not in ('close'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Entries which are already Closed!'))
#		osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
#		return True
		return super(hr_payslip_run, self).unlink(cr, uid, ids, context=context)    		
    		
	
##################################################################### Excel Generate #####################################################################
	def compute_sheet(self, cr, uid, ids, context=None):
		emp_pool = self.pool.get('hr.employee')
		slip_pool = self.pool.get('hr.payslip')
		run_pool = self.pool.get('hr.payslip.run')
		slip_ids = []
		this = self.browse(cr,uid, ids[0], context=None)
		if context is None:
		    context = {}
		data = self.read(cr, uid, ids, context=context)[0]
		run_data = {}
		if context and context.get('active_id', False):
#		    run_data = run_pool.read(cr, uid, context['active_id'], ['date_start', 'date_end', 'credit_note','credit_account_id','journal_id'])
		    run_data = run_pool.read(cr, uid, context['active_id'], ['date_start', 'date_end', 'credit_note','journal_id'])
		from_date =  this.date_start
		to_date = this.date_end
		credit_note = this.credit_note
#		credit_account_id = this.credit_account_id.id
		journal_id =  this.journal_id.id
		
	     #   raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(this.name))
		if not this.employee_ids:
		    raise osv.except_osv(_("Warning!"), _("You must select employee(s) to generate payslip(s)."))
		for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
		    slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False, context=context)
		    res = {
		        'employee_id': emp.id,
		        'name': slip_data['value'].get('name', False),
		        'struct_id': slip_data['value'].get('struct_id', False),
		        'contract_id': slip_data['value'].get('contract_id', False),
#		        'payslip_run_id': context.get('active_id', False),
		        'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
		        'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
		        'date_from': from_date,
		        'date_to': to_date,
		        'credit_note': credit_note,
#		        'credit_pay':credit_account_id,
			'journal_id':journal_id,
			'payslip_run_id':ids[0],
#			'cost_center':emp.cost_center.id,		# Customize 
			'employee_name':emp.name_related,		# Customize
			'contract_structure': slip_data['value'].get('contract_structure',False),
#[(emp.cont_id.type_id.name) + '/' + (emp.cont_id.contract_type.name) + '/' (emp.cont_id.contract_detail.name)
#			'contract_structure':str(emp.cont_id.type_id.name)  + '/' + emp.cont_id.contract_type.name + emp.cont_id.contract_detail.name)
			}
		    slip_ids.append(slip_pool.create(cr, uid, res, context=context))
		slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
		#slip_pool.process_sheet(cr, uid, [351,352,253], context=context) # Processing the Sheet of Payroll Screen
#		self.write(cr, uid, ids, {'state':'to_approve','ref_no':ref_no_seq,'value_date':value_date}, context=context)
		self.write(cr, uid, ids, {'state':'to_approve'}, context=context)
		self.export_bank_statement_excel(cr,uid,ids,context)     # Generate Bank Statement
		cr.execute("""INSERT INTO ir_attachment(datas_fname,res_model,type,db_datas,name) 
			SELECT hr_payslip_run.file_name_excel,'hr_payslip_run','binary',hr_payslip_run.data_excel,hr_payslip_run.file_name_excel
			FROM hr_payslip_run WHERE hr_payslip_run.id = %s """,[ids[0]])		
		cr.execute("""SELECT max(id) from ir_attachment where res_model = 'hr_payslip_run'""")
		x = cr.fetchone()
		cr.execute("""INSERT INTO excel_attachments_payslip_run(name,attachment_id) values(%s,%s)""",[ids[0],x])					
                return True
		
##################################################################### CSV Generate #######################################################################
		
	def compute_sheet_1(self, cr, uid, ids, context=None):
	    	ref_no_seq = self.pool.get('ir.sequence').get(cr, uid, 'hr.payslip.run')
		value_date = time.strftime('%Y/%m/%d') #Validation Date			
		payslip_id = self.pool.get('hr.payslip')
		for x in self.browse(cr, uid, ids, context=context):
		    #Search Payslip Data

		    old_payslip_id = payslip_id.search(cr, uid, [('payslip_run_id', '=', x.id)], context=context)		    
		    le = len(old_payslip_id)
		    i = 0		
		    for i in range(le):
			
			if old_payslip_id[i] in old_payslip_id:
#				raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(old_payslip_id[i]))	 
		        	payslip_id.process_sheet(cr, uid, [old_payslip_id[i]], context=context)
			
			else:
				return True
    		self.write(cr, uid, ids, {'state':'close','ref_no':ref_no_seq,'value_date':value_date}, context=context)
		self.export_bank_statement_csv(cr,uid,ids,context)     # Generate Bank Statement in CSV
		return True
hr_payslip_run()	

