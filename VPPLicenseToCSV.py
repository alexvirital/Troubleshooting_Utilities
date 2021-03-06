#!/usr/bin/python

import urllib2
import json
import httplib

vpp_licenses_url = 'https://vpp.itunes.apple.com/WebObjects/MZFinance.woa/wa/getVPPLicensesSrv'
vpp_user_url = 'https://vpp.itunes.apple.com/WebObjects/MZFinance.woa/wa/getVPPUserSrv'
app_search_api = 'http://ax.itunes.apple.com/WebObjects/MZStoreServices.woa/wa/wsLookup?id='
stoken_file = ''
csv_file = '/Users/Shared/licenses.csv'
token_string = ''


def main():
    global token_string
    global stoken_file
    if stoken_file == '':
        stoken_file = raw_input('Path to VPP sToken: ')
    license_file = open(csv_file,'wb')
    license_file.write('App ID,License ID,App Name,App Bundle ID,License Status,Assigned User ID,Assigned User Email, \
    Assigned User Association Status')
    license_file.close()
    token_string_file = open(stoken_file.replace('\\','').strip())
    token_string = token_string_file.read()
    batch_token = ''
    while batch_token != 'done':
        batch_token = get_vpp_licenses(token_string, batch_token)


def get_vpp_licenses(token_string, batch_token):
    if batch_token == '':
        body = '{"sToken":"' + str(token_string) + '"}'
    else:
        body = '{"sToken":"' + str(token_string) + '","batchToken":"' + batch_token + '"}'
    try:
        request = urllib2.Request(vpp_licenses_url, body)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'POST'
        data = urllib2.urlopen(request)
    except httplib.HTTPException as inst:
        print "Error getting VPP Licenses: %s" % inst
    except ValueError as inst:
        print "Error getting VPP Licenses: %s" % inst
    except urllib2.HTTPError as inst:
        print "Error getting VPP Licenses: %s" % inst
    vpp_licenses_json = json.load(data)
    for x in vpp_licenses_json['licenses']:
        vpp_license = VPPLicense(x)
        vpp_license.print_everything(csv_file)
    if vpp_licenses_json.get('batchToken'):
        return vpp_licenses_json['batchToken']
    else:
        return 'done'


def get_app_info(adam_id):
    try:
        request = urllib2.Request(app_search_api + str(adam_id))
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'GET'
        data = urllib2.urlopen(request)
        return data
    except httplib.HTTPException as inst:
        print "Error getting app info: %s" % inst
    except ValueError as inst:
        print "Error getting app info: %s" % inst
    except urllib2.HTTPError as inst:
        print "Error getting app info: %s" % inst


def get_vpp_user_info(user_id):
    global token_string
    body = '{"sToken":"' + token_string + '","userId":"' + str(user_id) + '"}'
    try:
        request = urllib2.Request(vpp_user_url, body)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: 'POST'
        data = urllib2.urlopen(request)
        user = json.load(data)
        user_array = [''] * 2
        if user['user'].get('status'):
            user_array[0] = user['user']['status']
        if user['user'].get('email'):
            user_array[1] = user['user']['email']
        return user_array
    except httplib.HTTPException as inst:
        print "Error getting VPP Licenses: %s" % inst
    except ValueError as inst:
        print "Error getting VPP Licenses: %s" % inst
    except urllib2.HTTPError as inst:
        print "Error getting VPP Licenses: %s" % inst


class VPPLicense:
    def __init__(self, license_json):
        self.adam_id = license_json['adamId']
        self.license_id = license_json['licenseId']
        self.product_type = license_json['productTypeName']
        self.status = license_json['status']
        self.user_id = ''
        self.app_info = ''
        self.app_name = ''
        self.app_bundle_id = ''
        self.user_email = ''
        self.user_status = ''
        if self.status == 'Associated':
            self.user_id = license_json['userId']
            user_array = get_vpp_user_info(self.user_id)
            if user_array[0] != '':
                self.user_status = user_array[0]
            if user_array[1] != '':
                self.user_email = user_array[1]
        if self.product_type == 'Application':
            self.app_info = get_app_info(self.adam_id)
            self.app_info_json = json.load(self.app_info)
            self.app_name = self.app_info_json['results'][0]['trackName']
            self.app_name = self.app_name.encode('ascii','ignore')
            self.app_bundle_id = self.app_info_json['results'][0]['bundleId']

    def print_everything(self, file_path):
        license_string = ''
        try:
            license_string = '\n' + str(self.license_id) + \
                         ',' + str(self.adam_id) + \
                         ',' + str(self.app_name) + \
                         ',' + str(self.app_bundle_id) + \
                         ',' + str(self.status) + \
                         ',' + str(self.user_id) + ',' + str(self.user_email) + ',' + str(self.user_status)
        except:
            print "String failed"
        license_file = open(file_path, 'a+')
        license_file.write(license_string)
        license_file.close()


main()
