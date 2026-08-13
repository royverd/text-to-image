# text-to-image

Renders a text/JSON/CSV file into a series of monochrome PNG images, paginated to stay under vision-model image size limits — useful for feeding long text content to a vision-capable LLM as images instead of raw text.

## Install

```bash
git clone <this-repo-url>
cd text-to-image
pip install Pillow
```

## Usage

Drop a file named `prompt.txt`, `prompt.json`, or `prompt.csv` in the working directory, then run:

```bash
python text_to_image.py
```

```
Found target file: prompt.json
Processed file data (4213 characters). Splitting and rendering pages...
Saved: output_page_1.png (2048x2456)
Saved: output_page_2.png (2048x1188)

Done! Generated 2 local image file(s).
```

The script finds the first file in the current directory whose name starts with `prompt` and has a supported extension, formats it, wraps it to fit `output_width` (2048px by default), and splits it across pages so no single image exceeds `max_height` (4000px by default). Each page is saved as `output_page_<n>.png` in the current directory.

**File type handling:**

| Extension | Formatting |
|---|---|
| `.json` | Pretty-printed with 2-space indent (`json.dumps(..., indent=2)`) |
| `.csv` | Parsed and rendered as an aligned, pipe-delimited table |
| `.txt` | Written as-is |

To change output size or font size, edit the call in `main()`:

```python
images = text_to_optimized_images(formatted_text, output_width=2048, font_size=12, max_height=4000)
```

## Limitations

- No CLI arguments — input file discovery and output sizing are both fixed in source.
- Only reads UTF-8 text files.
- Font is `Courier` if available on the system, otherwise falls back to Pillow's default bitmap font (which renders noticeably smaller/uglier).
- Line wrapping is a character-count estimate (`output_width / (font_size * 0.6)`), not real text-width measurement, so it can be slightly off for non-monospace-width fonts.
- The `prompt.json` and `output_page_*.png` files in this folder are sample output from a test run, not meant to be committed long-term — clear them out or add them to `.gitignore` before using this as a real repo.

## License

[MIT](LICENSE)
