
import csv

csv_record = None

pjsip_wizard_header = '''
;!
;! Automatically generated configuration file
;! Filename: pjsip_wizard.conf (/etc/asterisk/pjsip_wizard.conf)
;! Generator: Manager
;! Creation Date: Tue Nov  3 15:06:56 2026
;!

; ==========================================
; SIP Trunk: Universal Trunk Settings
; ==========================================
[MAINEXCH]
type = wizard
sends_registrations = no
accepts_registrations = no
sends_auth = no
accepts_auth = no
transport = trunk-transport-udp
remote_hosts = 10.24.49.144
endpoint/context = exch
endpoint/allow = ulaw,alaw,g722,h264,vp8
endpoint/direct_media = no
aor/qualify_frequency = 15


;
; ==========================================
; Intercom Profile : Universal Settings
; ==========================================
; 
[common-template](!)
type = wizard
accepts_registrations = yes
accepts_auth = yes
transport = transport-udp
has_hint = yes
endpoint/allow = ulaw,alaw,g722,h264,h263,vp8
endpoint/allow_subscribe = yes
endpoint/direct_media = yes
endpoint/trust_id_outbound = yes
endpoint/send_pai = yes
endpoint/send_rpid = yes
aor/max_contacts = 1
aor/qualify_frequency = 15
aor/default_expiration = 120
aor/maximum_expiration = 3600
aor/minimum_expiration = 60


;
; ==========================================
; Intercom Profile : Departmental Settings
; ==========================================
;
[exch-template](!,common-template)
endpoint/context = exch

[GM-template](!,common-template)
endpoint/context = GM

[PCSTE-template](!,common-template)
endpoint/context = PCSTE

[PCCM-template](!,common-template)
endpoint/context = PCCM

[Management-template](!,common-template)
endpoint/context = Management

[PCPO-template](!,common-template)
endpoint/context = PCPO

[PFA-template](!,common-template)
endpoint/context = PFA

[PCMM-template](!,common-template)
endpoint/context = PCMM

[PCOM-template](!,common-template)
endpoint/context = PCOM

[PCEE-template](!,common-template)
endpoint/context = PCEE

[PCME-template](!,common-template)
endpoint/context = PCME

[PCE-template](!,common-template)
endpoint/context = PCE

[PCMD-template](!,common-template)
endpoint/context = PCMD


;
; ==========================================
; Extension Profile 
; ==========================================
;


'''


pjsip_template = '''
[{ext}]({context}-template)
endpoint/callerid = "{CID}"
inbound_auth/username = {ext}
inbound_auth/password = {password}

'''

extension_template = '''
exten => {ext},hint,PJSIP/{ext}
exten => {ext},1,Dial(PJSIP/{ext},Tt)
same => n,Hangup()

'''

pjsip_template_record = ""
extension_template_record = ""
context = "[GM]"

with open("GM_Intercom_Extension_post.csv", mode="r", encoding="utf-8", newline="") as file:
    csv_record = csv.reader(file)
    header = next(csv_record, None)  # Skip the header row if present
    for row in csv_record:
        #print(row[1],": ", row[2])
        ext = row[1]
        cid = "" if row[2]=="-" else row[2]
        pjsip_template_record+=pjsip_template.format(ext=ext, CID=cid, context="GM", password="1234")
        extension_template_record+=extension_template.format(ext=ext)
        

with open("pjsip_wizard.conf", mode="w", encoding="utf-8") as file:
    file.writelines(pjsip_wizard_header)
    file.writelines(pjsip_template_record)

with open("extensions.conf", mode="w", encoding="utf-8") as file:
    file.writelines(context)
    file.writelines(extension_template_record)
