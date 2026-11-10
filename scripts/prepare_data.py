"""Extract only the two required official tables from an authorized archive."""
import argparse
from pathlib import Path
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive',type=Path)
    args=parser.parse_args()
    names=['demographics_diagnosis.csv','biomarkers.csv']
    with ZipFile(args.archive) as z:
        if any(z.namelist().count(n)!=1 for n in names):
            raise ValueError('Archive must contain exactly one copy of each required table.')
        data={n:z.read(n) for n in names}
    out=ROOT/'data/raw'; out.mkdir(parents=True,exist_ok=True)
    for n,content in data.items():
        target=out/n
        if target.exists() and target.read_bytes()!=content:
            raise ValueError(f'Refusing to replace different existing data: {n}')
    for n,content in data.items(): (out/n).write_bytes(content)
    print('Prepared demographics and targeted biomarkers; other modalities were not extracted.')
if __name__=='__main__': main()
