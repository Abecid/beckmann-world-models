#!/usr/bin/env python3
"""Validate relative references and build a minimal portable static site."""
from pathlib import Path
from html.parser import HTMLParser
import argparse
import json
import re
import shutil
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = ('index.html', 'styles.css', 'app.js', '.nojekyll', 'robots.txt', 'sitemap.xml')
PUBLIC_DIRS = ('media', 'figures', 'data', 'paper')

class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.errors = [], set(), []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append(f"Duplicate id: {attrs['id']}")
            self.ids.add(attrs['id'])
        for key in ('href', 'src', 'poster'):
            if attrs.get(key): self.refs.append(attrs[key])
        if tag == 'img' and 'alt' not in attrs:
            self.errors.append('Image missing alternative text')
        if tag == 'video' and not attrs.get('aria-label'):
            self.errors.append('Video missing accessible name')

def rendered_html(public=False):
    html = (ROOT / 'index.html').read_text()
    if public:
        # The revised manuscript is private; remove its links from the public page.
        html = re.sub(r'<a\b[^>]*\bdata-review-paper\b[^>]*>.*?</a>\s*', '', html, flags=re.S)
        # Keep the research repository private and omit inaccessible public CTAs.
        html = re.sub(r'<a\b[^>]*href="https://github\.com/Abecid/beckman-world"[^>]*>.*?</a>\s*', '', html, flags=re.S)
    return html

def check(allow_missing_paper=False, public=False):
    document = References()
    document.feed(rendered_html(public))
    errors = document.errors
    for ref in document.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc: continue
        if not url.path and url.fragment:
            if url.fragment not in document.ids:
                errors.append(f'Missing anchor: {ref}')
            continue
        if not url.path: continue
        if url.path.startswith('/'):
            errors.append(f'Root-relative URL breaks project Pages: {ref}')
        target = ROOT / unquote(url.path)
        if not target.is_file():
            if allow_missing_paper and url.path == 'paper/bwm-paper.pdf': continue
            errors.append(f'Missing file: {ref}')
    for manifest_name in ('results.json', 'native-media.json', 'rgb-media-provenance.json', 'comparison.json'):
        manifest_path = ROOT / 'data' / manifest_name
        if not manifest_path.is_file():
            errors.append(f'Missing data manifest: {manifest_name}')
        else:
            json.loads(manifest_path.read_text())
    native = json.loads((ROOT / 'data/native-media.json').read_text())
    for clip in native['clips']:
        for key in ('src', 'poster'):
            if not (ROOT / clip[key]).is_file(): errors.append(f'Missing native asset: {clip[key]}')
        for example in clip['examples']:
            for key in ('src', 'poster'):
                if not (ROOT / example[key]).is_file(): errors.append(f'Missing native example: {example[key]}')
    comparison = json.loads((ROOT / 'data/comparison.json').read_text())
    if len(comparison['images']) != 56:
        errors.append('Comparison must retain all 56 recorded panels')
    for record in comparison['images'].values():
        if not (ROOT / record['src']).is_file(): errors.append(f'Missing comparison frame: {record["src"]}')
    for task, samples in {'pusht': [2, 3, 1], 'can': [5, 3, 4]}.items():
        for sample in samples:
            for ext in ('mp4', 'jpg'):
                if not (ROOT / f'media/{task}-30ep-{sample}.{ext}').is_file():
                    errors.append(f'Missing gallery asset: {task} {sample} {ext}')
    if 'data-pending=' in (ROOT / 'index.html').read_text():
        errors.append('Page contains unfinished metric cells')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Checked {len(document.refs)} HTML references, {len(document.ids)} anchors, all gallery assets, 56 comparison panels, and 4 data manifests.')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Validate without building')
    parser.add_argument('--allow-missing-paper', action='store_true', help='Temporary preview only')
    parser.add_argument('--public', action='store_true', help='Exclude private review PDF and its links')
    args = parser.parse_args()
    check(args.allow_missing_paper, args.public)
    if args.check: return
    dist = ROOT / ('dist-public' if args.public else 'dist')
    if dist.exists(): shutil.rmtree(dist)
    dist.mkdir()
    for name in PUBLIC_FILES:
        if (ROOT / name).exists(): shutil.copy2(ROOT / name, dist / name)
    (dist / 'index.html').write_text(rendered_html(args.public))
    for name in PUBLIC_DIRS:
        if args.public and name == 'paper': continue
        if (ROOT / name).exists(): shutil.copytree(ROOT / name, dist / name)
    if args.public:
        # Retain archived record identities without linking inaccessible private code.
        result_path = dist / 'data' / 'results.json'
        records = result_path.read_text().replace(
            'https://github.com/Abecid/beckman-world/blob/', 'archived-record:')
        result_path.write_text(records)
        # Publish only the curated gallery clips and method/social assets.
        media_root = dist / 'media'
        keep = {'noise.png', 'social-cover.jpg', 'social-cover.png'}
        keep.update(f'{kind}-{i}.jpg' for kind in ('history', 'future') for i in range(1, 5))
        keep.update(f'{task}-30ep-{i}.{ext}' for task, ids in
                    {'pusht': (1, 2, 3), 'can': (3, 4, 5)}.items()
                    for i in ids for ext in ('mp4', 'jpg'))
        keep.update(f'{task}-population70-case{case}.{ext}'
                    for task in ('bridge', 'rt1') for case in ('01', '04') for ext in ('mp4', 'jpg'))
        keep.update(clip[key].removeprefix('media/')
                    for clip in json.loads((ROOT / 'data' / 'native-media.json').read_text())['clips']
                    for key in ('src', 'poster'))
        keep.update(record['src'].removeprefix('media/') for record in
                    json.loads((ROOT / 'data/comparison.json').read_text())['images'].values())
        for path in media_root.rglob('*'):
            if path.is_file() and path.relative_to(media_root).as_posix() not in keep:
                path.unlink()
    files = [p for p in dist.rglob('*') if p.is_file()]
    if args.public:
        if any(p.suffix.lower() == '.pdf' for p in files):
            raise SystemExit('Public artifact unexpectedly contains a PDF')
        if 'paper/bwm-paper.pdf' in (dist / 'index.html').read_text():
            raise SystemExit('Public artifact unexpectedly links the private review draft')
        if 'href="https://github.com/Abecid/beckman-world"' in (dist / 'index.html').read_text():
            raise SystemExit('Public artifact unexpectedly links the private code repository')
    size = sum(p.stat().st_size for p in files)
    print(f'Built {len(files)} static files ({size / 1024 / 1024:.2f} MiB) into {dist}')

if __name__ == '__main__': main()
