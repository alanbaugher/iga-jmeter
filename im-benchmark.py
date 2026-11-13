#!/usr/bin/env python3
"""Consolidated IGA JMeter benchmark, recovery, reporting, and log diagnostics.
Original benchmark Groovy is retained in im-benchmark.jmx. Recovery JMX is
embedded and extracted into the individual results directory when required.
"""
import argparse, base64, csv, fcntl, getpass, os, re, shutil, subprocess, sys, tempfile, zlib
from pathlib import Path
from datetime import datetime
BASE=Path(__file__).resolve().parent
RESULTS=BASE/'results'
EMBEDDED={'find-im-log-errors.py': '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', 'summarize-im-cycle.py': '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', 'recover-im-run.py': 'eNqNV2tv2zgW/Z5fwWIHoITKcjrtLLAuhEEfnpl042mQpINZOIZAS7TNVK8lqSRG6v++55KSH3Gms/5gh4/7Pvfw5h8vhq3Rw7mqhrK6Y83arurq9Ykqm1pbJvSyEdrIfp2Zu/7PRVbZol8spW2EMf2yNicLXZesEXZVqDnrti+w7K/orU6zaq3aajLtvNF1JnfKrCybhSqkV9nqAhpj51WvF3umKZQ9OcnlgpmsbmSg2yocnTB81IJVNQy2VVyJUsbGCm3NvbKrgJeqaq0c8O4qfbRQ0PyHKFo51rrWAb+ShcyQC+Zvs7msslUp9FfSyXKlcVrrNQ+dDjqQ2iTT2VthyXdrEiNtEL7NocfK3K/cXXKCkatDflviTMdFveRhjACqIGTCsMXOsUWtWaEqRF3tbzubiUZcUuhsFWh+Mz2bDN6Pf//w282MXVyOfzk/+/W3a7bQUiY3+UsmH7KizeEILby7SfBpMj0d/EsMFrPHVz9uwuDn0Y359kPIIzIZHlhDQstRH2csGjibB+X01ezwGvk7F8uooTToityeBn1Koiduvru+Hk8urpnKEx5GQZeq/tbH8fn4evwR93g4Owz9afidtZeaBz6lqZXGpogn+PnFKT4hxTl7fLP55je69etN+N2gt4EjpFjk+wFju0C9uoSEL5JXDKET5rowYmUAayp7H/538fZBVCQMt8W8UGYF5LWV+m8rHd68GSaqnGV1ZZSxsgI4s6xu8VvIfCl1B0XUpalV1QPwKeS0NG1hTXxrix5zlbyn0BPOn0Ofru+piiCB+KPK7KUUudTBIhw9hQcuxqCEgBdiLqH8RcJPf2RX7bxU4BAtc7isRGH4CCFYdJU80IB+TvqeDra6vlye8wiOHdalodov2qIohXXoHypRDlU5DKY39/Fg9jIc8gjKYuKiIxzTgclWspRwcWVtY3hfOzpa1cYSZ9AerVsDaHVrutMcY/G4nF8q+dCAImTOziYMUVAO7WqfRz5dn/ND37alc1gL9p3x0Tia1ezNm9dRQ0g8gOJWmsA4+j8QVoNW4FwvxxzVko87z7S0re7hZ6ans8jAB5lvMT3o0B5GO+ebugHuHC2XQoHTfMKyQiX90xK/08u2BCAuaKXR+ibTqrGqrhJ+oeWdkvcUKVi2vgPwO1efcnHcuQnVlLJUdFoDDqzzyK4bmdD7E749vjEYgMSKNY9E5s0a8LlMrW5lpxV3TUKCzmUSNV0/QTuFYmJ6X9BRdXEnwfVzYby9IE3p8UrTcHdKWmD4sB+7zSGPVTnw0eE1yL72rcmF70na28HO6vXIvcTxgg4C+or8xvnnD/9Ox39+21v9/n6HMrwCsrHsPUmoann22WHjGbBcH0C1JuqpAY1tRdZMGUaZu5N7IPY4iVRuooCQGxFigYy7MNk90LvbdQ7S8VUgELuMuiWTBfzhjQcC30o0GgALFvyqbnUmR+wR+jY31TUkpR0x18uj4fCRbG9Gj2R901PDI9zYDG+qCaxCkoxv2LeOO1kGalW5wLOBM+omxBBueLQoWrNKrgGKnd/dbIEbh0zgveNjlx7Kk8Z7S8wHtaxrGCYKrPM1W6GqAnVdLnHHNRFAGFGmKc2S3dNXVfdyBlB/23Xj6dbqbZnUJkZgSteVJ8xPEzyal0ANNBmrA8LkEEkWILyBfxwHP8X/jF+76c9v8KPY/HgW368U6PW2DEfPDUiWeWPM1p42JqQMGJNZSxyzj4xspYp831nAYY2WcftTfjZJv1zB7VniNnwo/aaLhatS5OgQfqjSiV68u7o6EnWbTrSbU+Pul04p8SBkWt6jTCN2nIKn6p9JwRiFWW+V7KmoW+t5oB9j4/JrTn8HgPRCPSS8b6MBjzBLJtQX4RHML/1bDURC4V+AMSvzZHpbRnwAwuMDy6Nd1cEpnZ0Bcc1t+YAxa8EHn6g/Et8l3G1QpyS+X/wGypS4jvFL4xpu4sfGR9/mG7LXnZzlJuEvsRHf4g1wzePk+jCp6RLfcyRVeC8R1ZOBBGe3e2f78/FsGzIeMNtivNn+00A0HCARxDQeBcS71CsZLO4X1ouOukbyq+25Z+Vjp/5uSnKTklBFC6lkSvPS9+amg1HJtBkF4IYl9/LMnpu9euXT0U+zUccyv7w7w2SEC9Nu3ppFW63d/Qk0i6X0TbA9hJ4GI+TudIcl5Dk5TnxMhIWB+sEGknBvCL1NIbL9/u4ySq7N67oIeped7QWfXo4/fP5jfPmfmWf9jn7BSdlX/E/CPaFW5EF4ggSlKQ09aZokPE1piEhT7hNOb5/vxKs1puBy/IBx0Y8Z3fzrn7jg85Xr0mjXsK5u8lia4CYh/T+7Utv5'}
RECOVERY_JMX='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'
def legacy(name):
    ns={'__name__':'iga_embedded_'+name.replace('-','_'), '__file__':str(BASE/'im-benchmark.py')}
    exec(compile(zlib.decompress(base64.b64decode(EMBEDDED[name])),name,'exec'),ns)
    return ns

def latest():
    files=[p for p in RESULTS.glob('minute-*/results.jtl') if p.is_file()]
    if not files: raise ValueError('No benchmark results in results/minute-*/results.jtl')
    return max(files,key=lambda p:(p.stat().st_mtime_ns,str(p))).parent

def target(value):
    if not value:return latest()
    p=Path(value).expanduser().resolve()
    return p.parent if p.is_file() else p

def jmeter():
    path=os.environ.get('JMETER',str(BASE/'apache-jmeter-5.6.3/bin/jmeter'))
    if not (Path(path).is_file() and os.access(path,os.X_OK)):
        raise ValueError(f'JMeter executable not found: {path}; set JMETER in .env')
    return path

def validate():
    for name in ['USERS','SECONDS_PER_PHASE','EXTRA','CLEANUP_WORKERS']:
        v=int(os.environ.get(name,{'USERS':'10','SECONDS_PER_PHASE':'60','EXTRA':'0','CLEANUP_WORKERS':'32'}[name]))
        lo,hi={'USERS':(1,999),'SECONDS_PER_PHASE':(1,3600),'EXTRA':(0,999),'CLEANUP_WORKERS':(1,64)}[name]
        if not lo<=v<=hi:raise ValueError(f'{name} must be {lo}..{hi}')
    if not (BASE/'im-benchmark.jmx').is_file():raise ValueError('Missing im-benchmark.jmx')
    jmeter()
    print('IGA configuration: valid | Java:',os.environ.get('JAVA_HOME','system default'))
    return 0

def credentials():
    env=os.environ.copy();env.setdefault('IM_USER','imadmin')
    if not env.get('IM_PASS'):env['IM_PASS']=getpass.getpass('IM login password: ')
    if not env['IM_PASS']:raise ValueError('Empty IM password')
    return env

def lock():
    RESULTS.mkdir(parents=True,exist_ok=True)
    f=(RESULTS/'.im-minute.lock').open('a')
    try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        f.close();raise ValueError('Another benchmark or recovery is running')
    return f

def summary(run):
    path=run/'cycle-summary.txt'
    with path.open('w') as out:
        from contextlib import redirect_stdout
        with redirect_stdout(out): verdict=legacy('summarize-im-cycle.py')['summarize'](run)
    print(path.read_text())
    return 0 if verdict=='MET' else 1

def logs(run, all_entries=False):
    m=legacy('find-im-log-errors.py')
    args=['find-im-log-errors.py',str(run),'--logs-root',os.environ.get('IGA_LOGS_ROOT','/opt/brcm/iga/logs'),
          '--seconds',os.environ.get('LOG_PADDING_SECONDS','15'),
          '--server-tz',os.environ.get('SERVER_TZ','America/Chicago'),
          '--router-tz',os.environ.get('ROUTER_TZ','America/Chicago'),
          '--ustore-tz',os.environ.get('USTORE_TZ','America/Chicago')]
    for flag,var in [('--server-log','SERVER_LOG'),('--router-log','ROUTER_LOG'),('--ustore-log','USTORE_LOG')]:
        if os.environ.get(var):args.extend([flag,os.environ[var]])
    if all_entries:args.append('--all')
    old=sys.argv
    try:sys.argv=args;return m['main']()
    finally:sys.argv=old

def recover(run, apply):
    m=legacy('recover-im-run.py')
    marker,ids,(host,port,env_name)=m['scope'](run)
    print(f'Recovery: {len(ids)} ledger candidates | target=https://{host}:{port}/iam/im/{env_name}/ | apply={apply}')
    if not ids:return 0
    child=credentials() if apply else os.environ.copy()
    folder=Path(tempfile.mkdtemp(prefix='recovery-',dir=run))
    plan=folder/'recovery-plan.jmx'
    plan.write_bytes(zlib.decompress(base64.b64decode(RECOVERY_JMX)))
    mode='apply' if apply else 'preview'
    cmd=[jmeter(),'-n','-t',str(plan),f'-Jhost={host}',f'-Jport={port}',f'-Jenv={env_name}',
         f'-JsourceMarker={marker}','-JsourceIds='+','.join(ids),f'-JrecoveryMode={mode}',
         '-l',str(folder/'results.jtl'),'-j',str(folder/'jmeter.log')]
    status=subprocess.run(cmd,env=child,cwd=BASE).returncode
    if status:return status
    with (folder/'results.jtl').open(newline='') as f:
        failed=[row for row in csv.DictReader(f) if row.get('success')!='true']
    for row in failed[:5]:print('FAIL',row.get('label'),row.get('failureMessage') or row.get('responseMessage'))
    log=(folder/'jmeter.log').read_text(errors='replace')
    return int(bool(failed) or f'[RECOVERY] mode={mode} checked=' not in log)

def run():
    validate()
    users=os.environ.get('USERS','10');seconds=os.environ.get('SECONDS_PER_PHASE','60')
    extra=os.environ.get('EXTRA','0');workers=os.environ.get('CLEANUP_WORKERS','32')
    with lock():
        child=credentials()
        run_dir=Path(tempfile.mkdtemp(prefix='minute-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-',dir=RESULTS))
        print(f'Results: {run_dir} | {users} workers | {seconds}s per phase | extra={extra} | cleanup workers={workers}',flush=True)
        cmd=[jmeter(),'-n','-t',str(BASE/'im-benchmark.jmx'),
             '-Jhost='+os.environ.get('IM_HOST','192.168.2.130'),'-Jport='+os.environ.get('IM_PORT','8443'),
             '-Jenv='+os.environ.get('IM_ENV','identityEnv'),'-Jorg='+os.environ.get('IM_ORG','im'),
             '-Jusers='+users,'-Jseconds='+seconds,'-Jextra='+extra,'-JdeleteWorkers='+workers,
             '-Jverbose=false','-l',str(run_dir/'results.jtl'),'-j',str(run_dir/'jmeter.log')]
        status=subprocess.run(cmd,cwd=BASE,env=child).returncode
        log=run_dir/'jmeter.log'
        if not log.is_file():raise ValueError('JMeter did not produce a log; inspect the run')
        content=log.read_text(errors='replace')
        matches=re.findall(r'\[IM-BENCH\] CLEANUP attempted=\d+ confirmed=\d+ deleted=\d+ remaining=(\d+)',content)
        if not matches:
            print('Missing final cleanup inventory; automatic recovery blocked',file=sys.stderr)
            status=status or 1
        elif int(matches[-1])>0:
            print('Remaining accounts detected; attempting run-scoped recovery',flush=True)
            # Release the benchmark lock before recovery reacquires it.
            # Current runner already owns the exclusive lock, so call recovery directly.
            try:status=recover(run_dir,True) or status
            except Exception as exc:print('Recovery failed:',exc,file=sys.stderr);status=status or 1
        if '[IM-BENCH] CLEANUP_TIME ' not in content:
            print('Missing cleanup deadline result',file=sys.stderr);status=status or 1
        return run_dir,status

def menu():
    choices = {'1':'all','2':'run','3':'check','4':'logs','5':'report','6':'recover','7':'recover --apply','8':'latest'}
    if not sys.stdin.isatty():
        raise ValueError('Interactive menu requires a terminal; use --help for commands')
    print('\nIGA Benchmark - Interactive Menu')
    for number, label in [('1','Full benchmark + cleanup + report + log analysis'),
                          ('2','Benchmark + cleanup + report'),('3','Validate configuration'),
                          ('4','Analyze latest run logs'),('5','Report latest run'),
                          ('6','Preview recovery'),('7','Apply recovery (confirmation required)'),
                          ('8','Show latest run'),('0','Exit')]:
        print(f'  {number}. {label}')
    choice=input('Select [0-8]: ').strip()
    if choice=='0':return 0
    if choice not in choices:raise ValueError('Invalid menu selection')
    return main(choices[choice].split())

def confirm_recovery(run_dir):
    if not sys.stdin.isatty():
        raise ValueError('Recovery --apply requires an interactive terminal or --yes')
    print(f'WARNING: recovery may delete benchmark accounts scoped to {run_dir}')
    answer=input('Type APPLY to proceed: ').strip()
    if answer != 'APPLY':
        print('Recovery cancelled; no changes made')
        return False
    return True

def main(argv=None):
    p=argparse.ArgumentParser(prog='./iga-benchmark.sh',description='Broadcom IGA JMeter benchmark: default command is all', epilog='Examples: iga-benchmark.sh | iga-benchmark.sh menu | iga-benchmark.sh recover --apply | iga-benchmark.sh recover --apply --yes')
    p.add_argument('command',nargs='?',choices=['all','run','logs','report','recover','check','latest','menu','help'],default='all')
    p.add_argument('path',nargs='?',help='Existing run directory for logs/report/recover')
    p.add_argument('--apply',action='store_true',help='Apply recovery; default is preview (requires confirmation)')
    p.add_argument('-y','--yes',action='store_true',help='Skip interactive confirmation for recover --apply')
    p.add_argument('--all-entries',action='store_true',help='Show all correlated log entries')
    args=p.parse_args(argv)
    if args.command=='help':p.print_help();return 0
    if args.command=='menu':return menu()
    if args.apply and args.command!='recover':p.error('--apply is only valid with recover')
    if args.yes and not (args.command=='recover' and args.apply):p.error('--yes requires recover --apply')
    if args.command=='check':return validate()
    if args.command=='latest':print(target(args.path));return 0
    if args.command in ('run','all'):
        run_dir,status=run()
        try:status=summary(run_dir) or status
        except Exception as exc:print('Summary failed:',exc,file=sys.stderr);status=status or 1
        if args.command=='all':
            try:
                with (run_dir/'log-analysis.txt').open('w') as f:
                    from contextlib import redirect_stdout
                    with redirect_stdout(f):log_status=logs(run_dir,args.all_entries)
                print((run_dir/'log-analysis.txt').read_text())
                status=log_status or status
            except Exception as exc:print('Log analysis failed:',exc,file=sys.stderr);status=status or 1
        print('Run directory:',run_dir)
        return status
    run_dir=target(args.path)
    if args.command=='report':return summary(run_dir)
    if args.command=='logs':return logs(run_dir,args.all_entries)
    if args.command=='recover':
        if args.apply and not args.yes and not confirm_recovery(run_dir):return 0
        with lock():return recover(run_dir,args.apply)
    return 2

if __name__=='__main__':
    try:sys.exit(main())
    except (OSError,ValueError,KeyError) as exc:sys.exit('IGA benchmark: '+str(exc))
