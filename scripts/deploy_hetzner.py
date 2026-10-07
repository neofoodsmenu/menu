"""Publish generated menu files over verified explicit FTPS; never delete remote files."""
import os
import ssl
from ftplib import FTP_TLS, error_perm
from pathlib import Path, PurePosixPath


def settings():
    values = {key: os.environ.get('HETZNER_' + key, '') for key in ('HOST', 'USER', 'PASSWORD', 'MENU_DIR')}
    if not all(values.values()):
        raise ValueError('Hetzner deployment secrets are incomplete.')
    target = PurePosixPath(values['MENU_DIR'])
    if not target.is_absolute() or '..' in target.parts or str(target) in ('/', '/public_html'):
        raise ValueError('MENU_DIR must be the absolute dedicated menu directory, not the main website root.')
    if any('\n' in value or '\r' in value for value in values.values()):
        raise ValueError('Invalid deployment configuration.')
    return values


def deploy():
    cfg = settings()
    root = Path(__file__).resolve().parents[1] / '_site'
    if not (root / 'index.html').is_file() or not (root / 'admin/config.yml').is_file():
        raise ValueError('Build output is incomplete.')
    files = sorted((p for p in root.rglob('*') if p.is_file()), key=lambda p: (p.suffix == '.html', p.name == 'index.html', str(p)))
    with FTP_TLS(context=ssl.create_default_context(), timeout=120) as ftp:
        ftp.connect(cfg['HOST'], 21)
        ftp.login(cfg['USER'], cfg['PASSWORD'])
        ftp.prot_p()
        # The target must already exist; a typo must not create an unrelated root.
        ftp.cwd(cfg['MENU_DIR'])
        base = ftp.pwd()
        for path in files:
            if path.is_symlink():
                raise ValueError('Symlink in export.')
            relative = path.relative_to(root)
            ftp.cwd(base)
            for part in relative.parts[:-1]:
                try:
                    ftp.cwd(part)
                except error_perm as exc:
                    if not str(exc).startswith('550'):
                        raise
                    ftp.mkd(part)
                    ftp.cwd(part)
            with path.open('rb') as source:
                ftp.storbinary('STOR ' + path.name, source)
    print(f'Published {len(files)} files to Hetzner. No remote files deleted.')


if __name__ == '__main__':
    deploy()
