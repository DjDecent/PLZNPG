# ZPL to PNG

Local Flask application and Python renderer for ZPL labels. The default canvas is
812 × 1218 pixels (4 × 6 inches at 203 DPI).

## Run

```powershell
python -m pip install -r requirements.txt
python examples/web_server.py
```

Open http://localhost:5000. The app renders labels locally.

## Tests

```powershell
python -B -m unittest discover -s tests -v
```

## Current limits

This is a partial ZPL implementation.
The bundled Roboto Condensed and Liberation Mono fonts approximate printer fonts
0 and A; glyph outlines, font metrics, hinting, and barcode captions still differ.
Field blocks (`^FB`) support alignment, word wrapping, explicit `\&` line breaks,
line spacing, hanging indentation, and last-line overprinting. Rotated blocks,
soft hyphens, and exact printer font metrics need further validation.
International encodings and several printer commands are not fully implemented.
Code 128 supports default subset B, explicit subset
invocations, and automatic numeric runs; Data Matrix currently supports square
ECC 200 with the `_1` FNC1 escape. Other barcode options need separate validation.

The canvas dimensions are controlled by the conversion call; out-of-bounds fields
are clipped. `^PW` and `^LL` do not expand the requested media dimensions.

## QR codes

QR model 2 rendering uses qrcodegen. Use `^BQN,2,5,M^FDMA,{$qr$}^FS`
and substitute your actual payload. `MA,` is the normal QR configuration prefix.
Replace `{$logo$}` with valid ZPL graphics before rendering.
QR automatic input, numeric/alphanumeric/manual bytes, magnification, and explicit
mask selection are supported. Model 1 and Kanji/mixed manual modes are not.
