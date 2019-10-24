import pandas as pd
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import datetime
from xml.dom import minidom
from xml.etree import ElementTree
from excelimport import ExcelImporter


class Buildetwork(object):

    def __init__(self):
        self.my_filetypes = [('Excel File', 'xlsx'), ('Excel file', 'xlx')]
        self.sheet_bridge_domain = 'bridge_domain'
        self.sheet_bd_subnet = 'bd_subnet'
        self.sheet_bd_l3out = 'bd_l3out'
        self.sheet_contract = 'contract'
        self.sheet_epg = 'end_point_group'
        self.sheet_epg_subnet = 'epg_subnet'
        self.sheet_epg_domain_ass = 'epg_domain_association'
        self.sheet_stat_bnd = 'epg_static_binding'
        self.sheet_app_prof = 'application_profile'

    
    def get_excel_file(self):
        self.xl_file = ExcelImporter().import_excelfile()
        return self.xl_file



    def create_bridge_domain(self,xl_file):
        # Bridge SpreadSheet
        excel_file = xl_file
        raw_bridge_domain_sheet = pd.read_excel(excel_file,sheet_name=self.sheet_bridge_domain)
        bridge_domain_sheet = raw_bridge_domain_sheet.sort_values(by=['tenant'])
        raw_bd_subnet_sheet = pd.read_excel(excel_file, sheet_name=self.sheet_bd_subnet)
        bd_subnet_sheet = raw_bd_subnet_sheet.sort_values(by=['tenant'])
        raw_bd_l3out_sheet = pd.read_excel(excel_file, sheet_name=self.sheet_bd_l3out)
        bd_l3out_sheet = raw_bd_l3out_sheet.sort_values(by=['tenant'])
        set_of_tenants = set()
        results = []

        for index, row in bridge_domain_sheet.iterrows():
            if pd.notnull(row['status']):
                continue
            else:
                set_of_tenants.add(row['tenant'])
        set_of_tenants = sorted(set_of_tenants)
        print(set_of_tenants)

        for tenant in set_of_tenants:
            root = Element('polUni')
            # root.set('version', '1.0')
            root.append(Comment('Generated by JTools UCI Builder'))
            self.fvTenant = SubElement(root, 'fvTenant', {'name': tenant, 'status': 'modified'})
            for index, row in bridge_domain_sheet.iterrows():
                if pd.notnull(row['status']):
                    continue
                else:
                    if row['tenant'] == tenant:
                        fvBD = SubElement(self.fvTenant, 'fvBD', {'arpFlood': 'yes','descr': row['description'],
                                                                  'ipLearning':'yes', 'limitIpLearnToSubnets':'yes',
                                                                  'mcastAllow':'no','multiDstPktAct':'bd-flood',
                                                                  'name':row['name'], 'status':'', 'type':'regular',
                                                                  'unicastRoute':'yes', 'unkMacUcastAct':'flood',
                                                                  'unkMcastAct':'flood'})
                        fvRsBDToNdP = SubElement(fvBD,'fvRsBDToNdP',{'tnNdIfPolName':''})
                        fvRsCtx = SubElement(fvBD,'fvRsCtx', {'tnFvCtxName':row['vrf']})
                        fvRsIgmpsn = SubElement(fvBD,'fvRsIgmpsn',{'tnIgmpSnoopPolName':''})
                        fvRsBdToEpRet = SubElement(fvBD,'fvRsBdToEpRet',{'resolveAct':'resolve',
                        'tnFvEpRetPolName':''})
                        for index, row_ip in bd_subnet_sheet.iterrows():
                            if (row_ip['bridge_domain'] == row['name']) and (row_ip['tenant'] == tenant):
                                fvSubnet = SubElement(fvBD, 'fvSubnet', {'ctrl': '','descr':row_ip['description'],
                                                                         'ip':row_ip['bd_subnet'],'preferred':'no',
                                                                         'scope':'public','virtual':'no'})
                        for index, row_l3 in bd_l3out_sheet.iterrows():
                            if (row_l3['bd_name'] == row['name']) and (row_ip['tenant'] == tenant):
                                fvRsBDToOut = SubElement(fvBD, 'fvRsBDToOut', {'tnL3extOutName':row_l3['l3out_name']})
            results.append(root)
        for result in results:
            print(ExcelImporter().prettify(result))
        return results

    def generate_xml_files(self):
        pass


    def create_contract(self,xl_file):
        # contract SpreadSheet
        excel_file = xl_file
        raw_contract_sheet = pd.read_excel(excel_file,sheet_name=self.sheet_contract)
        contract_sheet = raw_contract_sheet.sort_values(by=['tenant'])
        set_of_tenants = set()
        results = []

        for index, row in contract_sheet.iterrows():
            if pd.notnull(row['status']):
                continue
            else:
                set_of_tenants.add(row['tenant'])
        set_of_tenants = sorted(set_of_tenants)

        for tenant in set_of_tenants:
            root = Element('polUni')
            # root.set('version', '1.0')
            root.append(Comment('Generated by JTools UCI Builder'))
            self.fvTenant = SubElement(root, 'fvTenant', {'name': tenant, 'status': 'modified'})
            for index, row in contract_sheet.iterrows():
                if pd.notnull(row['status']):
                    continue
                else:
                    if row['tenant'] == tenant:
                        vzBrCP = SubElement(self.fvTenant, 'vzBrCP', {'descr': row['description'],
                                                                  'name':row['name'], 'nameAlias':'', 'prio':'unspecified',
                                                                  'scope':row['scope'], 'status':'',
                                                                  'targetDscp':'unspecified'})
            results.append(root)
        for result in results:
            print(ExcelImporter().prettify(result))
        return results


    def create_epg(self,xl_file):
        # Bridge SpreadSheet
        excel_file = xl_file
        raw_epg_sheet = pd.read_excel(excel_file,sheet_name=self.sheet_epg)
        epg_sheet = raw_epg_sheet.sort_values(by=['tenant', 'app_profile'])
        epg_subnet_sheet = pd.read_excel(excel_file, sheet_name=self.sheet_epg_subnet)
        raw_epg_domain_ass_sheet = pd.read_excel(excel_file, sheet_name=self.sheet_epg_domain_ass)
        epg_domain_ass_sheet = raw_epg_domain_ass_sheet.sort_values(by=['tenant', 'app_profile'])
        set_of_tenants = set()
        epg_dom_vmm = 'vmm_vmware'
        epg_dom_phy = 'physical'
        epg_dom = ''
        epg_vmm_tDn = ''
        epg_phy_tDN = ''
        results = []

        for index, row in epg_sheet.iterrows():
            if pd.notnull(row['status']):
                continue
            else:
                set_of_tenants.add(row['tenant'])
        set_of_tenants = sorted(set_of_tenants)

        for tenant in set_of_tenants:
            root = Element('polUni')
            # root.set('version', '1.0')
            root.append(Comment('Generated by JTools UCI Builder'))
            self.fvTenant = SubElement(root, 'fvTenant', {'name': tenant, 'status': 'modified'})
            set_of_AppProf = set() 
            for index, row in epg_sheet.iterrows():
                if row['tenant'] == tenant and pd.isnull(row['status']):
                    set_of_AppProf.add(row['app_profile'])
            set_of_AppProf = sorted(set_of_AppProf)
            for app_prof in set_of_AppProf:
                fvAp = SubElement(self.fvTenant,'fvAp',{'name': app_prof,'status':'modified'})
                for index, row_app in epg_sheet.iterrows():
                    if row_app['tenant'] == tenant and row_app['app_profile'] == app_prof:
                        fvAEPg = SubElement(fvAp,'fvAEPg',{'descr': row_app['description'],
                                                                  'floodOnEncap':'disabled', 'isAttrBasedEPg':'no',
                                                                  'matchT':'AtleastOne','name':row_app['name'], 'pcEnfPref':'unenforced', 'prefGrMemb':'exclude',
                                                                  'prio':'unspecified', 'status':''})
                        fvRsBd = SubElement(fvAEPg,'fvRsBd',{'tnFvBDName':row_app['bridge_domain']})
                        for index, row_ip in epg_subnet_sheet.iterrows():
                            if row_ip['epg'] == row_app['name'] and row_ip['tenant'] == row_app['tenant']:
                                fvSubnet = SubElement(fvAEPg,'fvSubnet',{'ctrl':'no-default-gateway','descr':row_ip['description'],
                                                                    'ip':row_ip['epg_subnet'],'preferred':'no','scope':row_ip['subnet_scope'],
                                                                    'virtual':'no'})
                        for index, row_domain in epg_domain_ass_sheet.iterrows():
                            epg_dom = row_domain['domainName']
                            if row_domain['epg_name'] == row_app['name'] and row_domain['tenant'] == row_app['tenant'] and row_domain['domainType'] == epg_dom_vmm:
                                epg_vmm_tDn = 'uni/vmmp-VMware/dom-' + epg_dom
                                fvRsDomAtt_vmm = SubElement(fvAEPg,'fvRsDomAtt',{'encap':'','encapMode':'auto','epgCos':'Cos0','epgCosPref':'disabled',
                                                                    'instrImedcy':'immediate','netflowDir':'both','netflowPref':'disabled',
                                                                    'primaryEncap':'unknown','primaryEncapInner':'unknown','resImedcy':'immediate',
                                                                    'secondaryEncapInner':'unknown','status':'','switchingMode':'native','tDn':epg_vmm_tDn})
                                vmmSecP = SubElement(fvRsDomAtt_vmm,'vmmSecP',{'allowPromiscuous':'reject','descr':'','forgedTransmits':'reject',
                                                                    'macChanges':'reject','name':''})
                            elif row_domain['epg_name'] == row_app['name'] and row_domain['tenant'] == row_app['tenant'] and row_domain['domainType'] == epg_dom_phy:
                                epg_phy_tDN = 'uni/phys-' + epg_dom
                                fvRsDomAtt_phy = SubElement(fvAEPg,'fvRsDomAtt',{'instrImedcy':'immediate','resImedcy':'immediate',
                                                                    'status':'','tDn':epg_phy_tDN})
            results.append(root)
            print(tenant,set_of_AppProf)
            set_of_AppProf.clear()
        for result in results:
            print(ExcelImporter().prettify(result))
        return results




    def create_epg_stat_bnd(self,xl_file):
        # Bridge SpreadSheet
        excel_file = xl_file
        raw_epg_stat_bnd_sheet = pd.read_excel(excel_file, sheet_name=self.sheet_stat_bnd)
        epg_stat_bnd_sheet = raw_epg_stat_bnd_sheet.sort_values(by=['tenant', 'app_profile'])
        set_of_tenants = set()
        epg_encap = ''
        epg_paths_tDN = ''
        epg_protpaths_tDN = ''
        results = []
        for index, row in epg_stat_bnd_sheet.iterrows():
            if pd.notnull(row['status']):
                continue
            else:
                set_of_tenants.add(row['tenant'])
        set_of_tenants = sorted(set_of_tenants)
        for tenant in set_of_tenants:
            root = Element('polUni')
            root.append(Comment('Generated by JTools UCI Builder'))
            self.fvTenant = SubElement(root,'fvTenant',{'name':tenant,'status':'modified'})
            set_of_AppProf = set() 
            for index, row in epg_stat_bnd_sheet.iterrows():
                if row['tenant'] == tenant and pd.isnull(row['status']):
                    set_of_AppProf.add(row['app_profile'])
            set_of_AppProf = sorted(set_of_AppProf)                   
            for app_prof in set_of_AppProf:
                fvAp = SubElement(self.fvTenant,'fvAp',{'name': app_prof,'status':'modified'})
                for index, row_app in epg_stat_bnd_sheet.iterrows():
                    if row_app['tenant'] == tenant and row_app['app_profile'] == app_prof:
                        fvAEPg = SubElement(fvAp,'fvAEPg',{'matchT':'AtleastOne','name':row_app['name'],'status':'modified'})
                        if pd.isnull(row_app['right_node_id']):    
                            epg_encap = 'vlan-' + str(int(row_app['encap_vlan_id']))
                            epg_paths_tDN = 'topology/pod-' + str(int(row_app['pod_id'])) + '/paths-' + str(int(row_app['left_node_id'])) + '/pathep-[eth' + str(row_app['access_port_id']) + ']'
                            fvRsPathAtt = SubElement(fvAEPg,'fvRsPathAtt',{'descr':'','encap':epg_encap,'instrImedcy':'lazy','mode':row_app['mode'],'status':'','tDn':epg_paths_tDN})
                        else:
                            epg_encap = 'vlan-' + str(row_app['encap_vlan_id'])
                            epg_protpaths_tDN = 'topology/pod-' + str(int(row_app['pod_id'])) + '/protpaths-' + str(int(row_app['left_node_id'])) + '-' + str(int(row_app['right_node_id'])) + '/pathep-[' + row_app['interface_policy_group'] + ']'
                            fvRsPathAtt = SubElement(fvAEPg,'fvRsPathAtt',{'descr':'','encap':epg_encap,'instrImedcy':'lazy','mode':row_app['mode'],'primaryEncap':'unknown','tDn':epg_protpaths_tDN})
            results.append(root)
            print(tenant,set_of_AppProf)
            set_of_AppProf.clear()

        for result in results:
            print(ExcelImporter().prettify(result))
        return results

    def create_app_profile(self,xl_file):
        # Bridge SpreadSheet
        excel_file = xl_file
        raw_app_prof_sheet = pd.read_excel(excel_file, sheet_name=self.sheet_app_prof )
        app_prof_sheet = raw_app_prof_sheet.sort_values(by=['tenant'])
        set_of_tenants = set()

        results = []
        for index, row in app_prof_sheet.iterrows():
            if pd.notnull(row['status']):
                continue
            else:
                set_of_tenants.add(row['tenant'])
        set_of_tenants = sorted(set_of_tenants)
		
		
        for tenant in set_of_tenants:
            root = Element('polUni')
            # root.set('version', '1.0')
            root.append(Comment('Generated by JTools UCI Builder'))
            self.fvTenant = SubElement(root, 'fvTenant', {'name': tenant, 'status': 'modified'})
            for index, row in app_prof_sheet.iterrows():
                if pd.notnull(row['status']):
                    continue
                else:
                    if row['tenant'] == tenant:
                        fvAp = SubElement(self.fvTenant, 'fvAp', {'descr':row['description'],'name':row['name'],'prio':'unspecified','status':'',})
                        fvRsApMonPol = SubElement(fvAp,'fvRsApMonPol',{'tnMonEPGPolName':''})
            results.append(root)
        for result in results:
            print(ExcelImporter().prettify(result))
        return results






    def call_all_aci_elements(self):
        xl_file = Buildetwork().get_excel_file()
        
        #Buildetwork().create_bridge_domain(xl_file)
        #Buildetwork().create_contract(xl_file)
        #Buildetwork().create_epg(xl_file)
        #Buildetwork().create_epg_stat_bnd(xl_file)
        Buildetwork().create_app_profile(xl_file)


Buildetwork().call_all_aci_elements()



