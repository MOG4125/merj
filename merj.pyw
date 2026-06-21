import os
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class MerjV5CompilerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("merj v5.0 // Direct VST Export Matrix")
        self.root.geometry("600x580")
        self.root.configure(bg='#0b0b0f')

        # Neon Terminal Styling
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TButton', background='#00ffaa', foreground='#000000', font=('Consolas', 10, 'bold'), borderwidth=0)
        self.style.map('TButton', background=[('active', '#00cc88')])

        self.file_paths = ["", "", "", ""]
        self.lbl_statuses = []
        self.knob_strip_path = ""

        self.build_interface()

    def build_interface(self):
        tk.Label(self.root, text="[ merj v5.0 // NO-CODE VST EXPORTER ]", bg='#0b0b0f', fg='#00ffaa', font=('Consolas', 13, 'bold')).pack(pady=15)

        # 4 Layout File Upload Slots
        slot_letters = ['A', 'B', 'C', 'D']
        for i in range(4):
            frame = tk.Frame(self.root, bg='#14141a', bd=1, relief='solid')
            frame.pack(fill='x', padx=25, pady=5)
            tk.Label(frame, text=f"Layout {slot_letters[i]} (.uidesc/.xml):", bg='#14141a', fg='#888899', font=('Consolas', 9)).pack(side='left', padx=10)
            btn = ttk.Button(frame, text="BROWSE", command=lambda idx=i: self.load_layout(idx))
            btn.pack(side='left', padx=10, pady=5)
            lbl = tk.Label(frame, text="empty //", bg='#14141a', fg='#555566', font=('Consolas', 9, 'italic'))
            lbl.pack(side='left', padx=5)
            self.lbl_statuses.append(lbl)

        # Knobman Asset Upload Slot
        frame_art = tk.Frame(self.root, bg='#14141a', bd=1, relief='solid')
        frame_art.pack(fill='x', padx=25, pady=10)
        tk.Label(frame_art, text="SkinMan / Knobman Animation (.png):", bg='#14141a', fg='#ffffff', font=('Consolas', 9)).pack(side='left', padx=10)
        ttk.Button(frame_art, text="LOAD ART", command=self.load_knob_art).pack(side='left', padx=10, pady=5)
        self.lbl_art_status = tk.Label(frame_art, text="no art loaded //", bg='#14141a', fg='#555566', font=('Consolas', 9, 'italic'))
        self.lbl_art_status.pack(side='left', padx=5)

        # Parameter Mapping Field
        frame_macro = tk.Frame(self.root, bg='#0b0b0f')
        frame_macro.pack(fill='x', padx=25, pady=5)
        tk.Label(frame_macro, text="Bind Macro Control Slider to Target Parameter IDs:", bg='#0b0b0f', fg='#ffffff', font=('Consolas', 10, 'bold')).pack(anchor='w')
        self.entry_macro_ids = tk.Entry(frame_macro, bg='#14141a', fg='#00ffaa', font=('Consolas', 11), insertbackground='white', bd=1, relief='solid')
        self.entry_macro_ids.insert(0, "0,1,2")
        self.entry_macro_ids.pack(fill='x', ipady=4, pady=5)

        # Name Configuration Field
        tk.Label(frame_macro, text="Custom VST Display Name (Must be exactly 9 letters long):", bg='#0b0b0f', fg='#ffffff', font=('Consolas', 10, 'bold')).pack(anchor='w')
        self.entry_name = tk.Entry(frame_macro, bg='#14141a', fg='#00ffaa', font=('Consolas', 11), insertbackground='white', bd=1, relief='solid')
        self.entry_name.insert(0, "HELLCRUSH")
        self.entry_name.pack(fill='x', ipady=4, pady=5)

        # Compile and Export Trigger Button
        tk.Button(self.root, text="⚡ GENERATE STANDALONE VST3 PLUGIN", bg='#ffffff', fg='#000000', font=('Consolas', 11, 'bold'), command=self.compile_vst_package, borderwidth=0).pack(fill='x', padx=25, ipady=10, pady=15)

    def load_layout(self, index):
        path = filedialog.askopenfilename(filetypes=[("UI Description", "*.uidesc *.xml")])
        if path:
            self.file_paths[index] = path
            self.lbl_statuses[index].config(text=os.path.basename(path), fg='#00ffaa')

    def load_knob_art(self):
        path = filedialog.askopenfilename(filetypes=[("PNG Image", "*.png")])
        if path:
            self.knob_strip_path = path
            self.lbl_art_status.config(text=os.path.basename(path), fg='#00ffaa')

    def compile_vst_package(self):
        # Validation checks
        if not self.file_paths[0] or not self.file_paths[1]:
            messagebox.showerror("merj Error", "You must load at least Layout A and Layout B.")
            return
        if not self.knob_strip_path:
            messagebox.showerror("merj Error", "Please upload your custom filmstrip artwork file.")
            return
        
        vst_name = self.entry_name.get().strip()
        if len(vst_name) != 9:
            messagebox.showerror("merj Error", "To avoid internal byte shifts, the plugin name must be exactly 9 characters long.")
            return

        macro_tags = self.entry_macro_ids.get().strip()

        # Check for our template file template block
        if not os.path.exists("base_engine.vst3"):
            messagebox.showerror("merj Error", "Template engine not found. Please place 'base_engine.vst3' in the script folder.")
            return

        try:
            # 1. PROCESS TEXT SCHEMAS (Like previous versions of merj)
            with open(self.file_paths[0], 'r', encoding='utf-8') as f:
                master_xml = f.read()

            patched_nodes = []
            for i in range(1, 4):
                if not self.file_paths[i]: continue
                with open(self.file_paths[i], 'r', encoding='utf-8') as f:
                    sub_xml = f.read()
                
                nodes = re.findall(r'(<view\s+class="[^"]+".*?/>)', sub_xml, re.DOTALL)
                shift_x = 160 if (i == 1 or i == 3) else 0
                shift_y = 140 if (i == 2 or i == 3) else 0

                for node in nodes:
                    node = re.sub(r'control-tag="[^"]+"', f'control-tag="{macro_tags}"', node)
                    if 'origin="' in node:
                        coords = re.search(r'origin="(\d+),\s*(\d+)"', node)
                        if coords:
                            node = re.sub(r'origin="\d+,\s*\d+"', f'origin="{int(coords.group(1))+shift_x}, {int(coords.group(2))+shift_y}"', node)
                    patched_nodes.append(node)

            # Injecting the coordinate modifications into the master manifest
            final_views = "\n\t\t".join(patched_nodes)
            modified_uidesc = master_xml.replace("</vstgui-ui-description>", f"\t\t<view class=\"CAnimKnob\" origin=\"0, 0\" size=\"800, 600\" resource-names=\"massive_hell_anim_strip\" control-tag=\"{macro_tags}\" height-of-one-image=\"600\"/>\n\t\t{final_views}\n</vstgui-ui-description>")

            # 2. AUTOMATED DIRECT BINARY PACKAGING
            save_path = filedialog.asksaveasfilename(defaultextension=".vst3", filetypes=[("VST3 Plugin", "*.vst3")])
            if not save_path: return

            # Create the plugin output directory hierarchy bundle
            vst_bundle_dir = save_path if save_path.endswith(".vst3") else save_path + ".vst3"
            binary_target_dir = os.path.join(vst_bundle_dir, "Contents", "x86_64-win")
            resources_target_dir = os.path.join(vst_bundle_dir, "Contents", "Resources")
            os.makedirs(binary_target_dir, exist_ok=True)
            os.makedirs(resources_target_dir, exist_ok=True)

            # Copy the binary base core file over
            target_binary_file = os.path.join(binary_target_dir, os.path.basename(vst_bundle_dir))
            shutil.copyfile("base_engine.vst3", target_binary_file)

            # Write the generated layout file directly into the resources folder
            with open(os.path.join(resources_target_dir, "plugin.uidesc"), 'w', encoding='utf-8') as f:
                f.write(modified_uidesc)

            # Copy your custom SkinMan layout artwork directly into the resources folder
            shutil.copyfile(self.knob_strip_path, os.path.join(resources_target_dir, "massive_hell_anim_strip.png"))

            # 3. DIRECT HEX NAME MODIFICATION
            with open(target_binary_file, 'rb') as f:
                binary_data = f.read()

            # Find and replace the hardcoded core developer metadata text strings
            # Assuming PeakEater as default template framework string
            if b"PeakEater" in binary_data:
                binary_data = binary_data.replace(b"PeakEater", vst_name.encode('utf-8'))
            
            with open(target_binary_file, 'wb') as f:
                f.write(binary_data)

            messagebox.showinfo("merj Complete", f"Success! Standalone Multi-FX compiled.\nSaved to: {vst_bundle_dir}")

        except Exception as e:
            messagebox.showerror("merj Failure", f"An export error occurred: {str(e)}")

if __name__ == "__main__":
    window = tk.Tk()
    app = MerjV5CompilerApp(window)
    window.mainloop()
