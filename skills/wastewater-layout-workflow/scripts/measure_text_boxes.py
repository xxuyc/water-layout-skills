"""Read a JSON label array and measure compact boxes using an explicit font."""
import argparse, json, sys
from pathlib import Path
from PIL import ImageFont

def measure(items, font_path, bold_font_path=None, padding=3, scale=4):
    if padding < 0 or scale <= 0:
        raise ValueError('Padding must be nonnegative and scale positive')
    fonts = {}
    result = []
    for item in items:
        size = float(item['size'])
        if size <= 0:
            raise ValueError('Font size must be positive')
        selected = bold_font_path if item.get('bold') and bold_font_path else font_path
        key = (str(selected), round(size * scale))
        if key not in fonts:
            fonts[key] = ImageFont.truetype(key[0], key[1])
        font = fonts[key]
        lines = str(item['text']).split('\n')
        ascent, descent = font.getmetrics()
        line_height = max(size * 1.35, (ascent + descent) / scale)
        result.append({
            'text': item['text'],
            'width': max(font.getlength(line) / scale for line in lines) + 2 * padding,
            'height': line_height * len(lines) + 2 * padding,
            'font_size': size,
            'line_count': len(lines),
        })
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', required=True)
    parser.add_argument('--bold-font')
    parser.add_argument('--input', help='JSON array path, otherwise stdin')
    parser.add_argument('--output', help='Output JSON path, otherwise stdout')
    parser.add_argument('--padding', type=float, default=3)
    args = parser.parse_args()
    source = Path(args.input).read_text(encoding='utf-8-sig') if args.input else sys.stdin.read()
    result = measure(json.loads(source), args.font, args.bold_font, args.padding)
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(encoded, encoding='utf-8')
    else:
        print(encoded)

if __name__ == '__main__':
    main()
