"""Create an internal-review archive with an explicit allowlist; exclude raw rows."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
def main():
    status=json.loads((ROOT/'outputs/verification.json').read_text())
    assert status['status']=='passed'
    files=[ROOT/'README.md',ROOT/'requirements.txt',ROOT/'.gitignore']
    files+=sorted((ROOT/'scripts').glob('*.py'))
    files+=sorted((ROOT/'docs').glob('*.md'))
    files+=sorted((ROOT/'outputs').glob('*.json'))
    files+=sorted((ROOT/'outputs').glob('*.md'))
    files+=[ROOT/'outputs/FINAL_REPORT.html']
    files+=sorted((ROOT/'outputs/figures').glob('*.png'))
    files+=sorted((ROOT/'outputs/figures').glob('*.svg'))
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    destination=ROOT/'SPHERE_Research_Package.zip'
    with ZipFile(destination,'w',ZIP_DEFLATED) as z:
        for p in files:
            relative=str(p.relative_to(ROOT))
            assert not any(part in p.relative_to(ROOT).parts for part in ('data','.venv','__pycache__'))
            assert 'local_oof_predictions' not in relative
            z.writestr('sphere-alzheimers/'+relative,p.read_bytes())
        z.writestr('sphere-alzheimers/MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    with ZipFile(destination) as z:
        assert z.testzip() is None
        assert not any(n.endswith('.csv') or '/data/' in n or '/.venv/' in n for n in z.namelist())
        # Detect common credential shapes without displaying any matched text.
        import re
        for n in z.namelist():
            if n.endswith(('.md','.py','.json','.html','.txt')):
                assert not re.search(rb'sphere_[A-Za-z0-9_-]{30,}',z.read(n)), 'Credential-shaped text in package'
    print(f'Packaged {len(files)} files plus checksums; no raw data, row predictions, or credentials.')
if __name__=='__main__': main()
