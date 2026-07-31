#!/usr/bin/env python3
"""
make_pdf.py — Convert வான் வளரொளி HTML to PDF using Chrome headless.

Usage:
    python3 make_pdf.py                         # converts latest v4.x HTML
    python3 make_pdf.py myfile.html             # converts specified file
    python3 make_pdf.py myfile.html out.pdf     # specify output path too

Why this is better than browser print dialog:
  • No user-configurable print settings (margins, headers, scale)
  • Consistent output every time — same rendering as your browser
  • Respects @page { size: A4 } exactly
  • Runs headlessly — no print dialog interaction needed
"""
import subprocess, sys, os, glob, re

BASE = os.path.dirname(os.path.abspath(__file__))

CHROME_PATHS = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
]

def find_chrome():
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    raise RuntimeError('Chrome/Chromium not found. Install Google Chrome.')

def find_latest_html():
    """Find the highest-version v4.x HTML in the project dir."""
    pattern = os.path.join(BASE, 'VAN_Vallaroli_Chittirai2026_v*.html')
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError('No VAN_Vallaroli HTML file found in ' + BASE)
    # Sort by version number
    def version_key(f):
        m = re.search(r'_v(\d+)_(\d+)_', f)
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    return sorted(files, key=version_key)[-1]

def html_to_pdf(html_path, pdf_path, chrome_path):
    html_url = 'file://' + os.path.abspath(html_path)
    cmd = [
        chrome_path,
        '--headless=new',          # new headless mode (Chrome 112+)
        '--disable-gpu',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--run-all-compositor-stages-before-draw',
        '--print-to-pdf=' + os.path.abspath(pdf_path),
        '--print-to-pdf-no-header',     # no "Printed by Chrome" header/footer
        '--no-pdf-header-footer',
        html_url,
    ]
    print(f'  Chrome: {os.path.basename(chrome_path)}')
    print(f'  Input:  {os.path.basename(html_path)}')
    print(f'  Output: {os.path.basename(pdf_path)}')
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Try legacy --headless flag (older Chrome)
        cmd[1] = '--headless'
        result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'\n⚠️  Chrome stderr: {result.stderr[:500]}')
        raise RuntimeError(f'Chrome exited with code {result.returncode}')
    size = os.path.getsize(pdf_path)
    print(f'\n✅ PDF written: {pdf_path}')
    print(f'   Size: {size / 1024 / 1024:.1f} MB')

if __name__ == '__main__':
    # Parse arguments
    if len(sys.argv) >= 3:
        html_in  = sys.argv[1]
        pdf_out  = sys.argv[2]
    elif len(sys.argv) == 2:
        html_in = sys.argv[1]
        pdf_out = os.path.splitext(html_in)[0] + '.pdf'
    else:
        html_in = find_latest_html()
        pdf_out = os.path.splitext(html_in)[0] + '.pdf'

    if not os.path.exists(html_in):
        print(f'Error: {html_in} not found')
        sys.exit(1)

    chrome = find_chrome()
    print('\n🖨️  வான் வளரொளி — PDF Generator')
    print('=' * 50)
    try:
        html_to_pdf(html_in, pdf_out, chrome)
    except Exception as e:
        print(f'\n❌ {e}')
        sys.exit(1)
