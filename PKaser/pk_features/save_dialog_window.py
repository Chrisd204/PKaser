import tkinter as tk
from tkinter import ttk
from unittest import case
import validators
import os
import json
from simple_salesforce import Salesforce
import configparser
import keyring


import pk_popouts.create_tool_tip as create_tool_tip
import pk_salesforce.salesForceRequest as salesForceRequest

'''Main Class for 'save' window
Handles requesting user input for pcase information to save for new and 
existing pcases.
'''
class saveDialogWindow:

    def __init__(self,parent,edit):

        # save parent for further use
        self.the_parent = parent

        # Disable parent window
        self.the_parent.toplevel.wm_attributes("-disabled", True)

        # Set Theme for Window
        self.style=ttk.Style()
        self.style.theme_use('vista')

        # Initialize tk instance and frame
        self.save_window = tk.Tk()
        self.save_window.title("New Case")
        self.save_frame = tk.Frame(self.save_window,borderwidth=1)

        # Control Location of Appearence
        self.save_window.geometry('+%d+%d'%(parent.toplevel.winfo_x(),parent.toplevel.winfo_y()))

        # Tell the window manager to give focus back after the X button is hit
        self.save_window.protocol("WM_DELETE_WINDOW", self.kill_window)

        # Set this window to appear on top of all other windows
        self.save_window.attributes("-topmost",True)

        # Add Frame to Window via Grid
        self.save_frame.pack()

        # Initialize Labels
        self.cn_label = tk.Label(self.save_frame,text="Case Number")


        # Initialize Entries
        self.cn_entry = ttk.Entry(self.save_frame,validate="focusout",validatecommand=self.validateSRD,width=50,style="EntryStyle.TEntry")


        # ✔ ❌ ❓
        # Initialize Verify Labels, Label Messages, and Tooltips
        self.cn_valid = ttk.Label(self.save_frame,text="❓",width=3,foreground="#fcba03")

        # self.srd_tt = create_tool_tip.CreateToolTip(self.srd_valid,"SRD will be validated when text is entered and the mouse leaves this box.")
        # self.sf_tt = create_tool_tip.CreateToolTip(self.srd_valid,"SalesForce link will be validated when text is entered and the mouse leaves this box.")


        # Initialize Command Buttons
        #self.save_button =TkinterCustomButton(master=self.save_window,text='Save',bg_color="#ffffcc",fg_color="#003035",corner_radius=5,text_color="white",hover_color="#53ba65",width=80,height=24,command=self.savePCase)
        self.save_button = ttk.Button(self.save_window,text="Save", command=self.savePCase,state=tk.DISABLED)
        self.cancel_button = ttk.Button(self.save_window,text="Cancel",command=self.kill_window)
        self.validate_button = ttk.Button(self.save_window,text="Validate")

        # Pack Command Buttons to Window
        self.save_button.pack(side="right", padx=5, pady=5)
        self.cancel_button.pack(side="right",padx=5)
        self.validate_button.pack(side="left",padx=5)

        # Configure Grid Layout
        self.cn_label.grid(row=2,column=0)
        self.cn_entry.grid(row=2,column=1)
        self.cn_valid.grid(row=2,column=2,padx=2,pady=2)

        # Initialize Data File Location
        user = os.getlogin()
        self.data_folder = "C:\\Users\\%s\\AppData\\Roaming\\PKaser" %user
        self.data_file = self.data_folder+"\\nt-json-files\\pkaser.json"




        # If pcase already exists in data, load and validate
        if edit:
            data = self.the_parent.json_data
            pcase = self.the_parent.pcase_list.item(self.the_parent.pcase_list.selection())['values'][0]
            if pcase in data:
                self.srd_entry.insert(tk.END,data[pcase]['srd_link'])
                self.sf_entry.insert(tk.END,data[pcase]['sf_link'])
                self.validateSF()
                # Used to view srd link.
                print("self.retValidSFLink(): %s"%self.retValidSFLink())
    

       
    def savePCase(self):
        srd_link = ""
        case_number = ""
        if not os.path.exists(self.data_file):
            if not os.path.isdir(self.data_folder):
                os.mkdir(self.data_folder)

            data = {} 
            # Initialize Data File
            with open(self.data_file,'w') as outfile:
                json.dump(data,outfile)

        case_number = salesForceRequest.getSfCaseInfo(self.cn_entry.get().strip())
        if case_number:
            sf_link = case_number[0] # salesforce link
            srd_link = case_number[1] # srd link

        case_info = self.getSFInfo(sf_link)

        if case_info:
            case_info['srd_link'] = srd_link
            case_info['sf_link'] = sf_link
            #case_info['notes'] = ''
            pcase = case_info['pcase']

            json_file = open(self.data_file)
            data = json.load(json_file)
            
            if pcase not in data:
                data[pcase] = case_info
            else:
                data[pcase] = case_info
                

            json_file.close()
            with open(self.data_file,'w') as outfile:
                json.dump(data,outfile)

            self.the_parent.json_data = data
            self.kill_window()
            self.the_parent.loadPCases()
            self.the_parent.pcase_list.selection_set(pcase)
            

    def getSFInfo(self,sf_link):

        if not os.path.exists(self.data_folder+"\\config.txt"):
            e = "No Config File Found. Please Run installer.bat file found in PKaser.zip"
            tk.messagebox.showerror(message='Error: "{}"'.format(e))
            return False
        else:
            config = configparser.ConfigParser()
            config.read(self.data_folder+"\\config.txt")
            username = config.get('credentials','username')
            client = Salesforce(
                username= username,
                password=keyring.get_password("pkaser-userinfo", username),
                security_token=keyring.get_password("pkaser-token", username)
                )
            
            case_id = sf_link.split('/')[-1]
            if 'lightning' in case_id:
                case_id = sf_link.split('/')[6]

            case_info = client.Case.get(case_id)

            case_dict = {
                'subject':case_info['Subject'],
                'last_modified':case_info['LastModifiedDate'],
                'case_owner':case_info['Case_Owner__c'],
                'case_number':case_info['CaseNumber'],
                'parent_case_owner':case_info['Parent_Case_Owner__c'],
                'classification':case_info['Case_Classification__c'],
                'cust_name':case_info['CSR_Username_Cases__c'],
                'pcase':case_info['Z_Case_NoPath__c']
                }
            print(case_dict)

            return case_dict

    def validateSF(self):
        entry = self.cn_entry.get()
        case_number = salesForceRequest.getSfCaseInfo(entry)
        print(case_number)
        if case_number:
            if validators.url(case_number[0]):
                self.cn_valid.config(text="✔",foreground="#198000")
                self.stateHandler()
                return True
        else:
            self.cn_valid.config(text="❌",foreground="#b00505") 
            self.stateHandler()
            return False

    
    def retValidSFLink(self):
        entry = self.cn_entry.get()
        case_number = salesForceRequest.getSfCaseInfo(entry)
        if case_number:
            self.cn_valid.config(text="✔",foreground="#198000")
            self.stateHandler()
            return case_number[0]
        else:
            self.cn_valid.config(text="❌",foreground="#b00505")
            self.stateHandler()
            return False
  

    def validateSRD(self):
        print("validateSRD")
        entry = self.cn_entry.get()
        case_number = salesForceRequest.getSfCaseInfo(entry)
        print(case_number)
        if case_number[1]:
            print("validateSRD - if case_number")
            if validators.url(case_number[1]):
                self.cn_valid.config(text="✔",foreground="#198000")
                self.stateHandler()
                return True
        else:
            self.cn_valid.config(text="✔",foreground="#198000") 
            self.stateHandler()
            return True

    # ✔ ❌ ❓
    def stateHandler(self):
        if self.cn_valid.cget('text') == "✔":
            self.save_button.config(state=tk.ACTIVE)
        else:
            self.save_button.config(state=tk.DISABLED)

    def kill_window(self):
        self.the_parent.toplevel.wm_attributes("-disabled",False)
        self.save_window.destroy()

 