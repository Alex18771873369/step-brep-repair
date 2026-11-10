#!/usr/bin/env python3
"""Read-only CAD discovery. No installations, launches of CAD GUI, or configuration changes."""
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def command_path(name):
    try:
        return shutil.which(name)
    except OSError:
        return None


def probe_freecad_python(path):
    try:
        proc = subprocess.run([str(path), '-c', 'import FreeCAD,Part;print("FREECAD_OK", ".".join(FreeCAD.Version()[:3]))'],
                              timeout=20, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='replace')
        return {'usable': proc.returncode == 0 and 'FREECAD_OK' in proc.stdout,
                'stdout': proc.stdout.strip()[-1000:], 'stderr': proc.stderr.strip()[-1000:], 'exit_code': proc.returncode}
    except Exception as exc:
        return {'usable': False, 'error': str(exc)}


def windows_registry():
    if os.name != 'nt':
        return []
    import winreg
    found = []
    roots = [(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Uninstall'),
             (winreg.HKEY_LOCAL_MACHINE, r'Software\Microsoft\Windows\CurrentVersion\Uninstall'),
             (winreg.HKEY_LOCAL_MACHINE, r'Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall')]
    for hive, path in roots:
        try:
            with winreg.OpenKey(hive, path) as key:
                i = 0
                while True:
                    try:
                        subname = winreg.EnumKey(key, i)
                    except OSError:
                        break
                    i += 1
                    try:
                        with winreg.OpenKey(key, subname) as sub:
                            def val(n):
                                try:
                                    return str(winreg.QueryValueEx(sub, n)[0])
                                except OSError:
                                    return ''
                            name = val('DisplayName')
                            if any(term in name.lower() for term in ('freecad', 'creo', 'solidworks', 'fusion 360', 'autocad', 'inventor', 'solidedge', 'solid edge', 'bricscad', 'onshape', 'rhino', 'siemens nx')):
                                found.append({'name': name, 'version': val('DisplayVersion'), 'location': val('InstallLocation'), 'icon': val('DisplayIcon')})
                    except OSError:
                        pass
        except OSError:
            pass
    return found


def main():
    installed = windows_registry()
    commands = {}
    for name in ('FreeCAD', 'FreeCADCmd', 'freecad', 'freecadcmd', 'parametric', 'solidworks', 'openscad', 'python'):
        p = command_path(name)
        if p:
            commands[name] = p
    python_candidates = set()
    for item in installed:
        if 'freecad' not in item['name'].lower():
            continue
        loc = item.get('location', '').strip().strip('"')
        icon = item.get('icon', '').strip().strip('"')
        if ',' in icon and icon.rsplit(',', 1)[-1].lstrip('-').isdigit():
            icon = icon.rsplit(',', 1)[0].strip().strip('"')
        for root in filter(None, [loc, str(Path(icon).parent) if icon else '']):
            for rel in ('python.exe', 'bin/python.exe', 'bin/python3', 'bin/python'):
                python_candidates.add(str(Path(root) / rel))
    for p in commands.values():
        parent = Path(p).parent
        for rel in ('python.exe', 'python3', 'python'):
            python_candidates.add(str(parent / rel))
    for base in (os.environ.get('ProgramFiles', ''), '/usr/local', '/opt/homebrew', '/Applications/FreeCAD.app/Contents/Resources'):
        if base:
            for rel in ('FreeCAD/bin/python.exe', 'FreeCAD/bin/python3', 'bin/python3'):
                python_candidates.add(str(Path(base) / rel))
    results = []
    for p in sorted(python_candidates):
        if Path(p).is_file():
            results.append({'path': p, **probe_freecad_python(p)})
    report = {'platform': platform.platform(), 'registry_installed_programs': installed, 'path_commands': commands,
              'tested_freecad_python': results,
              'notes': ['Detection is incomplete; a listed CAD program may lack an accessible automation interface or license.',
                        'Existing CAD, MCP connectivity and intended use must be verified separately.',
                        'This detector never installs CAD, configures MCP, launches CAD GUI, or inspects private documents.']}
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
