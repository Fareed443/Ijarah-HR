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
from openerp.tools.safe_eval import safe_eval as eval
import re
import logging
_logger = logging.getLogger(__name__)
class res_bank(osv.osv):
	_name = 'res.bank'
	_inherit = 'res.bank'
	_columns = {
		'bank_clearing_code':fields.char("Bank Clearing Code")
	}
res_bank() 

class hr_employee(osv.osv):
	"""Employee Details """		
############################################### Check unique Employee No #######################################################
	def _check_emp_no(self, cr, uid, ids, context=None):

		this = self.browse(cr,uid, ids[0], context=None)
		company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'hr.employee', context)
		current_emp_no = this.ijarah_emp_no   # Current Employee NO
		obj = self.pool.get('hr.employee')
		ids = obj.search(cr,uid,[('cont_id', '!=', None),('id', '!=',ids[0]),('company_id', '=',company_id)])
		res = obj.read(cr, uid, ids,['ijarah_emp_no'],context)
		res = [(r['ijarah_emp_no']) for r in res ]
#		raise osv.except_osv(_('Warning!'), _('%s') % (res))
		if current_emp_no in res:
			return False
		if current_emp_no not in res:
			return True		

############################### Arabic Name Condition ########################################
	def _check_eng_name(self, cr, uid, ids, context=None):
		for employee in self.browse(cr, uid, ids, context=context):
			if employee.arabic_name:
				if (re.match('^[\w -]+$', employee.arabic_name) is not None):
					return False
		return True

	def onchange_partner_bank(self,cr,uid,ids,partner_bank,context=None):					
		value = {}
		this = self.pool.get('res.partner.bank').browse(cr, uid,partner_bank,context=context)		
		if partner_bank:
			iban = this.acc_number
			iban_replace = iban.replace(" ", "")				
			value ={'iban_no':iban_replace,'bank_bic':this.bank_bic}
			return {'value': value}                
		return True

			
	def write(self, cr, uid, ids, vals, context=None):						
		value = {}
		res={}						
		partner_bank = vals.get('partner_bank')
		#raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal  %s has not properly configured the Credit Account!')%(partner_bank))	
		this = self.pool.get('res.partner.bank').browse(cr, uid,partner_bank,context=context)				
		if vals.get('partner_bank'):
			iban = this.acc_number
			iban_replace = iban.replace(" ", "")				
			vals['iban_no'] = iban_replace # name.dbfieldname	
			vals['bank_bic'] = this.bank_bic 		
			res.update({'iban_no': iban_replace , 'emp_name': this.bank_bic})		
		result = super(hr_employee, self).write(cr, uid, ids, vals, context=context)	
		return result	
	
	_name = 'hr.employee'
	_inherit = 'hr.employee'
	_description = 'Employee Contract Details'
	_columns = {
                'arabic_name':fields.char("Arabic Name" ,size=256,required=True), 
                'ijarah_emp_no':fields.char("Employee No",size=64,readonly=True),  
		'religion':fields.char("Religion",size=64),
		'border_no':fields.char("Border No",size=64),
		'security_no':fields.char("Socail Security No",size=64),
		'visa_type': fields.selection([('Business', 'Business'),('Visit', 'Visit'),('Iqama', 'Iqama')], 'Visa Type'),
		'visa_det': fields.many2one("ijarah.visa.type",'Visa Detail',domain=[('name','=','Test')]),
		'visa_duration':fields.selection([('15 days', '15 days'),('30 days', '30 days'),('90 days', '90 days')], 'Visa Duration'),
		'entry_type':fields.char("Entry Type",size=64),
		'qualification':fields.char("Qualification",size=64),
		'deg':fields.char("Degree",size=64),
		'experience':fields.char("Experience",size=64),	
		'payment_type': fields.selection([('Bank', 'Bank')], 'Payment Type',required=True),
		'payment_by':fields.many2one('account.account','Account Number',domain=[('type','in',['liquidity','regular']),]),
		'activate':fields.boolean("Active"),
		'structure_id': fields.many2one('hr.payroll.structure', 'Salary Structure'),
		'cont_id': fields.many2one('hr.contract', 'Contract'),
		'emp_start_date':fields.date("Employee Start Date"),
		'emp_end_date':fields.date("Employee End Date"),
		'bank_clearing_code':fields.char("Bank Clearing Code"),
		'lines_iqama':fields.one2many('ijarah.hr.emp.iqama','iqama_ids',ondelete="cascade"),
		'doc_attach_ids': fields.many2many('ir.attachment','docs_ir_attachments_rel','employee_id', 'attachment_id', 'Certificate Attachments'),
		'state': fields.selection([('Draft', 'Draft'),('Active', 'Active'),('Termination','Termination'),('Resigned', 'Resigned')],'Status'),
		'partner_bank':fields.many2one("res.partner.bank",'Account Holder'),
		'iban_no':fields.char("IBAN No",readonly=True),
		'bank_bic':fields.char("Bank Identifier Code",size=8,readonly=True),
		'lines_certificate':fields.one2many('ijarah.hr.emp.certificate','certificate_ids',ondelete="cascade"),
		'is_ijarah':fields.boolean("Is Ijarah"),
        }
	_defaults = {
		'state'   : lambda * a: 'Draft',
		'payment_type':lambda * a: 'Bank',
	}
#	_sql_constraints = [
#        ('empname_uniq', 'unique(emp_no)', 'Employee Number must be unique!'),]

	_constraints = [(_check_eng_name, 'Error: Please Enter Valid Arabic Name', ['arabic_name']),
					(_check_emp_no, 'Error: Employee Number must be unique...', ['ijarah_emp_no'])]

	def onchange_partner_bank(self,cr,uid,ids,partner_bank,context=None):					
		value = {}
		this = self.pool.get('res.partner.bank').browse(cr, uid,partner_bank,context=context)		
		if partner_bank:
			iban = this.acc_number
			iban_replace = iban.replace(" ", "")				
			value ={'iban_no':iban_replace,'bank_bic':this.bank_bic}
			return {'value': value}                
		return True

	def unlink(self, cr, uid, ids, context=None):
		res = self.pool.get('hr.employee').read(cr, uid, ids, ['state'])
		unlink_ids = []
		for x in res:
		    if x['state'] in ('Draft'):
			unlink_ids.append(x['id'])
		    else:
			raise osv.except_osv(_('Invalid action !'), _('Cannot delete Employee(s) which are already in Active,Resigned,Termination State !'))
		#osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
		#return True
		return super(hr_employee, self).unlink(cr, uid, ids, context=context)
	def validate_state(self, cr, uid, ids,context=None):
		self.write(cr, uid, ids, {'state':'Active','activate':True}, context=context)
		return True

	
	def terminate_state(self, cr, uid, ids,context=None):
		this = self.browse(cr,uid, ids[0], context=None)
		cr.execute("""SELECT state from ijarah_hr_emp_equip where name = %s """,[ids[0]])
		x = cr.fetchone()	
#		raise osv.except_osv(_('Configuration Error!'),_('The Expense Journal "%s" has not properly configured the Debit Account!')%(x))
		if x:
			if x[0] == "Received":			
				self.write(cr, uid, ids, {'state':'Termination','activate':False}, context=context)
			else:			
				raise osv.except_osv(_('Configuration Error!'),_('Assets are Pending for this Employee'))
			
		else:
			self.write(cr, uid, ids, {'state':'Termination','activate':False}, context=context)
			return True


	def check_iqama_expiry(self, cr, uid,automatic=False,use_new_cursor=False,context=None):
		
		cr.execute("""SELECT id from ir_mail_server WHERE smtp_user='hr_system' AND name='Ijarah Email Configuration' """)
		mail_id = cr.fetchone()

		cr.execute("""Select hr_employee.name_related,hr_employee.ijarah_emp_no FROM hr_employee,ijarah_hr_emp_iqama
				WHERE ijarah_hr_emp_iqama.iqama_ids = hr_employee.id 
				AND ijarah_hr_emp_iqama.iqama_end_date between
				ijarah_hr_emp_iqama.iqama_end_date AND CURRENT_DATE + INTERVAL '2 months' """)
		x = cr.fetchall()
		employee_obj = self.pool.get('hr.employee')
		mail_mail = self.pool.get('mail.mail')
		mail_ids = []
		z1 = ', '.join(str(z) for z in x) # 
		if x:				
			try :	
				email_to = 'hr_system@ijarah.sa'
				name = "Faten"
				subject = "Iqama Expiry"
				body = _("Hello %s, \n" %(name))
				body += _("\t Please update the Iqama Expiry date of the below Employee's \n")
				body += _("\t %s \n " %(z1))
				footer = _("Kind Regards \n")
				footer += _("Human Resource Department")
				mail_ids.append(mail_mail.create(cr,uid,{'email_to':email_to,'subject':subject,'mail_server_id':mail_id,
				'body_html':'<pre><span class="inner-pre" style="font-size":40px">%s<br>%s</span></pre>' %(body,footer)},context=context))
				mail_mail.send(cr,uid,mail_ids,context=context)
			except Exception , e:
				print "Exception",e
		return None					

	def onchange_visa_type(self, cr, uid,ids,visa_type,context=None):
		values = {}
		
		if visa_type == None:
			return True
		if visa_type == 'Business':
			return	{'value':{'visa_det':[]},'domain':{'visa_det':[('name','in',['Single','Multiple'])]}}

		if visa_type == 'Visit':
			return	{'value':{'visa_det':[]},'domain':{'visa_det':[('name','in',['Single','Multiple'])]}}

		if visa_type == 'Iqama':
			return	{'value':{'visa_det':[]},'domain':{'visa_det':[('name','in',['Iqama Profession'])]}}				
		return True

	def onchange_dob(self, cr, uid,ids,birthday,context=None):
		value = {}
		now = datetime.datetime.now().strftime("%Y-%m-%d")
		if birthday >= now:
			return { 'Warning':{'title':'warning','message':'Date Should be greater less than Future & Today Date'},'value' :{'birthday': ''}}	          
		else :
			return True
		

	
hr_employee()

class ijarah_hr_emp_iqama(osv.osv):
        
	_name = "ijarah.hr.emp.iqama"
	_columns = {
		'iqama_ids' : fields.many2one("hr.employee","Employee ID",hidden=True,ondelete='cascade'),
		'doc_name':fields.char("Name"),	
		'iqama_start_date':fields.date("Start Date"),
		'iqama_end_date':fields.date("End Date"),
		'attachment_ids': fields.many2many('ir.attachment','iqama_ir_attachments_rel','iqama_ids', 'attachment_id', 'Attachments'),

	}                

	def onchange_iqama_end_date(self, cr, uid,ids,iqama_start_date,iqama_end_date,context=None):
		today_date = str(datetime.datetime.now())
		result = {'value': {}}
		if not iqama_start_date:
			return { 'warning':{'title':'warning','message':'Please Enter Iqama Start Date'},'value' :{'iqama_end_date':False,}}	
		if iqama_end_date < iqama_start_date:
			return { 'warning':{'title':'warning','message':'Please Enter Valid End Date'},'value' :{'iqama_end_date':False,}}	
		return True

ijarah_hr_emp_iqama()       
 
class ijarah_hr_emp_certificate(osv.osv):

	_name = "ijarah.hr.emp.certificate"
	_columns = {
		'certificate_ids' : fields.many2one("hr.employee","Employee ID",hidden=True,ondelete='cascade'),
		'name':fields.char("Document Name",required=True),
		'emp_certificate_ids': fields.many2many('ir.attachment','certificate_ir_attachments_rel','certificate_ids', 'attachment_id', 'Attachments'),

	}                

ijarah_hr_emp_certificate()       
 

