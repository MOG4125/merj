import os, re, math, shutil, tkinter as tk
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
        
        # UI Options Controls
        self.bg_w = 800
        self.bg_h = 600
        self.knob_size = 60
        
        self.knob_coords = [[150, 200], [300, 200], [450, 200], [600, 200]]
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
        ttk.Button(s2, text="LOAD UNIQUE KNOB STICKER", command=self.load_knob_asset).pack(fill='x', padx=10, pady=2)

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

        tk.Button(self.left_panel, text="⚡ MERJ & EXPORT STANDALONE VST3", bg='#ffffff', fg='#000000', font=('Consolas', 10, 'bold'), command=self.build_vst_package, borderwidth=0).pack(fill='x', padx=10, ipady=10, pady=15)

        self.canvas = tk.Canvas(self.root, bg='#000000', highlightthickness=0)
        self.canvas.pack(side='right', expand=True, fill='both')
        self.canvas.bind("<Button-1>", self.identify_clicked_knob)
        self.canvas.bind("<B1-Motion>", self.drag_active_knob)
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
            scale_factor_x = 850 / self.bg_w
            scale_factor_y = 680 / self.bg_h
            display_k_size_x = int(self.knob_size * scale_factor_x)
            display_k_size_y = int(self.knob_size * scale_factor_y)
            
            self.knob_tk = ImageTk.PhotoImage(rot.resize((display_k_size_x, display_k_size_y)))
            
            rad = self.knob_size // 2
            for i, coord in enumerate(self.knob_coords):
                if i >= 2 and not self.vst_paths[i]: continue
                cx = int(coord[0] * scale_factor_x)
                cy = int(coord[1] * scale_factor_y)
                self.canvas.create_image(cx, cy, image=self.knob_tk, tags=f"k_{i}")
                color = '#00ffaa' if i == self.active_knob_index else '#444455'
                rx = int(rad * scale_factor_x)
                ry = int(rad * scale_factor_y)
                self.canvas.create_rectangle(cx-rx, cy-ry, cx+rx, cy+ry, outline=color, dash=(3, 3))

    def load_vst_binary(self, idx):
        p = filedialog.askopenfilename(filetypes=[("VST3 Plugin Binaries", "*.vst3")])
        if p:
            self.vst_paths[idx] = p
            self.lbl_statuses[idx].config(text=os.path.basename(p)[:12], fg='#00ffaa')
            self.render_editor_canvas()

    def load_bg_asset(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg")])
        if p: self.bg_img = Image.open(p); self.render_editor_canvas()

    def load_knob_asset(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png")])
        if p: self.knob_img = Image.open(p); self.render_editor_canvas()

    def preview_rotation(self, val):
        self.test_angle = float(val); self.render_editor_canvas()
    def identify_clicked_knob(self, event):
        self.active_knob_index = -1
        scale_factor_x = 850 / self.bg_w
        scale_factor_y = 680 / self.bg_h
        rad = self.knob_size // 2
        for i, coord in enumerate(self.knob_coords):
            if i >= 2 and not self.vst_paths[i]: continue
            cx = int(coord[0] * scale_factor_x)
            cy = int(coord[1] * scale_factor_y)
            rx = int(rad * scale_factor_x)
            ry = int(rad * scale_factor_y)
            if abs(event.x - cx)  1.0:
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

            macro_tags = self.entry_macro.get().strip()
            xml_views = []
            rad = self.knob_size // 2
            for i, coord in enumerate(self.knob_coords):
                if i >= 2 and not self.vst_paths[i]: continue
                ox = coord[0] - rad
                oy = coord[1] - rad
                xml_views.append(f'<view class="CAnimKnob" origin="{ox}, {oy}" size="{self.knob_size}, {self.knob_size}" resource-names="strip_dial" control-tag="{macro_tags}" height-of-one-image="{self.knob_size}"/>')
            
            final_views_payload = "\n\t\t".join(xml_views)
            uidesc_payload = f"""<?xml version="1.0" encoding="utf-8"?>
<vstgui-ui-description version="1">
    <template name="view" size="{self.bg_w}, {self.bg_h}" bitmap="bg_plate">
        {final_views_payload}
    </template>
</vstgui-ui-description>"""

            bundle_dir = save_p if save_p.endswith(".vst3") else save_p + ".vst3"
            bin_path = os.path.join(bundle_dir, "Contents", "x86_64-win")
            res_path = os.path.join(bundle_dir, "Contents", "Resources")
            os.makedirs(bin_path, exist_ok=True); os.makedirs(res_path, exist_ok=True)

            target_binary = os.path.join(bin_path, os.path.basename(bundle_dir).replace(".vst3", ""))
            shutil.copyfile(self.vst_paths[0], target_binary)

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
            with open(os.path.join(res_path, "plugin.uidesc"), 'w', encoding='utf-8') as f: f.write(uidesc_payload)

            with open(target_binary, 'rb') as f: data = f.read()
            for sig in [b"PeakEater", b"Template", b"BasePlug"]:
                if sig in data: data = data.replace(sig, name.encode('utf-8'))
            with open(target_binary, 'wb') as f: f.write(data)

            messagebox.showinfo("merj Studio Complete", f"Success! Multi-FX compiled.\nSaved to: {bundle_dir}")
        except Exception as e:
            messagebox.showerror("merj Fault", f"System compilation thread crashed: {str(e)}")

if __name__ == "__main__":
    window = tk.Tk()
    app = MerjV8QuadStudio(window)
    window.mainloop()
