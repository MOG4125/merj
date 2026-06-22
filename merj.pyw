import os, re, math, shutil, json, struct, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk

class MerjV8QuadStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("merj v8.0 // Quad Engine Visual VST Studio")
        self.root.geometry("1200x700")
        self.root.configure(bg='#08080c')

        self.vst_paths = ["", "", "", ""]
        self.bg_img = None
        self.bg_tk = None
        self.knob_img = None
        self.knob_tk = None

        self.bg_w = 800
        self.bg_h = 600
        self.knob_size = 60
        self.knob_is_strip = False

        self.knob_coords = [[100, 100], [200, 100], [300, 100], [400, 100]]
        self.active_knob_index = -1
        self.test_angle = 0
        self.lbl_statuses = []

        self.setup_ui_layout()

    def setup_ui_layout(self):
        self.left_panel = tk.Frame(self.root, bg='#111116', width=350)
        self.left_panel.pack(side='left', fill='y')
        self.left_panel.pack_propagate(False)

        tk.Label(self.left_panel, text="[ merj v8.0 // QUAD ENGINE ]", bg='#111116', fg='#00ffaa', font=('Consolas', 11, 'bold')).pack(pady=10)

        s1 = tk.LabelFrame(self.left_panel, text="1. Core Base Plugins Inputs", bg='#111116', fg='#888899', font=('Consolas', 8))
        s1.pack(fill='x', padx=10, pady=4)
        for i, char in enumerate(['A', 'B', 'C', 'D']):
            f = tk.Frame(s1, bg='#111116')
            f.pack(fill='x', padx=5, pady=2)
            ttk.Button(f, text=f"LOAD VST {char}", command=lambda idx=i: self.load_vst_binary(idx)).pack(side='left', fill='x', expand=True)
            lbl = tk.Label(f, text="unlinked //" if i < 2 else "optional //", bg='#111116', fg='#555566', font=('Consolas', 8, 'italic'))
            lbl.pack(side='left', padx=5)
            self.lbl_statuses.append(lbl)

        s2 = tk.LabelFrame(self.left_panel, text="2. UI Graphic Canvas Assets", bg='#111116', fg='#888899', font=('Consolas', 8))
        s2.pack(fill='x', padx=10, pady=4)
        ttk.Button(s2, text="LOAD BACKDROP PANEL", command=self.load_bg_asset).pack(fill='x', padx=10, pady=2)
        ttk.Button(s2, text="LOAD KNOB IMAGE", command=self.load_knob_asset).pack(fill='x', padx=10, pady=2)

        self.strip_var = tk.BooleanVar(value=False)
        strip_cb = tk.Checkbutton(s2, text="Uploaded knob IS a sprite strip (61 frames)", 
                                   variable=self.strip_var, bg='#111116', fg='#00ffaa',
                                   selectcolor='#111116', activebackground='#111116',
                                   activeforeground='#00ffaa', font=('Consolas', 8),
                                   command=self.toggle_knob_mode)
        strip_cb.pack(anchor='w', padx=10, pady=(0, 2))

        f_size = tk.Frame(s2, bg='#111116')
        f_size.pack(fill='x', padx=10, pady=2)
        tk.Label(f_size, text="W:", bg='#111116', fg='#888899', font=('Consolas', 8)).pack(side='left')
        self.ent_bg_w = tk.Entry(f_size, width=5, bg='#08080c', fg='#ffffff', font=('Consolas', 8))
        self.ent_bg_w.insert(0, "800")
        self.ent_bg_w.pack(side='left', padx=2)
        tk.Label(f_size, text="H:", bg='#111116', fg='#888899', font=('Consolas', 8)).pack(side='left')
        self.ent_bg_h = tk.Entry(f_size, width=5, bg='#08080c', fg='#ffffff', font=('Consolas', 8))
        self.ent_bg_h.insert(0, "600")
        self.ent_bg_h.pack(side='left', padx=2)
        tk.Label(f_size, text="Size:", bg='#111116', fg='#888899', font=('Consolas', 8)).pack(side='left')
        self.ent_k_size = tk.Entry(f_size, width=4, bg='#08080c', fg='#ffffff', font=('Consolas', 8))
        self.ent_k_size.insert(0, "60")
        self.ent_k_size.pack(side='left', padx=2)
        ttk.Button(f_size, text="Apply", command=self.apply_custom_sizes).pack(side='left', padx=2)

        s3 = tk.LabelFrame(self.left_panel, text="3. Macro Parameter Maps (e.g. 0,1,2)", bg='#111116', fg='#888899', font=('Consolas', 8))
        s3.pack(fill='x', padx=10, pady=4)
        self.entry_macro = tk.Entry(s3, bg='#08080c', fg='#00ffaa', font=('Consolas', 10), insertbackground='white', bd=1, relief='solid')
        self.entry_macro.insert(0, "0,1,2")
        self.entry_macro.pack(fill='x', ipady=2, padx=5, pady=2)

        s4 = tk.LabelFrame(self.left_panel, text="4. Product Name String (9 Letters)", bg='#111116', fg='#888899', font=('Consolas', 8))
        s4.pack(fill='x', padx=10, pady=4)
        self.entry_name = tk.Entry(s4, bg='#08080c', fg='#00ffaa', font=('Consolas', 10), insertbackground='white', bd=1, relief='solid')
        self.entry_name.insert(0, "HELLCRUSH")
        self.entry_name.pack(fill='x', ipady=2, padx=5, pady=2)

        s5 = tk.LabelFrame(self.left_panel, text="Live Animation Rotation Preview", bg='#111116', fg='#ffffff', font=('Consolas', 8))
        s5.pack(fill='x', padx=10, pady=4)
        self.rot_scale = tk.Scale(s5, from_=-135, to=135, orient='horizontal', bg='#111116', fg='#00ffaa', highlightthickness=0, command=self.preview_rotation)
        self.rot_scale.pack(fill='x')

        del_frame = tk.Frame(self.left_panel, bg='#111116')
        del_frame.pack(fill='x', padx=10, pady=(0, 5))
        tk.Button(del_frame, text="🗑 DELETE SELECTED KNOB", bg='#ff3333', fg='#ffffff', 
                  font=('Consolas', 9, 'bold'), command=self.delete_selected_knob, borderwidth=0).pack(fill='x', ipady=6)

        add_frame = tk.Frame(self.left_panel, bg='#111116')
        add_frame.pack(fill='x', padx=10, pady=(0, 5))
        tk.Button(add_frame, text="➕ ADD KNOB", bg='#00aa66', fg='#ffffff', 
                  font=('Consolas', 9, 'bold'), command=self.add_knob, borderwidth=0).pack(fill='x', ipady=6)

        tk.Button(self.left_panel, text="⚡ MERJ & EXPORT STANDALONE VST3", bg='#ffffff', fg='#000000', font=('Consolas', 10, 'bold'), command=self.build_vst_package, borderwidth=0).pack(fill='x', padx=10, ipady=10, pady=15)

        self.canvas = tk.Canvas(self.root, bg='#000000', highlightthickness=0)
        self.canvas.pack(side='right', expand=True, fill='both')
        self.canvas.bind("<Button-1>", self.identify_clicked_knob)
        self.canvas.bind("<B1-Motion>", self.drag_active_knob)
        self.root.bind("<Delete>", lambda e: self.delete_selected_knob())
        self.render_editor_canvas()

    def toggle_knob_mode(self):
        self.knob_is_strip = self.strip_var.get()
        self.render_editor_canvas()

    def add_knob(self):
        self.knob_coords.append([self.bg_w // 2, self.bg_h // 2])
        self.active_knob_index = len(self.knob_coords) - 1
        self.render_editor_canvas()

    def delete_selected_knob(self):
        if self.active_knob_index == -1:
            messagebox.showinfo("merj", "No knob selected. Click a knob first, then press Delete or click the delete button.")
            return
        if self.active_knob_index < len(self.knob_coords):
            del self.knob_coords[self.active_knob_index]
        self.active_knob_index = -1
        self.render_editor_canvas()

    def apply_custom_sizes(self):
        try:
            self.bg_w = int(self.ent_bg_w.get().strip())
            self.bg_h = int(self.ent_bg_h.get().strip())
            self.knob_size = int(self.ent_k_size.get().strip())
            self.render_editor_canvas()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric integers for sizes.")

    def render_editor_canvas(self):
        self.canvas.delete("all")
        if self.bg_img:
            bg_aspect = self.bg_img.width / self.bg_img.height
            target_aspect = self.bg_w / self.bg_h
            if bg_aspect > target_aspect:
                scaled_w = self.bg_w
                scaled_h = int(self.bg_w / bg_aspect)
            else:
                scaled_h = self.bg_h
                scaled_w = int(self.bg_h * bg_aspect)

            padded_bg = Image.new("RGBA", (self.bg_w, self.bg_h), (0, 0, 0, 255))
            offset_x = (self.bg_w - scaled_w) // 2
            offset_y = (self.bg_h - scaled_h) // 2
            resized_bg_layer = self.bg_img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
            padded_bg.paste(resized_bg_layer, (offset_x, offset_y))

            self.bg_tk = ImageTk.PhotoImage(padded_bg.resize((850, 680)))
            self.canvas.create_image(0, 0, anchor='nw', image=self.bg_tk)
        else:
            self.canvas.create_text(425, 350, text="[ merj quad engine workspace ]\n\nUpload a background faceplate panel to arrange multiple plugin controls", fill='#333344', font=('Consolas', 11), justify='center')

        if self.knob_img:
            scale_factor_x = 850 / self.bg_w
            scale_factor_y = 680 / self.bg_h
            display_k_size_x = int(self.knob_size * scale_factor_x)
            display_k_size_y = int(self.knob_size * scale_factor_y)

            if self.knob_is_strip:
                frame_h = self.knob_img.height // 61
                mid_frame = self.knob_img.crop((0, frame_h * 30, self.knob_img.width, frame_h * 31))
                preview_img = mid_frame.resize((display_k_size_x, display_k_size_y), Image.Resampling.LANCZOS)
            else:
                k_aspect = self.knob_img.width / self.knob_img.height
                if k_aspect > 1.0:
                    kw = self.knob_size
                    kh = int(self.knob_size / k_aspect)
                else:
                    kh = self.knob_size
                    kw = int(self.knob_size * k_aspect)

                padded_knob = Image.new("RGBA", (self.knob_size, self.knob_size), (0, 0, 0, 0))
                k_offset_x = (self.knob_size - kw) // 2
                k_offset_y = (self.knob_size - kh) // 2
                resized_knob_layer = self.knob_img.resize((kw, kh), Image.Resampling.LANCZOS)
                padded_knob.paste(resized_knob_layer, (k_offset_x, k_offset_y))
                rot = padded_knob.rotate(-self.test_angle, resample=Image.Resampling.BICUBIC)
                preview_img = rot.resize((display_k_size_x, display_k_size_y), Image.Resampling.LANCZOS)

            self.knob_tk = ImageTk.PhotoImage(preview_img)

            rad = self.knob_size // 2
            for i, coord in enumerate(self.knob_coords):
                if i >= len(self.vst_paths):
                    continue
                if i >= 2 and not self.vst_paths[i]:
                    continue
                cx = int(coord[0] * scale_factor_x)
                cy = int(coord[1] * scale_factor_y)
                self.canvas.create_image(cx, cy, image=self.knob_tk, tags=f"k_{i}")
                color = '#00ffaa' if i == self.active_knob_index else '#444455'
                rx = int(rad * scale_factor_x)
                ry = int(rad * scale_factor_y)
                self.canvas.create_rectangle(cx-rx, cy-ry, cx+rx, cy+ry, outline=color, dash=(3, 3))

    def load_vst_binary(self, idx):
        p = filedialog.askopenfilename(filetypes=[("VST3 Plugin", "*.vst3")])
        if p:
            self.vst_paths[idx] = p
            self.lbl_statuses[idx].config(text=os.path.basename(p)[:12], fg='#00ffaa')
            self.render_editor_canvas()

    def load_bg_asset(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg")])
        if p: self.bg_img = Image.open(p); self.render_editor_canvas()

    def load_knob_asset(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png")])
        if p: 
            self.knob_img = Image.open(p)
            if self.knob_img.height > self.knob_img.width * 2:
                self.strip_var.set(True)
                self.knob_is_strip = True
            self.render_editor_canvas()

    def preview_rotation(self, val):
        self.test_angle = float(val); self.render_editor_canvas()

    def identify_clicked_knob(self, event):
        self.active_knob_index = -1
        scale_factor_x = 850 / self.bg_w
        scale_factor_y = 680 / self.bg_h
        rad = self.knob_size // 2
        for i, coord in enumerate(self.knob_coords):
            if i >= len(self.vst_paths):
                continue
            if i >= 2 and not self.vst_paths[i]:
                continue
            cx = int(coord[0] * scale_factor_x)
            cy = int(coord[1] * scale_factor_y)
            rx = int(rad * scale_factor_x)
            ry = int(rad * scale_factor_y)
            if abs(event.x - cx) <= rx and abs(event.y - cy) <= ry:
                self.active_knob_index = i
                break
        self.render_editor_canvas()

    def drag_active_knob(self, event):
        if self.active_knob_index == -1:
            return
        scale_factor_x = 850 / self.bg_w
        scale_factor_y = 680 / self.bg_h
        new_x = int(event.x / scale_factor_x)
        new_y = int(event.y / scale_factor_y)
        new_x = max(0, min(new_x, self.bg_w))
        new_y = max(0, min(new_y, self.bg_h))
        self.knob_coords[self.active_knob_index] = [new_x, new_y]
        self.render_editor_canvas()

    def is_vst3_bundle(self, path):
        return os.path.isdir(path) and os.path.exists(os.path.join(path, "Contents"))

    def get_binary_from_bundle(self, bundle_path):
        if not os.path.isdir(bundle_path):
            return bundle_path
        arch_paths = [
            os.path.join(bundle_path, "Contents", "x86_64-win"),
            os.path.join(bundle_path, "Contents", "x86-win"),
            os.path.join(bundle_path, "Contents", "arm64-win"),
            os.path.join(bundle_path, "Contents", "MacOS"),
        ]
        for arch_dir in arch_paths:
            if os.path.exists(arch_dir):
                for f in os.listdir(arch_dir):
                    if f.endswith('.vst3') or f.endswith('.so') or '.' not in f:
                        return os.path.join(arch_dir, f)
        return None

    def copy_bundle_resources(self, src_bundle, dst_res_path):
        src_res = os.path.join(src_bundle, "Contents", "Resources")
        if os.path.exists(src_res):
            for item in os.listdir(src_res):
                src_item = os.path.join(src_res, item)
                dst_item = os.path.join(dst_res_path, item)
                if os.path.isfile(src_item):
                    shutil.copy2(src_item, dst_item)
                elif os.path.isdir(src_item):
                    if os.path.exists(dst_item):
                        shutil.rmtree(dst_item)
                    shutil.copytree(src_item, dst_item)

    def copy_child_plugins(self, bundle_dir):
        """Copy child plugin binaries into the bundle for the template to load."""
        child_dir = os.path.join(bundle_dir, "Contents", "Resources", "Plugins")
        os.makedirs(child_dir, exist_ok=True)
        copied = []
        for i, path in enumerate(self.vst_paths):
            if not path or i == 0:
                continue
            if self.is_vst3_bundle(path):
                src_bin = self.get_binary_from_bundle(path)
                if src_bin:
                    dst_name = f"Plugin{chr(65+i)}.vst3"
                    shutil.copy2(src_bin, os.path.join(child_dir, dst_name))
                    copied.append(dst_name)
            else:
                dst_name = f"Plugin{chr(65+i)}.vst3"
                shutil.copy2(path, os.path.join(child_dir, dst_name))
                copied.append(dst_name)
        return copied

    def build_vst_package(self):
        try:
            if not self.vst_paths[0]:
                messagebox.showerror("merj Fault", "Base VST A is required.")
                return
            if not self.bg_img:
                messagebox.showerror("merj Fault", "Background panel is required.")
                return
            if not self.knob_img:
                messagebox.showerror("merj Fault", "Knob sticker image is required.")
                return

            name = self.entry_name.get().strip().upper()
            if not name or len(name) != 9:
                messagebox.showerror("merj Fault", "Product name must be exactly 9 letters.")
                return

            base_path = self.vst_paths[0]
            is_bundle = self.is_vst3_bundle(base_path)

            if not is_bundle:
                result = messagebox.askyesno(
                    "merj Warning",
                    f"The selected base plugin is a single .vst3 file (deprecated format).\n\n"
                    f"For best results, use a VST3 BUNDLE folder (with Contents/Resources/).\n\n"
                    f"Continue anyway?"
                )
                if not result:
                    return

            save_p = filedialog.askdirectory()
            if not save_p:
                return

            bundle_dir = os.path.join(save_p, f"{name}.vst3")
            os.makedirs(bundle_dir, exist_ok=True)

            bin_path = os.path.join(bundle_dir, "Contents", "x86_64-win")
            res_path = os.path.join(bundle_dir, "Contents", "Resources")
            os.makedirs(bin_path, exist_ok=True)
            os.makedirs(res_path, exist_ok=True)

            # Copy original resources if base is a bundle
            if is_bundle:
                self.copy_bundle_resources(base_path, res_path)
                src_binary = self.get_binary_from_bundle(base_path)
            else:
                src_binary = base_path

            if not src_binary or not os.path.exists(src_binary):
                messagebox.showerror("merj Fault", "Could not find binary in base plugin.")
                return

            # Copy child plugins B, C, D into bundle
            child_plugins = self.copy_child_plugins(bundle_dir)

            binary_name = f"{name}.vst3"
            target_binary = os.path.join(bin_path, binary_name)
            shutil.copyfile(src_binary, target_binary)

            # Process knob image
            if self.knob_is_strip:
                canvas_strip = self.knob_img.resize((self.knob_size, self.knob_size * 61), Image.Resampling.LANCZOS)
            else:
                k_aspect = self.knob_img.width / self.knob_img.height
                if k_aspect > 1.0:
                    kw = self.knob_size
                    kh = int(self.knob_size / k_aspect)
                else:
                    kh = self.knob_size
                    kw = int(self.knob_size * k_aspect)
                padded_knob = Image.new("RGBA", (self.knob_size, self.knob_size), (0, 0, 0, 0))
                padded_knob.paste(self.knob_img.resize((kw, kh), Image.Resampling.LANCZOS), ((self.knob_size-kw)//2, (self.knob_size-kh)//2))

                canvas_strip = Image.new("RGBA", (self.knob_size, self.knob_size * 61), (0, 0, 0, 0))
                for f in range(61):
                    ang = -135.0 + ((f / 60.0) * 270.0)
                    rot = padded_knob.rotate(-ang, resample=Image.Resampling.BICUBIC)
                    canvas_strip.paste(rot, (0, f * self.knob_size))

            # Build knob XML for VSTGUI-style config
            macro_tags = self.entry_macro.get().strip()
            xml_views = []
            rad = self.knob_size // 2
            for i, coord in enumerate(self.knob_coords):
                if i >= len(self.vst_paths):
                    continue
                if i >= 2 and not self.vst_paths[i]:
                    continue
                ox = coord[0] - rad
                oy = coord[1] - rad
                xml_views.append(f'<view class="CAnimKnob" origin="{ox}, {oy}" size="{self.knob_size}, {self.knob_size}" bitmap="strip_dial" control-tag="{macro_tags}" height-of-one-image="{self.knob_size}"/>')

            final_views_payload = "\n\t\t".join(xml_views)

            uidesc_payload = f"""<?xml version="1.0" encoding="utf-8"?>
<vstgui-ui-description version="1">
    <bitmaps>
        <bitmap name="bg_plate" path="bg_plate.png"/>
        <bitmap name="strip_dial" path="strip_dial.png"/>
    </bitmaps>
    <template name="{name}" size="{self.bg_w}, {self.bg_h}" bitmap="bg_plate">
        {final_views_payload}
    </template>
</vstgui-ui-description>"""

            # CRITICAL: Write comprehensive config with ALL data the template needs
            # This includes plugin paths, knob coordinates, dimensions, etc.
            merj_config = {
                "product_name": name,
                "version": "1.0.0",
                "ui": {
                    "width": self.bg_w,
                    "height": self.bg_h,
                    "background": "bg_plate.png",
                    "knob_strip": "strip_dial.png",
                    "knob_size": self.knob_size,
                    "knob_count": len(self.knob_coords),
                    "knobs": [
                        {
                            "index": i,
                            "x": coord[0],
                            "y": coord[1],
                            "plugin_slot": i,
                            "control_tag": macro_tags
                        }
                        for i, coord in enumerate(self.knob_coords)
                    ]
                },
                "plugins": {
                    "A": {
                        "path": f"Contents/x86_64-win/{binary_name}",
                        "type": "base",
                        "enabled": True
                    },
                    "B": {
                        "path": f"Contents/Resources/Plugins/PluginB.vst3" if self.vst_paths[1] else None,
                        "type": "child",
                        "enabled": bool(self.vst_paths[1])
                    },
                    "C": {
                        "path": f"Contents/Resources/Plugins/PluginC.vst3" if self.vst_paths[2] else None,
                        "type": "child",
                        "enabled": bool(self.vst_paths[2])
                    },
                    "D": {
                        "path": f"Contents/Resources/Plugins/PluginD.vst3" if self.vst_paths[3] else None,
                        "type": "child",
                        "enabled": bool(self.vst_paths[3])
                    }
                }
            }

            # Save config in multiple formats for maximum compatibility
            # JSON format
            with open(os.path.join(res_path, "merj.config.json"), 'w', encoding='utf-8') as f:
                json.dump(merj_config, f, indent=2)

            # XML format (VSTGUI style)
            with open(os.path.join(res_path, "plugin.uidesc"), 'w', encoding='utf-8') as f:
                f.write(uidesc_payload)
            with open(os.path.join(res_path, f"{name.lower()}.uidesc"), 'w', encoding='utf-8') as f:
                f.write(uidesc_payload)
            with open(os.path.join(res_path, "AppWorkspace.xml"), 'w', encoding='utf-8') as f:
                f.write(uidesc_payload)
            with open(os.path.join(res_path, "Interface.xml"), 'w', encoding='utf-8') as f:
                f.write(uidesc_payload)

            # Save images
            bg_aspect = self.bg_img.width / self.bg_img.height
            target_aspect = self.bg_w / self.bg_h
            if bg_aspect > target_aspect:
                scaled_w = self.bg_w
                scaled_h = int(self.bg_w / bg_aspect)
            else:
                scaled_h = self.bg_h
                scaled_w = int(self.bg_h * bg_aspect)

            export_bg = Image.new("RGBA", (self.bg_w, self.bg_h), (0, 0, 0, 255))
            export_bg.paste(self.bg_img.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS), ((self.bg_w-scaled_w)//2, (self.bg_h-scaled_h)//2))

            export_bg.save(os.path.join(res_path, "bg_plate.png"))
            canvas_strip.save(os.path.join(res_path, "strip_dial.png"))

            # Binary patching
            with open(target_binary, 'rb') as f:
                data = bytearray(f.read())

            orig_plugin_file = os.path.basename(base_path)
            if is_bundle:
                orig_plugin_file = os.path.basename(src_binary)
            orig_name_noext = os.path.splitext(orig_plugin_file)[0]

            signatures = [
                b"PeakEater", b"peakeater", b"PEAKEATER",
                b"Template", b"BasePlug", b"baseplug", b"BASEPLUG",
                b"MyPlugin", b"myplugin", b"MYPLUGIN",
            ]

            if 3 <= len(orig_name_noext) <= 30:
                for enc in ['utf-8', 'ascii']:
                    try:
                        sig = orig_name_noext.encode(enc)
                        if sig not in signatures:
                            signatures.append(sig)
                        signatures.append(orig_name_noext.upper().encode(enc))
                        signatures.append(orig_name_noext.lower().encode(enc))
                    except:
                        pass

            for sig in signatures:
                if sig in data:
                    new_name = name.encode('utf-8')
                    if len(new_name) <= len(sig):
                        padded = new_name + b'\x00' * (len(sig) - len(new_name))
                        data = data.replace(sig, padded)

            # UTF-16LE patching
            for sig in signatures:
                try:
                    utf16_sig = sig.decode('utf-8').encode('utf-16-le')
                    if utf16_sig in data:
                        utf16_name = name.encode('utf-16-le')
                        if len(utf16_name) <= len(utf16_sig):
                            padded = utf16_name + b'\x00' * (len(utf16_sig) - len(utf16_name))
                            data = data.replace(utf16_sig, padded)
                except:
                    pass

            with open(target_binary, 'wb') as f:
                f.write(data)

            # Update moduleinfo.json
            moduleinfo = {
                "Name": name,
                "Version": "1.0.0",
                "Factory Info": {
                    "Vendor": "MERJ",
                    "URL": "",
                    "E-Mail": "",
                    "Flags": {
                        "Unicode": True,
                        "Classes Discardable": False,
                        "Component Non Discardable": False
                    }
                },
                "Classes": [
                    {
                        "CID": "84E8DE5F92554F5396FAE4133C935A18",
                        "Category": "Audio Module Class",
                        "Name": name,
                        "Vendor": "MERJ",
                        "Version": "1.0.0",
                        "SDKVersion": "VST 3.7.8",
                        "SubCategories": ["Fx"],
                        "Class Flags": 0,
                        "Cardinality": 2147483647
                    }
                ]
            }
            with open(os.path.join(res_path, "moduleinfo.json"), 'w', encoding='utf-8') as f:
                json.dump(moduleinfo, f, indent=2)

            # Windows bundle files
            desktop_ini = "[.ShellClassInfo]\nIconResource=Plugin.ico,0\n"
            with open(os.path.join(bundle_dir, "desktop.ini"), 'w', encoding='utf-8') as f:
                f.write(desktop_ini)

            try:
                ico = Image.new("RGBA", (32, 32), (8, 8, 12, 255))
                from PIL import ImageDraw
                draw = ImageDraw.Draw(ico)
                draw.text((6, 8), "M", fill=(0, 255, 170, 255))
                ico.save(os.path.join(bundle_dir, "Plugin.ico"), format='ICO')
            except:
                pass

            # Report
            report = f"Bundle saved to: {bundle_dir}\n\n"
            report += f"Base plugin: {'BUNDLE' if is_bundle else 'SINGLE FILE'}\n"
            if child_plugins:
                report += f"Child plugins copied: {', '.join(child_plugins)}\n"
            report += f"Knobs: {len(self.knob_coords)}\n"
            report += f"Config written to: merj.config.json\n"
            report += f"Resources: bg_plate.png, strip_dial.png\n"

            messagebox.showinfo("merj Studio Complete", report)
        except Exception as e:
            messagebox.showerror("merj Fault", f"System compilation thread crashed: {str(e)}")

if __name__ == "__main__":
    window = tk.Tk()
    app = MerjV8QuadStudio(window)
    window.mainloop()
