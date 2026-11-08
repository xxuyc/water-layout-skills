"""Read-only inventory of native slide shapes and text, including nested groups."""
import argparse, json, re
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E

NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
EMU_PER_PX = 9525

def inspect(source):
    slides = []
    with ZipFile(source) as package:
        presentation = E.fromstring(package.read('ppt/presentation.xml'))
        size = presentation.find('p:sldSz', NS)
        for filename in sorted((x for x in package.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', x)), key=lambda x: int(re.search(r'(\d+)\.xml$', x)[1])):
            root = E.fromstring(package.read(filename))
            shapes = []
            for node in root.findall('.//p:sp', NS):
                nonvisual = node.find('p:nvSpPr/p:cNvPr', NS)
                transform = node.find('p:spPr/a:xfrm', NS)
                position = None
                if transform is not None:
                    offset, extent = transform.find('a:off', NS), transform.find('a:ext', NS)
                    if offset is not None and extent is not None:
                        position = {k: int(v) / EMU_PER_PX for k, v in zip(('x','y','width','height'), (offset.get('x'), offset.get('y'), extent.get('cx'), extent.get('cy')))}
                paragraphs = [''.join(n.text or '' for n in q.findall('.//a:t', NS)) for q in node.findall('p:txBody/a:p', NS)]
                shapes.append({'id': nonvisual.get('id') if nonvisual is not None else None,
                    'name': nonvisual.get('name') if nonvisual is not None else '',
                    'text': '\n'.join(paragraphs), 'position_px': position})
            slides.append({'package_part': filename, 'native_shape_count': len(shapes),
                'image_count': len(root.findall('.//p:pic', NS)),
                'group_count': len(root.findall('.//p:grpSp', NS)), 'shapes': shapes})
        return {'source': str(Path(source).absolute()),
            'slide_size_emu': dict(size.attrib) if size is not None else None,
            'position_note': 'Grouped shapes use local group coordinates, not absolute slide coordinates.',
            'slides': slides}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('--output')
    args = parser.parse_args()
    encoded = json.dumps(inspect(args.source), ensure_ascii=False, indent=2)
    if args.output:
        target = Path(args.output)
        if target.resolve() == Path(args.source).resolve():
            parser.error('Output must not overwrite source')
        target.write_text(encoded, encoding='utf-8')
    else:
        print(encoded)

if __name__ == '__main__':
    main()
