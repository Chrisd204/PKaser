from logging import error
from unittest import case
from webbrowser import Error
from simple_salesforce import Salesforce, SalesforceLogin
import json
import os
import configparser
import keyring
from tkinter import messagebox
import requests
import re
from collections import OrderedDict

def get_SalesForceReport():
    # code conflict report
    global report_results_temp
    user = os.getlogin()
    
    data_folder = r"C:\\Users\\%s\\AppData\\Roaming\\PKaser" %user
    report_results_temp = data_folder+"\\nt-json-files\\temp_report_results.json"
    data_file = data_folder+"\\config.txt"

    try:
        config = configparser.ConfigParser()
        config.read(data_file)
        username = config.get('credentials','username')
        report_id = '00O1M000007vhEO'
        sf = Salesforce(
            username= username,
            password=keyring.get_password("pkaser-userinfo", username),
            security_token=keyring.get_password("pkaser-token", username)
        )
        report_results = sf.restful('analytics/reports/{}'.format(report_id))
        with open(report_results_temp, 'w') as fp:
            json.dump(report_results, fp)
    except configparser.NoOptionError as e:
        messagebox.showerror(message='Error: get_SalesForceReport(): "{}"'.format(e))
    except json.decoder.JSONDecodeError as e: 
        messagebox.showerror(message='Error: get_SalesForceReport(): "{}"'.format(e))
    except Exception as e:
        messagebox.showerror(message='Error: get_SalesForceReport(): "{}"'.format(e))


def load_OpenCases():

    try:
        # Opening JSON file 
        f = open(report_results_temp) 

        data = json.load(f)
        # Closing file 
        f.close()

        caseInfo = data['factMap']["T!T"]['rows']
        # Closing file 
        f.close()
        caseCount = -1
        for case in caseInfo: 
            caseCount +=1

        openCaseList = []
        while caseCount >= 0:

            strCount = str(caseCount)
            csrUsername = data['factMap']["T!T"]['rows'][caseCount]['dataCells'][15]['label']
            #print(csrUsername)
            sfCaseNumber = data['factMap']["T!T"]['rows'][caseCount]['dataCells'][0]['label']
            #print(sfCaseNumber)
            pcaseNumber = data['factMap']["T!T"]['rows'][caseCount]['dataCells'][2]['label']
            #print(pcaseNumber)
            rollStatus = data['factMap']["T!T"]['rows'][caseCount]['dataCells'][3]['label']
            #print(rollStatus)
            caseType = data['factMap']["T!T"]['rows'][caseCount]['dataCells'][8]['label']
            #print(caseType)
            caseStatus = data['factMap']["T!T"]['rows'][caseCount]['dataCells'][5]['label']
            #print(caseStatus)
            currentQueue = data['factMap']["T!T"]['rows'][caseCount]['dataCells'][7]['label']
            #print(currentQueue)
            pcasePath = "Z:\IT Documents\QA\%s"%(pcaseNumber)
            #print(pcasePath)
            caseSubject = data['factMap']["T!T"]['rows'][caseCount]['dataCells'][9]['label']

            caseDict = {'CSRUSERNAME': csrUsername, 'SFCASENUMBER':sfCaseNumber, 'PCASENUMBER':pcaseNumber,
                        'CASETYPE':caseType, 'CASESTATUS':caseStatus, 'CURRENTQ':currentQueue, 
                        'ROLLSTATUS':rollStatus, 'PCASEPATH':pcasePath, 'CASESUBJECT':caseSubject}

            openCaseList.append(caseDict)
            #print(caseDict)
            #print("---------------------------")   
            caseCount -=1
        
        return openCaseList
    except json.decoder.JSONDecodeError as e:
        messagebox.showerror(message='Error: load_OpenCases(): "{}"'.format(e))
    except Exception as e:
        messagebox.showerror(message='Error: load_OpenCases(): "{}"'.format(e))


def getCasesFromQueue(queue=""):
    user = os.getlogin()
    data_folder = r"C:\\Users\\%s\\AppData\\Roaming\\PKaser" %user
    data_file = data_folder+"\\config.txt"
    config = configparser.ConfigParser()
    config.read(data_file)
    username = config.get('credentials','username')
    organizationId = config.get('credentials','organizationId')
    session = requests.Session()
    sf = Salesforce(
        username= username,
        password=keyring.get_password("pkaser-userinfo", username),
        security_token=keyring.get_password("pkaser-token", username),
        organizationId=organizationId,
        session=session,
    )
   
    qGroup = sf.query("SELECT OwnerId FROM Group WHERE Name = '%s'"%(queue))
    groupOD = qGroup['records'][0]
    OwnerId = groupOD['OwnerId']
    qCases = sf.query("SELECT CaseNumber, Subject FROM Case WHERE OwnerId = '%s'"%(OwnerId))
    casesOD = qCases['records']
    # for i, (key, value) in enumerate(casesOD.items()):
    #     print(key, value)
 



# print(getCasesFromQueue('EIPP'))






def getSfUserId():
    user = os.getlogin()
    data_folder = r"C:\\Users\\%s\\AppData\\Roaming\\PKaser" %user
    data_file = data_folder+"\\config.txt"
    config = configparser.ConfigParser()
    config.read(data_file)
    username = config.get('credentials','username')
    organizationId = config.get('credentials','organizationId')
    session = requests.Session()
    sf = Salesforce(
        username= username,
        password=keyring.get_password("pkaser-userinfo", username),
        security_token=keyring.get_password("pkaser-token", username),
        organizationId=organizationId,
        session=session,
    )
    sf_username = username
    result = sf.query("SELECT Id FROM User WHERE Username = '%s'"%(sf_username))
    for i in result['records']:
        user_sf_id = i['Id']
    return user_sf_id


def get_openCasesByOwner():
    # AST Open Cases By Owner - Stand Up
    global report_results_temp
    user = os.getlogin()
    
    data_folder = r"C:\\Users\\%s\\AppData\\Roaming\\PKaser" %user
    #report_results_temp = data_folder+"\\nt-json-files\\temp_report_results.json"
    data_file = data_folder+"\\config.txt"

    try:
        config = configparser.ConfigParser()
        config.read(data_file)
        username = config.get('credentials','username')
        report_id = '00O1M000007rUPZ'
        sf = Salesforce(
            username= username,
            password=keyring.get_password("pkaser-userinfo", username),
            security_token=keyring.get_password("pkaser-token", username)
        )
        report_results = sf.restful('analytics/reports/{}'.format(report_id))
        with open(report_results_temp, 'w') as fp:
            json.dump(report_results, fp)
    except configparser.NoOptionError as e:
        messagebox.showerror(message='Error: get_openCasesByOwner(): "{}"'.format(e))
    except json.decoder.JSONDecodeError as e: 
        messagebox.showerror(message='Error: get_openCasesByOwner(): "{}"'.format(e))
    except Exception as e:
        messagebox.showerror(message='Error: get_openCasesByOwner(): "{}"'.format(e))


def getSfCaseInfo(case_number=""):
    def IsInt(number):
        try:
            int(number)
            return True
        except:
            return False

    user = os.getlogin()
    data_folder = r"C:\\Users\\%s\\AppData\\Roaming\\PKaser" %user
    data_file = data_folder+"\\config.txt"
    config = configparser.ConfigParser()
    config.read(data_file)
    username = config.get('credentials','username')
    organizationId = config.get('credentials','organizationId')
    regex = r"(?:http|https):\/\/docs.google.com\/spreadsheets(?:[\w.,@?^=%&amp;:\/~+#-]*[\w@?^=%&amp;\/~+#-]+)" # Not exact but works.
    case_number = case_number.strip()
    session = requests.Session()
    sf = Salesforce(
        username= username,
        password=keyring.get_password("pkaser-userinfo", username),
        security_token=keyring.get_password("pkaser-token", username),
        organizationId=organizationId,
        session=session,
    )
    if IsInt(case_number):
        result = sf.query("SELECT description FROM Case WHERE casenumber = '%s'"%(case_number))
        intTotalSize = result['totalSize']
        if intTotalSize:
            od = result['records'][0]
            case_id = od['attributes']['url'].split('/')[-1]
            sf_link = 'https://billtrust.my.salesforce.com/' + case_id
            try:
                srd_link = re.search(regex,od['Description']).group()
            except AttributeError: # NO SRD LINK FOUND IN DESCRIPTION.
                srd_link = 0
            return sf_link, srd_link
        else:
            return False # intTotalSize is 0
    else:
        return False

