import cirq
import cirq.contrib.svg as ccsvg
import resvg_py
from PIL import Image, ImageDraw, ImageFont
from circuits import CircuitCreation

builder = CircuitCreation()
baseline = builder.baseline_circuit()
flag = builder.flag_circuit()

def relabel(circuit, builder):
    """Swap raw LineQubit ids for readable role names, for display only."""
    mapping = {}
    for idx in builder.stabilizer_support:
        mapping[builder.q[idx]] = cirq.NamedQubit(f"Data q{idx}")
    mapping[builder.syndrome] = cirq.NamedQubit("Syndrome ancilla")
    if hasattr(builder, "flag"):
        mapping[builder.flag] = cirq.NamedQubit("Flag ancilla")
    return circuit.transform_qubits(mapping)

def render(circuit, out_png):
    svg = ccsvg.circuit_to_svg(circuit)
    png_bytes = resvg_py.svg_to_bytes(svg_string=svg, background="#ffffff", zoom=3.0)  # <-- REPLACE the cairosvg.svg2png(...) call
    with open(out_png, "wb") as f:
        f.write(bytes(png_bytes))

render(relabel(baseline, builder), "results/baseline_circuit.png")
render(relabel(flag, builder), "results/flag_circuit.png")

# cirq's SVG renderer draws a stray bracket artifact along the top/bottom
# edge of multi-ancilla circuits -- crop it off the flag circuit image.
img = Image.open("results/flag_circuit.png")
w, h = img.size
img.crop((0, 60, w, h - 55)).save("results/flag_circuit.png")

def flatten(path):
    """Composite the transparent PNG onto white so it isn't black when pasted."""
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, "white")
    bg.paste(im, (0, 0), im)
    return bg.convert("RGB")

baseline_img = flatten("results/baseline_circuit.png")
flag_img = flatten("results/flag_circuit.png")

target_w = max(baseline_img.width, flag_img.width)
def pad(img):
    if img.width == target_w:
        return img
    canvas = Image.new("RGB", (target_w, img.height), "white")
    canvas.paste(img, (0, 0))
    return canvas

baseline_img, flag_img = pad(baseline_img), pad(flag_img)

label_h, gap = 90, 40
total_h = label_h + baseline_img.height + gap + label_h + flag_img.height + 30
combined = Image.new("RGB", (target_w, total_h), "white")
draw = ImageDraw.Draw(combined)
font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 44)

y = 10
draw.text((10, y), "Baseline circuit (5 qubits, 7 gates)", fill="black", font=font)
y += label_h
combined.paste(baseline_img, (0, y))
y += baseline_img.height + gap
draw.text((10, y), "Flag circuit (6 qubits, 10 gates)", fill="black", font=font)
y += label_h
combined.paste(flag_img, (0, y))

combined.save("results/methods_circuit_diagram.png")
print("Saved results/methods_circuit_diagram.png")