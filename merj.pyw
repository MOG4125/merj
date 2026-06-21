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
        
        # FIXED: Initialized default visual grid coordinates for the 4 sliders
        self.knob_coords = [[100, 300], [250, 300], [400, 300], [550, 300]]
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

        self.canvas = tk.Canvas(self.root, bg='#050508', highlightthickness=0)
        self.canvas.pack(side='right', expand=True, fill='both')
        self.canvas.bind("<Button-1>", self.identify_clicked_knob)
        self.canvas.bind("<B1-Motion>", self.drag_active_knob)
        self.render_editor_canvas()

    def render_editor_canvas(self):
        self.canvas.delete("all")
        if self.bg_img:
            self.bg_tk = ImageTk.PhotoImage(self.bg_img.resize((850, 700)))
            self.canvas.create_image(0, 0, anchor='nw', image=self.bg_tk)
        else:
            self.canvas.create_text(425, 350, text="[ merj quad engine workspace ]\n\nUpload a background faceplate panel to arrange multiple plugin controls", fill='#333344', font=('Consolas', 11), justify='center')

        if self.knob_img:
            rot = self.knob_img.rotate(-self.test_angle, resample=Image.Resampling.BICUBIC).resize((60, 60))
            self.knob_tk = ImageTk.PhotoImage(rot)
            for i, coord in enumerate(self.knob_coords):
                if i >= sum(1 for p in self.vst_paths if p or (i = 2 and not self.vst_paths[i]: continue
                xml_views.append(f'<view class="CAnimKnob" origin="{coord[0]-30}, {coord[1]-30}" size="60, 60" resource-names="strip_dial" control-tag="{macro_tags}" height-of-one-image="60"/>')
            
            final_views_payload = "\n\t\t".join(xml_views)
            uidesc_payload = f"""<?xml version="1.0" encoding="utf-8"?>
<vstgui-ui-description version="1">
    <template name="view" size="800, 600" bitmap="bg_plate">
        {final_views_payload}
    </template>
</vstgui-ui-description>"""

            bundle_dir = save_p if save_p.endswith(".vst3") else save_p + ".vst3"
            bin_path = os.path.join(bundle_dir, "Contents", "x86_64-win")
            res_path = os.path.join(bundle_dir, "Contents", "Resources")
            os.makedirs(bin_path, exist_ok=True); os.makedirs(res_path, exist_ok=True)

            target_binary = os.path.join(bin_path, os.path.basename(bundle_dir).replace(".vst3", ""))
            shutil.copyfile(self.vst_paths[0], target_binary)

            self.bg_img.resize((800, 600)).save(os.path.join(res_path, "bg_plate.png"))
            canvas_strip.save(os.path.join(res_path, "strip_dial.png"))
            with open(os.path.join(res_path, "plugin.uidesc"), 'w', encoding='utf-8') as f: f.write(uidesc_payload)

            with open(target_binary, 'rb') as f: data = f.read()
            for sig in [b"PeakEater", b"Template", b"BasePlug"]:
                if sig in data: data = data.replace(sig, name.encode('utf-8'))
            with open(target_binary, 'wb') as f: f.write(data)

            messagebox.showinfo("merj Studio Complete", f"Success! Multi-FX compiled.\\nSaved to: {bundle_dir}")
        except Exception as e:
            messagebox.showerror("merj Fault", f"System compilation thread crashed: {str(e)}")

if __name__ == "__main__":
    window = tk.Tk()
    app = MerjV8QuadStudio(window)
    window.mainloop()
