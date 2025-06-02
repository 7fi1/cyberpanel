# -*- coding: utf-8 -*-
from random import randint

from django.shortcuts import render, redirect
from django.http import HttpResponse
from plogical.getSystemInformation import SystemInformation
import json
from loginSystem.views import loadLoginPage
from .models import version
import requests
import subprocess
import shlex
import os
import plogical.CyberCPLogFileWriter as logging
from plogical.acl import ACLManager
from manageServices.models import PDNSStatus
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from plogical.processUtilities import ProcessUtilities
from plogical.httpProc import httpProc
from websiteFunctions.models import Websites, WPSites
from databases.models import Databases
from mailServer.models import EUsers
from django.views.decorators.http import require_GET, require_POST
import pwd

# Create your views here.

VERSION = '2.4'
BUILD = 1


@ensure_csrf_cookie
def renderBase(request):
    template = 'baseTemplate/homePage.html'
    cpuRamDisk = SystemInformation.cpuRamDisk()
    finaData = {'ramUsage': cpuRamDisk['ramUsage'], 'cpuUsage': cpuRamDisk['cpuUsage'],
                'diskUsage': cpuRamDisk['diskUsage']}
    proc = httpProc(request, template, finaData)
    return proc.render()


@ensure_csrf_cookie
def versionManagement(request):
    getVersion = requests.get('https://cyberpanel.net/version.txt')
    latest = getVersion.json()
    latestVersion = latest['version']
    latestBuild = latest['build']

    currentVersion = VERSION
    currentBuild = str(BUILD)

    u = "https://api.github.com/repos/usmannasir/cyberpanel/commits?sha=v%s.%s" % (latestVersion, latestBuild)
    logging.writeToFile(u)
    r = requests.get(u)
    latestcomit = r.json()[0]['sha']

    command = "git -C /usr/local/CyberCP/ rev-parse HEAD"
    output = ProcessUtilities.outputExecutioner(command)

    Currentcomt = output.rstrip("\n")
    notechk = True

    if Currentcomt == latestcomit:
        notechk = False

    template = 'baseTemplate/versionManagment.html'
    finalData = {'build': currentBuild, 'currentVersion': currentVersion, 'latestVersion': latestVersion,
                 'latestBuild': latestBuild, 'latestcomit': latestcomit, "Currentcomt": Currentcomt,
                 "Notecheck": notechk}

    proc = httpProc(request, template, finalData, 'versionManagement')
    return proc.render()


@ensure_csrf_cookie
def upgrade_cyberpanel(request):
    if request.method == 'POST':
        try:
            upgrade_command = 'sh <(curl https://raw.githubusercontent.com/usmannasir/cyberpanel/stable/preUpgrade.sh || wget -O - https://raw.githubusercontent.com/usmannasir/cyberpanel/stable/preUpgrade.sh)'
            result = subprocess.run(upgrade_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True)

            if result.returncode == 0:
                response_data = {'success': True, 'message': 'CyberPanel upgrade completed successfully.'}
            else:
                response_data = {'success': False,
                                 'message': 'CyberPanel upgrade failed. Error output: ' + result.stderr}
        except Exception as e:
            response_data = {'success': False, 'message': 'An error occurred during the upgrade: ' + str(e)}


def getAdminStatus(request):
    try:
        val = request.session['userID']
        currentACL = ACLManager.loadedACL(val)

        if os.path.exists('/home/cyberpanel/postfix'):
            currentACL['emailAsWhole'] = 1
        else:
            currentACL['emailAsWhole'] = 0

        if os.path.exists('/home/cyberpanel/pureftpd'):
            currentACL['ftpAsWhole'] = 1
        else:
            currentACL['ftpAsWhole'] = 0

        try:
            pdns = PDNSStatus.objects.get(pk=1)
            currentACL['dnsAsWhole'] = pdns.serverStatus
        except:
            if ProcessUtilities.decideDistro() == ProcessUtilities.ubuntu or ProcessUtilities.decideDistro() == ProcessUtilities.ubuntu20:
                pdnsPath = '/etc/powerdns'
            else:
                pdnsPath = '/etc/pdns'

            if os.path.exists(pdnsPath):
                PDNSStatus(serverStatus=1).save()
                currentACL['dnsAsWhole'] = 1
            else:
                currentACL['dnsAsWhole'] = 0

        json_data = json.dumps(currentACL)
        return HttpResponse(json_data)
    except KeyError:
        return HttpResponse("Can not get admin Status")


def getSystemStatus(request):
    try:
        val = request.session['userID']
        currentACL = ACLManager.loadedACL(val)
        HTTPData = SystemInformation.getSystemInformation()
        json_data = json.dumps(HTTPData)
        return HttpResponse(json_data)
    except KeyError:
        return HttpResponse("Can not get admin Status")


def getLoadAverage(request):
    try:
        val = request.session['userID']
        currentACL = ACLManager.loadedACL(val)
        loadAverage = SystemInformation.cpuLoad()
        loadAverage = list(loadAverage)
        one = loadAverage[0]
        two = loadAverage[1]
        three = loadAverage[2]
        loadAvg = {"one": one, "two": two, "three": three}
        json_data = json.dumps(loadAvg)
        return HttpResponse(json_data)
    except KeyError:
        return HttpResponse("Not allowed.")


@ensure_csrf_cookie
def versionManagment(request):
    ## Get latest version

    getVersion = requests.get('https://cyberpanel.net/version.txt')
    latest = getVersion.json()
    latestVersion = latest['version']
    latestBuild = latest['build']

    ## Get local version

    currentVersion = VERSION
    currentBuild = str(BUILD)

    u = "https://api.github.com/repos/usmannasir/cyberpanel/commits?sha=v%s.%s" % (latestVersion, latestBuild)
    logging.CyberCPLogFileWriter.writeToFile(u)
    r = requests.get(u)
    latestcomit = r.json()[0]['sha']

    command = "git -C /usr/local/CyberCP/ rev-parse HEAD"
    output = ProcessUtilities.outputExecutioner(command)

    Currentcomt = output.rstrip("\n")
    notechk = True

    if (Currentcomt == latestcomit):
        notechk = False

    template = 'baseTemplate/versionManagment.html'
    finalData = {'build': currentBuild, 'currentVersion': currentVersion, 'latestVersion': latestVersion,
                 'latestBuild': latestBuild, 'latestcomit': latestcomit, "Currentcomt": Currentcomt,
                 "Notecheck": notechk}

    proc = httpProc(request, template, finalData, 'versionManagement')
    return proc.render()


def upgrade(request):
    try:
        admin = request.session['userID']
        currentACL = ACLManager.loadedACL(admin)

        data = json.loads(request.body)

        if currentACL['admin'] == 1:
            pass
        else:
            return ACLManager.loadErrorJson('fetchStatus', 0)

        from plogical.applicationInstaller import ApplicationInstaller

        extraArgs = {}
        extraArgs['branchSelect'] = data["branchSelect"]
        background = ApplicationInstaller('UpgradeCP', extraArgs)
        background.start()

        adminData = {"upgrade": 1}
        json_data = json.dumps(adminData)
        return HttpResponse(json_data)

    except KeyError:
        adminData = {"upgrade": 1, "error_message": "Please login or refresh this page."}
        json_data = json.dumps(adminData)
        return HttpResponse(json_data)


def upgradeStatus(request):
    try:
        val = request.session['userID']
        currentACL = ACLManager.loadedACL(val)
        if currentACL['admin'] == 1:
            pass
        else:
            return ACLManager.loadErrorJson('FilemanagerAdmin', 0)

        try:
            if request.method == 'POST':
                from plogical.upgrade import Upgrade

                path = Upgrade.LogPathNew

                try:
                    upgradeLog = ProcessUtilities.outputExecutioner(f'cat {path}')
                except:
                    final_json = json.dumps({'finished': 0, 'upgradeStatus': 1,
                                             'error_message': "None",
                                             'upgradeLog': "Upgrade Just started.."})
                    return HttpResponse(final_json)

                if upgradeLog.find("Upgrade Completed") > -1:

                    command = f'rm -rf {path}'
                    ProcessUtilities.executioner(command)

                    final_json = json.dumps({'finished': 1, 'upgradeStatus': 1,
                                             'error_message': "None",
                                             'upgradeLog': upgradeLog})
                    return HttpResponse(final_json)
                else:
                    final_json = json.dumps({'finished': 0, 'upgradeStatus': 1,
                                             'error_message': "None",
                                             'upgradeLog': upgradeLog})
                    return HttpResponse(final_json)
        except BaseException as msg:
            final_dic = {'upgradeStatus': 0, 'error_message': str(msg)}
            final_json = json.dumps(final_dic)
            return HttpResponse(final_json)
    except KeyError:
        final_dic = {'upgradeStatus': 0, 'error_message': "Not Logged In, please refresh the page or login again."}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def upgradeVersion(request):
    try:



        vers = version.objects.get(pk=1)
        getVersion = requests.get('https://cyberpanel.net/version.txt')
        latest = getVersion.json()
        vers.currentVersion = latest['version']
        vers.build = latest['build']
        vers.save()
        return HttpResponse("Version upgrade OK.")
    except BaseException as msg:
        logging.CyberCPLogFileWriter.writeToFile(str(msg))
        return HttpResponse(str(msg))


@ensure_csrf_cookie
def design(request):
    ### Load Custom CSS
    try:
        from baseTemplate.models import CyberPanelCosmetic
        cosmetic = CyberPanelCosmetic.objects.get(pk=1)
    except:
        from baseTemplate.models import CyberPanelCosmetic
        cosmetic = CyberPanelCosmetic()
        cosmetic.save()

    val = request.session['userID']
    currentACL = ACLManager.loadedACL(val)
    if currentACL['admin'] == 1:
        pass
    else:
        return ACLManager.loadErrorJson('reboot', 0)

    finalData = {}

    if request.method == 'POST':
        MainDashboardCSS = request.POST.get('MainDashboardCSS', '')
        cosmetic.MainDashboardCSS = MainDashboardCSS
        cosmetic.save()
        finalData['saved'] = 1

    ####### Fetch sha...

    sha_url = "https://api.github.com/repos/usmannasir/CyberPanel-Themes/commits"

    sha_res = requests.get(sha_url)

    sha = sha_res.json()[0]['sha']

    l = "https://api.github.com/repos/usmannasir/CyberPanel-Themes/git/trees/%s" % sha
    fres = requests.get(l)
    tott = len(fres.json()['tree'])
    finalData['tree'] = []
    for i in range(tott):
        if (fres.json()['tree'][i]['type'] == "tree"):
            finalData['tree'].append(fres.json()['tree'][i]['path'])

    template = 'baseTemplate/design.html'
    finalData['cosmetic'] = cosmetic

    proc = httpProc(request, template, finalData, 'versionManagement')
    return proc.render()


def getthemedata(request):
    try:
        val = request.session['userID']
        currentACL = ACLManager.loadedACL(val)
        data = json.loads(request.body)

        if currentACL['admin'] == 1:
            pass
        else:
            return ACLManager.loadErrorJson('reboot', 0)

        # logging.CyberCPLogFileWriter.writeToFile(str(data) + "  [themedata]")

        url = "https://raw.githubusercontent.com/usmannasir/CyberPanel-Themes/main/%s/design.css" % data['Themename']

        res = requests.get(url)

        rsult = res.text
        final_dic = {'status': 1, 'csscontent': rsult}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)
    except BaseException as msg:
        final_dic = {'status': 0, 'error_message': str(msg)}
        final_json = json.dumps(final_dic)
        return HttpResponse(final_json)


def onboarding(request):
    template = 'baseTemplate/onboarding.html'

    proc = httpProc(request, template, None, 'admin')
    return proc.render()


def runonboarding(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if currentACL['admin'] == 1:
            pass
        else:
            return ACLManager.loadErrorJson()

        data = json.loads(request.body)
        hostname = data['hostname']

        try:
            rDNSCheck = str(int(data['rDNSCheck']))
        except:
            rDNSCheck = 0

        tempStatusPath = "/home/cyberpanel/" + str(randint(1000, 9999))

        WriteToFile = open(tempStatusPath, 'w')
        WriteToFile.write('Starting')
        WriteToFile.close()

        command = f'/usr/local/CyberCP/bin/python /usr/local/CyberCP/plogical/virtualHostUtilities.py OnBoardingHostName --virtualHostName {hostname} --path {tempStatusPath} --rdns {rDNSCheck}'
        ProcessUtilities.popenExecutioner(command)

        dic = {'status': 1, 'tempStatusPath': tempStatusPath}
        json_data = json.dumps(dic)
        return HttpResponse(json_data)


    except BaseException as msg:
        dic = {'status': 0, 'error_message': str(msg)}
        json_data = json.dumps(dic)
        return HttpResponse(json_data)

def RestartCyberPanel(request):
    try:
        userID = request.session['userID']
        currentACL = ACLManager.loadedACL(userID)

        if currentACL['admin'] == 1:
            pass
        else:
            return ACLManager.loadErrorJson()


        command = 'systemctl restart lscpd'
        ProcessUtilities.popenExecutioner(command)

        dic = {'status': 1}
        json_data = json.dumps(dic)
        return HttpResponse(json_data)


    except BaseException as msg:
        dic = {'status': 0, 'error_message': str(msg)}
        json_data = json.dumps(dic)
        return HttpResponse(json_data)

def getDashboardStats(request):
    try:
        val = request.session['userID']
        currentACL = ACLManager.loadedACL(val)
        total_sites = Websites.objects.count()
        total_wp_sites = WPSites.objects.count()
        total_dbs = Databases.objects.count()
        total_emails = EUsers.objects.count()
        data = {
            'total_sites': total_sites,
            'total_wp_sites': total_wp_sites,
            'total_dbs': total_dbs,
            'total_emails': total_emails,
            'status': 1
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 0, 'error_message': str(e)}), content_type='application/json')

def getTrafficStats(request):
    try:
        val = request.session['userID']
        currentACL = ACLManager.loadedACL(val)
        # Get network stats from /proc/net/dev (Linux)
        rx = tx = 0
        with open('/proc/net/dev', 'r') as f:
            for line in f.readlines():
                if 'lo:' in line:
                    continue
                if ':' in line:
                    parts = line.split()
                    rx += int(parts[1])
                    tx += int(parts[9])
        data = {
            'rx_bytes': rx,
            'tx_bytes': tx,
            'status': 1
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 0, 'error_message': str(e)}), content_type='application/json')

def getDiskIOStats(request):
    try:
        val = request.session['userID']
        currentACL = ACLManager.loadedACL(val)
        # Parse /proc/diskstats for all disks
        read_sectors = 0
        write_sectors = 0
        sector_size = 512  # Most Linux systems use 512 bytes per sector
        with open('/proc/diskstats', 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) < 14:
                    continue
                # parts[2] is device name, skip loopback/ram devices
                dev = parts[2]
                if dev.startswith('loop') or dev.startswith('ram'):
                    continue
                # 6th and 10th columns: sectors read/written
                read_sectors += int(parts[5])
                write_sectors += int(parts[9])
        data = {
            'read_bytes': read_sectors * sector_size,
            'write_bytes': write_sectors * sector_size,
            'status': 1
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 0, 'error_message': str(e)}), content_type='application/json')

def getCPULoadGraph(request):
    try:
        val = request.session['userID']
        currentACL = ACLManager.loadedACL(val)
        # Parse /proc/stat for the 'cpu' line
        with open('/proc/stat', 'r') as f:
            for line in f:
                if line.startswith('cpu '):
                    parts = line.strip().split()
                    # parts[1:] are user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice
                    cpu_times = [float(x) for x in parts[1:]]
                    break
            else:
                cpu_times = []
        data = {
            'cpu_times': cpu_times,
            'status': 1
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'status': 0, 'error_message': str(e)}), content_type='application/json')

@csrf_exempt
@require_GET
def getRecentSSHLogins(request):
    try:
        user_id = request.session.get('userID')
        if not user_id:
            return HttpResponse(json.dumps({'error': 'Not logged in'}), content_type='application/json', status=403)
        currentACL = ACLManager.loadedACL(user_id)
        if not currentACL.get('admin', 0):
            return HttpResponse(json.dumps({'error': 'Admin only'}), content_type='application/json', status=403)

        import re, time
        from collections import OrderedDict

        # Run 'last -n 20' to get recent SSH logins
        try:
            output = ProcessUtilities.outputExecutioner('last -n 20')
        except Exception as e:
            return HttpResponse(json.dumps({'error': 'Failed to run last: %s' % str(e)}), content_type='application/json', status=500)

        lines = output.strip().split('\n')
        logins = []
        ip_cache = {}
        for line in lines:
            if not line.strip() or any(x in line for x in ['reboot', 'system boot', 'wtmp begins']):
                continue
            # Example: ubuntu   pts/0        206.84.168.7     Sun Jun  1 19:41   still logged in
            # or:     ubuntu   pts/0        206.84.169.36    Tue May 27 11:34 - 13:47  (02:13)
            parts = re.split(r'\s+', line, maxsplit=5)
            if len(parts) < 5:
                continue
            user, tty, ip, *rest = parts
            # Find date/time and session info
            date_session = rest[-1] if rest else ''
            # Try to extract date/session
            date_match = re.search(r'([A-Za-z]{3} [A-Za-z]{3} +\d+ [\d:]+)', line)
            date_str = date_match.group(1) if date_match else ''
            session_info = ''
            if '-' in line:
                # Session ended
                session_info = line.split('-')[-1].strip()
            elif 'still logged in' in line:
                session_info = 'still logged in'
            # GeoIP lookup (cache per request)
            country = flag = ''
            if re.match(r'\d+\.\d+\.\d+\.\d+', ip) and ip != '127.0.0.1':
                if ip in ip_cache:
                    country, flag = ip_cache[ip]
                else:
                    try:
                        geo = requests.get(f'http://ip-api.com/json/{ip}', timeout=2).json()
                        country = geo.get('countryCode', '')
                        flag = f"https://flagcdn.com/24x18/{country.lower()}.png" if country else ''
                        ip_cache[ip] = (country, flag)
                    except Exception:
                        country, flag = '', ''
            elif ip == '127.0.0.1':
                country, flag = 'Local', ''
            logins.append({
                'user': user,
                'ip': ip,
                'country': country,
                'flag': flag,
                'date': date_str,
                'session': session_info,
                'raw': line
            })
        return HttpResponse(json.dumps({'logins': logins}), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'error': str(e)}), content_type='application/json', status=500)

@csrf_exempt
@require_GET
def getRecentSSHLogs(request):
    try:
        user_id = request.session.get('userID')
        if not user_id:
            return HttpResponse(json.dumps({'error': 'Not logged in'}), content_type='application/json', status=403)
        currentACL = ACLManager.loadedACL(user_id)
        if not currentACL.get('admin', 0):
            return HttpResponse(json.dumps({'error': 'Admin only'}), content_type='application/json', status=403)
        from plogical.processUtilities import ProcessUtilities
        distro = ProcessUtilities.decideDistro()
        if distro in [ProcessUtilities.ubuntu, ProcessUtilities.ubuntu20]:
            log_path = '/var/log/auth.log'
        else:
            log_path = '/var/log/secure'
        try:
            output = ProcessUtilities.outputExecutioner(f'tail -n 100 {log_path}')
        except Exception as e:
            return HttpResponse(json.dumps({'error': f'Failed to read log: {str(e)}'}), content_type='application/json', status=500)
        lines = output.split('\n')
        logs = []
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) > 4:
                timestamp = ' '.join(parts[:3])
                message = ' '.join(parts[4:])
            else:
                timestamp = ''
                message = line
            logs.append({'timestamp': timestamp, 'message': message, 'raw': line})
        return HttpResponse(json.dumps({'logs': logs}), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'error': str(e)}), content_type='application/json', status=500)

@csrf_exempt
@require_POST
def getSSHUserActivity(request):
    import json, os
    from plogical.processUtilities import ProcessUtilities
    try:
        user_id = request.session.get('userID')
        if not user_id:
            return HttpResponse(json.dumps({'error': 'Not logged in'}), content_type='application/json', status=403)
        currentACL = ACLManager.loadedACL(user_id)
        if not currentACL.get('admin', 0):
            return HttpResponse(json.dumps({'error': 'Admin only'}), content_type='application/json', status=403)
        data = json.loads(request.body.decode('utf-8'))
        user = data.get('user')
        tty = data.get('tty')
        login_ip = data.get('ip', '')
        if not user:
            return HttpResponse(json.dumps({'error': 'Missing user'}), content_type='application/json', status=400)
        # Get processes for the user
        ps_cmd = f"ps -u {user} -o pid,ppid,tty,time,cmd --no-headers"
        try:
            ps_output = ProcessUtilities.outputExecutioner(ps_cmd)
        except Exception as e:
            ps_output = ''
        processes = []
        pid_map = {}
        if ps_output:
            for line in ps_output.strip().split('\n'):
                parts = line.split(None, 4)
                if len(parts) == 5:
                    pid, ppid, tty_val, time_val, cmd = parts
                    if tty and tty not in tty_val:
                        continue
                    # Try to get CWD
                    cwd = ''
                    try:
                        cwd_path = f"/proc/{pid}/cwd"
                        if os.path.islink(cwd_path):
                            cwd = os.readlink(cwd_path)
                    except Exception:
                        cwd = ''
                    proc = {
                        'pid': pid,
                        'ppid': ppid,
                        'tty': tty_val,
                        'time': time_val,
                        'cmd': cmd,
                        'cwd': cwd
                    }
                    processes.append(proc)
                    pid_map[pid] = proc
        # Build process tree
        tree = []
        def build_tree(parent_pid, level=0):
            for proc in processes:
                if proc['ppid'] == parent_pid:
                    proc_copy = proc.copy()
                    proc_copy['level'] = level
                    tree.append(proc_copy)
                    build_tree(proc['pid'], level+1)
        build_tree('1', 0)  # Start from init
        # Find main shell process for history
        shell_history = []
        try:
            shell_home = pwd.getpwnam(user).pw_dir
        except Exception:
            shell_home = f"/home/{user}"
        history_file = ''
        for shell in ['.bash_history', '.zsh_history']:
            path = os.path.join(shell_home, shell)
            if os.path.exists(path):
                history_file = path
                break
        if history_file:
            try:
                with open(history_file, 'r') as f:
                    lines = f.readlines()
                    shell_history = [l.strip() for l in lines[-10:]]
            except Exception:
                shell_history = []
        # Disk usage
        disk_usage = ''
        try:
            du_out = ProcessUtilities.outputExecutioner(f'du -sh {shell_home}')
            disk_usage = du_out.strip().split('\t')[0] if du_out else ''
        except Exception:
            disk_usage = ''
        # GeoIP details
        geoip = {}
        if login_ip and login_ip not in ['127.0.0.1', 'localhost']:
            try:
                geo = requests.get(f'http://ip-api.com/json/{login_ip}?fields=status,message,country,regionName,city,isp,org,as,query', timeout=2).json()
                if geo.get('status') == 'success':
                    geoip = {
                        'country': geo.get('country'),
                        'region': geo.get('regionName'),
                        'city': geo.get('city'),
                        'isp': geo.get('isp'),
                        'org': geo.get('org'),
                        'as': geo.get('as'),
                        'ip': geo.get('query')
                    }
            except Exception:
                geoip = {}
        # Optionally, get 'w' output for more info
        w_cmd = f"w -h {user}"
        try:
            w_output = ProcessUtilities.outputExecutioner(w_cmd)
        except Exception as e:
            w_output = ''
        w_lines = []
        if w_output:
            for line in w_output.strip().split('\n'):
                w_lines.append(line)
        return HttpResponse(json.dumps({
            'processes': processes,
            'process_tree': tree,
            'shell_history': shell_history,
            'disk_usage': disk_usage,
            'geoip': geoip,
            'w': w_lines
        }), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({'error': str(e)}), content_type='application/json', status=500)
