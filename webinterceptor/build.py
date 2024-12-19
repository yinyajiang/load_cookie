#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
import subprocess
from pathlib import Path
import re
import subprocess

def get_cert(): 
    prename='Developer ID Application:'
    output = subprocess.check_output(f'security find-certificate -c "{prename}"', shell=True).decode('utf-8')
    match = re.compile(f'"({prename}.+)"').search(output)
    cert = match.group(1)
    if cert == '':
        raise Exception('No certificate found')
    return cert


current_dir = Path(__file__).parent

def main():

    parser = argparse.ArgumentParser(description='Build Qt project')
    parser.add_argument('--name', default='webinterceptor',
                      help='Target executable name')
    parser.add_argument('--bundle-id', default='com.example.webinterceptor',
                      help='Bundle identifier (macOS)')
    parser.add_argument('--icon',
                      help='Path to icon file')
    args = parser.parse_args()

    # 删除dist
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    isWin= sys.platform == 'win32'


    with open('Info.plist', 'r') as file:
        content = file.read()
        if args.bundle_id:
            content = content.replace('{bundle_id}', args.bundle_id)
    with open('Info_build.plist', 'w') as file:
        file.write(content)

    with open('webinterceptor.pro', 'r') as file:
        content = file.read()
        content = content.replace('{name}', args.name)
        content = content.replace('Info.plist', "Info_build.plist")
        if args.icon:
            if isWin:
                content = content.replace(';RC_ICONS', f'RC_ICONS = {args.icon}')
            else:
                content = content.replace(';ICON', f'ICON = {args.icon}')
    with open('webinterceptor_build.pro', 'w') as file:
        file.write(content)
 
    qt_dir = os.getenv('QT_DIR')
    subprocess.run([f'{qt_dir}/bin/qmake', 'webinterceptor_build.pro'], cwd=current_dir)
    subprocess.run(['make'], cwd=current_dir)
    # 使用macdeployqt部署
    if not isWin:
        subprocess.run([f'{qt_dir}/bin/macdeployqt', f'dist/{args.name}.app',
                        ], cwd=current_dir).check_returncode()
        cert = get_cert()
        if cert:
            subprocess.run([f'codesign', '--timestamp', '--force', '--deep', '--verify', '--verbose', '--sign', cert, f'dist/{args.name}.app'], cwd=current_dir).check_returncode()
            print(f'codesign success')
            subprocess.run(['zip', '-ry', f'{args.name}.zip', f'{args.name}.app'], cwd=os.path.join(current_dir, 'dist')).check_returncode()
        else:
            print(f'not found cert')
          
    # 删除临时文件
    os.remove('webinterceptor_build.pro')
    os.remove('Info_build.plist')


if __name__ == '__main__':
    main()