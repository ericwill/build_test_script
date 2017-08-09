#!/usr/bin/python3

import datetime
import sys, getopt
import xml.etree.ElementTree
from urllib.request import urlopen
import xml.etree.ElementTree
import argparse
import os

CURRENT_DATE = ""
CUSTOM_DATE = ""
BUILD_STRING = ""
TEST_PROJECTS = []
DEFAULT_PROJECTS = ["org.eclipse.ant.tests.ui", "org.eclipse.e4.ui.tests.css.swt", "org.eclipse.swt.tests",
        "org.eclipse.ui.tests", "org.eclipse.e4.ui.tests", "org.eclipse.pde.ui.tests",
        "org.eclipse.e4.ui.bindings.tests", "org.eclipse.e4.ui.tests.css.core", "org.eclipse.equinox.p2.tests.ui",
        "org.eclipse.jdt.ui.tests", "org.eclipse.jdt.ui.tests.refactoring", "org.eclipse.ltk.ui.refactoring.tests",
        "org.eclipse.ui.editors.tests", "org.eclipse.ui.genericeditor.tests",
        "org.eclipse.ui.tests.forms", "org.eclipse.ui.tests.navigator", "org.eclipse.ui.workbench.texteditor.tests"]
WIN = ["ep48I-unit-win32_win32.win32.x86_8.0"]
MAC = ["ep48I-unit-mac64_macosx.cocoa.x86_64_8.0"]
LINUX = ["ep48I-unit-cen64-gtk3_linux.gtk.x86_64_8.0", "ep48I-unit-cen64-gtk2_linux.gtk.x86_64_8.0"]
GTK2 = ["ep48I-unit-cen64-gtk2_linux.gtk.x86_64_8.0"]
GTK3 = ["ep48I-unit-cen64-gtk3_linux.gtk.x86_64_8.0"]
PLATFORMS = []
URL_PREFIX = "http://download.eclipse.org/eclipse/downloads/drops4/"
TEST_DIR = "/testresults/xml/"
FILE_DIR = ""
CUSTOM_FILE = False
CUSTOM_FILE_NAME = ""
FILES = []
SEPARATE_FILE = False
CONSOLE_PRINT = False

def build_string():
    return "I" + CURRENT_DATE + "-2000";

def date_string():
    if not CUSTOM_DATE:
        date = datetime.datetime.now() - datetime.timedelta(days=1)
        month = date.month;
        day = date.day;
        if (month < 10):
            str_month = "0" + str(month)
        else:
            str_month = str(month)
        if (day < 10):
            str_day = "0" + str(day)

        return str(date.year) + str_month + str_day;
    else:
        return CUSTOM_DATE;

def download_files():
    for project in TEST_PROJECTS:
        for platform in PLATFORMS:
            url = URL_PREFIX + BUILD_STRING + TEST_DIR + project + "_" + platform + ".xml"
            try:
                url_open = urlopen(url)
                xml_file_str = url_open.read()
                xml_file = open(FILE_DIR + project + "_" + platform + ".xml", 'wb+')
                FILES.append(FILE_DIR + project + "_" + platform + ".xml")
                xml_file.write(xml_file_str)
                xml_file.close()
            except:
                print("Downloading files for one of the projects failed.", 
                        "Please verify that an I-build actually occurred.")
                sys.exit(2)
    return;

def parse_xml():
    if CUSTOM_FILE:
        if SEPARATE_FILE:
            if os.path.isfile(FILE_DIR + CUSTOM_FILE_NAME + "_stacktraces"):
                os.remove(FILE_DIR + CUSTOM_FILE_NAME + "_stacktraces")
            sep_file = open(FILE_DIR + CUSTOM_FILE_NAME + "_stacktraces", 'ab+')
        if os.path.isfile(FILE_DIR + CUSTOM_FILE_NAME):
            os.remove(FILE_DIR + CUSTOM_FILE_NAME)
        output_file = open(FILE_DIR + CUSTOM_FILE_NAME, 'ab+')
    else:
        if SEPARATE_FILE:
            if os.path.isfile(FILE_DIR + CURRENT_DATE + "_stacktraces"):
                os.remove(FILE_DIR + CURRENT_DATE + "_stacktraces")
            sep_file = open(FILE_DIR + CURRENT_DATE + "_stacktraces", 'ab+')
        if os.path.isfile(FILE_DIR + CURRENT_DATE):
            os.remove(FILE_DIR + CURRENT_DATE)
        output_file = open(FILE_DIR + CURRENT_DATE, 'ab+')
    for file_name in FILES:
        root = xml.etree.ElementTree.parse(file_name).getroot()
        for node in root:
            attributes = node.attrib
            errors = attributes.get("errors")
            failures = attributes.get("failures")
            project_name_fail_or_error = ""
            if int(errors) > 0 or int(failures) > 0:
                for name in TEST_PROJECTS:
                    project_name_fail_or_error = name
                    os_name = ""
                    if "gtk" in file_name:
                        if "gtk2" in file_name:
                            os_name = "GTK2"
                        elif "gtk3" in file_name:
                            os_name = "GTK3"
                    elif "mac64" in file_name:
                        os_name = "MAC"
                    elif "win32" in file_name:
                        os_name = "WIN32"
                    if name in file_name:
                        output_file.write(str.encode(name + " errors: " + errors + 
                            " failures: " + failures + " " + os_name + "\n"))
                        if CONSOLE_PRINT:
                            print(name + " errors: " + errors + " failures: " + failures + " " + os_name)
            if int(errors) > 0:
                for x in node.findall(".//error"):
                    if SEPARATE_FILE:
                        sep_file.write(str.encode(project_name_fail_or_error + "\n" + x.text + "\n"))
                    else:
                        output_file.write(str.encode(x.text + "\n"))
            if int(failures) > 0:
                for x in node.findall(".//failure"):
                    if SEPARATE_FILE:
                        sep_file.write(str.encode(project_name_fail_or_error + "\n" + x.text + "\n"))
                    else:
                        output_file.write(str.encode(x.text + "\n"))
    output_file.close()
    if SEPARATE_FILE:
        sep_file.close()
    return;

def usage():
    print("Usage of this function:")
    print("-c or --console if you'd like the summary of failures/errors printed to the console ",
        "(in addition to file)")
    print("-d or --date if you'd like the results for a specific build date. Format is YYYYMMDD")
    print("-h or --help for help")
    print("-n or --name to specify a custom file name to save test results")
    print("-o or --os to specify the platforms. Format is a comma separated list of [GTK2/GTK3,GTK],WIN32,OSX,", 
        "or just all for all platforms. Note that GTK pulls in both GTK2 and GTK3 results.")
    print("-p or --project to specify the test projects to check. Format is a", 
        "comma separated list of project names (i.e. org.eclipse.swt.tests) or default for a basic",
        "running of the UI test projects")
    print("-s or --separate if stack traces should be printed in a separate file")
    return;

def parse_args():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "cd:hln:o:p:s", ["console","date=", 
            "help", "location", "name=", "os=", "project=", "separate"])
    except getopt.GetoptError as err:
        print("Option not recognized")
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-c", "--console"):
            global CONSOLE_PRINT
            CONSOLE_PRINT = True
        elif o in ("-d", "--date"):
            global CUSTOM_DATE
            CUSTOM_DATE += a
        elif o in ("-s", "--separate"):
            global SEPARATE_FILE
            SEPARATE_FILE = True
        elif o in ("-p", "--project"):
            p_list = a.split(",")
            if a == "default":
                global TEST_PROJECTS
                TEST_PROJECTS = DEFAULT_PROJECTS[:]
            else:
                for project in p_list:
                    TEST_PROJECTS.append(project)
        elif o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-n", "--name"):
            global CUSTOM_FILE
            global CUSTOM_FILE_NAME
            CUSTOM_FILE = True
            CUSTOM_FILE_NAME += a
        elif o in ("-o", "--os"):
            if "all" in a:
                for i in LINUX:
                    PLATFORMS.append(i)
                for i in MAC:
                    PLATFORMS.append(i)
                for i in WIN:
                    PLATFORMS.append(i)
            else:
                if "GTK" in a:
                    if "GTK2" in a:
                        for i in GTK2:
                            PLATFORMS.append(i)
                    elif "GTK3" in a:
                        for i in GTK3:
                            PLATFORMS.append(i)
                    else:
                        for i in LINUX:
                            PLATFORMS.append(i)
                if "OSX" in a:
                    for i in MAC:
                        PLATFORMS.append(i)
                if "WIN32" in a:
                    for i in WIN:
                        PLATFORMS.append(i)
        else:
            print(o + "is not a valid option")
            usage()
            sys.exit(2)
    
    if not PLATFORMS:
        print("No OS specified.")
    elif not TEST_PROJECTS:
        print("No projects specified")
    if not PLATFORMS or not TEST_PROJECTS:
        usage()
    
    return;

def cleanup():
    for file_name in FILES:
        try:
            os.remove(file_name)
        except:
            continue
    return;

if __name__ == "__main__":
    parse_args()
    CURRENT_DATE = date_string()
    BUILD_STRING = build_string()
    download_files()
    parse_xml()
    cleanup()
    sys.exit(0)
