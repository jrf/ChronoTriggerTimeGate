#!/usr/bin/env python3
"""Render timegate.glsl offscreen with moderngl and write timegate.gif.

Usage: python3 capture.py [width] [height] [seconds] [fps]
Defaults: 320 320 4 20  ->  ~80 frames, 4-second loop.
"""
import sys
from pathlib import Path

import moderngl
import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parent
SHADER_PATH = REPO / "timegate.glsl"
OUT_PATH = REPO / "timegate.gif"

VS = """
#version 330 core
in vec2 a_pos;
void main() { gl_Position = vec4(a_pos, 0.0, 1.0); }
"""

# The shader uses Shadertoy conventions (mainImage, iResolution, iTime).
# Only declare uniforms the shader actually reads, so the GL compiler
# doesn't optimize them away and trip moderngl's uniform lookup.
FS_HEADER = """
#version 330 core
uniform vec3 iResolution;
uniform float iTime;
out vec4 _fragColor;
"""

FS_FOOTER = """
void main() { mainImage(_fragColor, gl_FragCoord.xy); }
"""


def render_frames(width: int, height: int, n_frames: int, fps: float):
    user_src = SHADER_PATH.read_text()
    fs = FS_HEADER + user_src + FS_FOOTER

    ctx = moderngl.create_context(standalone=True)
    color_tex = ctx.texture((width, height), 4)
    fbo = ctx.framebuffer(color_attachments=[color_tex])
    fbo.use()
    ctx.viewport = (0, 0, width, height)

    prog = ctx.program(vertex_shader=VS, fragment_shader=fs)
    quad = ctx.buffer(np.array([-1.0, -1.0, 3.0, -1.0, -1.0, 3.0], dtype="f4").tobytes())
    vao = ctx.simple_vertex_array(prog, quad, "a_pos")

    prog["iResolution"].value = (float(width), float(height), 1.0)

    frames = []
    for i in range(n_frames):
        t = i / fps
        prog["iTime"].value = t
        ctx.clear(0.0, 0.0, 0.0, 1.0)
        vao.render(moderngl.TRIANGLES)

        # OpenGL's framebuffer origin is bottom-left; PIL expects top-left.
        raw = fbo.read(components=3, alignment=1)
        img = Image.frombytes("RGB", (width, height), raw).transpose(Image.FLIP_TOP_BOTTOM)
        frames.append(img)

    return frames


def quantize_per_frame(frames):
    """Quantize each frame to its own 256-color palette with Floyd-Steinberg dither.

    A shared cross-frame palette caps total color variety at 256 for the
    entire loop, which crushes the bright vortex peaks. Per-frame palettes
    give each frame its own optimal 256 colors — so peaks that only appear
    in a few frames still get accurate representation.
    """
    return [
        f.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
        for f in frames
    ]


def main():
    args = sys.argv[1:]
    width = int(args[0]) if len(args) > 0 else 320
    height = int(args[1]) if len(args) > 1 else 320
    seconds = float(args[2]) if len(args) > 2 else 4.0
    fps = float(args[3]) if len(args) > 3 else 20.0
    n_frames = int(round(seconds * fps))

    print(f"Rendering {n_frames} frames at {width}x{height} ({fps} fps, {seconds}s loop)...")
    frames = render_frames(width, height, n_frames, fps)

    print("Quantizing palette...")
    palette_frames = quantize_per_frame(frames)

    print(f"Writing {OUT_PATH.name}...")
    palette_frames[0].save(
        OUT_PATH,
        save_all=True,
        append_images=palette_frames[1:],
        duration=int(round(1000.0 / fps)),
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
