#!/usr/bin/python3

"""
This script will check the available free disk space on the specified drive, and then tell
  qBittorrent to resume all downloads that won't fill the disk.  Torrents will attempt to download
  in order, but that won't necessarily happen.  e.g. if a drive has 10GB of free space, and the first
  torrent is 20GB and the 2nd is 5GB, the script will tell qBittorrent to resume the 2nd one.

  qBittorrent download settings
    - Downloads - Add to top of queue
    - Downloads - Torrent stop condition: Metadata received
    - WebUI - Bypass authentication for clients on localhost
"""

import shutil, requests, re, os

qbittorrent_ip = os.environ.get('QBITTORRENT_IP', '127.0.0.1')
qbittorrent_port = os.environ.get('QBITTORRENT_PORT', '8080')
qbittorrent_user = os.environ.get('QBITTORRENT_USER', 'admin')
qbittorrent_pass = os.environ.get('QBITTORRENT_PASS', 'adminadmin')
leave_free_space = os.environ.get('MINIMUM_SPACE', '30G')
download_directory = os.environ.get('DOWNLOAD_DIR', 'downloads')

running_states = ['downloading', 'stalledDL', 'forcedDL', 'allocating', 'checkingResumeData', 'moving']
paused_states = ['pausedDL']
base_url = f"http://{qbittorrent_ip}:{qbittorrent_port}/api/v2"


UNITS = {
  'k': 1e3,
  'm': 1e6,
  'g': 1e9,
  't': 1e12,
}

def get_auth_token(requestSession):
  response = requestSession.post(f'{base_url}/auth/login', data = {'username' : qbittorrent_user, 'password': qbittorrent_pass})
  if response.status_code == 200:
    return response.headers['set-cookie'].split(';')[0]
  else:
    print(response.status_code)
  
def parse_size(size):
  m = re.match(r'^([0-9]+(?:\.[0-9]+)?)([kmgt]?)$', size, re.IGNORECASE)
  if not m:
    raise ValueError(f"Unsupported value for leave_free_space: {repr(s)}")
  val = float(m.group(1))
  unit = m.group(2)
  if unit:
    val *= UNITS[unit.lower()]
  return val


disk_stats = shutil.disk_usage(download_directory)
free_space = disk_stats.free
free_space -= parse_size(leave_free_space)

# Get token
request = requests.Session()
request.headers.update({'Accept': 'application/json'})
token = get_auth_token(request)

if token:
  request.headers.update({'Cookie': '{}'.format(token)})
  torrents = request.get(f'{base_url}/torrents/info').json()

  if torrents:
    sorted_torrents = sorted(torrents, key=lambda t: t['priority'])

    for torrent in sorted_torrents:
      if torrent['state'] in running_states:
        free_space -= torrent['amount_left']

    resume_hashes = []
    for torrent in sorted_torrents:
      if torrent['state'] in paused_states and free_space > torrent['amount_left']:
        resume_hashes.append(torrent['hash'])
        print(f'Resuming {torrent["name"]}')
        free_space -= torrent['amount_left']

    if len(resume_hashes) > 0:
      request.post(f'{base_url}/torrents/resume', data = {'hashes': "|".join(resume_hashes)})
    else:
      print("Not enough space to unpause, remaining space would be: {:.1f}G".format(free_space / UNITS['g']))
  else:
    print('There was an issue getting the token: {}'.format(torrents.status_code))