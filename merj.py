import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class MerjPluginUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("merj // Open Source Audio Layer Utility")
        self.root.geometry("550x420")
        self.root.configure(bg='#0b0b0f')

        # Custom Dark & Neon Terminal Style Sheet
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TButton', background='#00ffaa', foreground='#000000', font=('Consolas', 10, 'bold'), borderwidth=0)
        self.style.map('TButton', background=[('active', '#00cc88')])

        # Core File Data Buffers
        self.file_a_path = ""
        self.file_b_path = ""

        self.build_merj_interface()

    def build_merj_interface(self):
        # Header Logotype Banner
        title = tk.Label(self.root, text="[ merj // VST3 XML ENGINE ]", bg='#0b0b0f', fg='#00ffaa', font=('Consolas', 14, 'bold'))
        title.pack(pady=20)

        # Module Input Panel A
        frame_a = tk.Frame(self.root, bg='#14141a', bd=1, relief='solid')
        frame_a.pack(fill='x', padx=25, pady=10)
        
        lbl_a = tk.Label(frame_a, text="Source Engine A (.uidesc / .xml):", bg='#14141a', fg='#888899', font=('Consolas', 10))
        lbl_a.pack(anchor='w', padx=15, pady=5)
        
        self.btn_load_a = ttk.Button(frame_a, text="LOAD CORE A", command=self.fetch_layout_a)
        self.btn_load_a.pack(side='left', padx=15, pady=8)
        
        self.lbl_status_a = tk.Label(frame_a, text="unlinked //", bg='#14141a', fg='#555566', font=('Consolas', 9, 'italic'))
        self.lbl_status_a.pack(side='left', padx=10, pady=8)

        # Module Input Panel B
        frame_b = tk.Frame(self.root, bg='#14141a', bd=1, relief='solid')
        frame_b.pack(fill='x', padx=25, pady=10)
        
        lbl_b = tk.Label(frame_b, text="Source Engine B (.uidesc / .xml):", bg='#14141a', fg='#888899', font=('Consolas', 10))
        lbl_b.pack(anchor='w', padx=15, pady=5)
        
        self.btn_load_b = ttk.Button(frame_b, text="LOAD CORE B", command=self.fetch_layout_b)
        self.btn_load_b.pack(side='left', padx=15, pady=8)
        
        self.lbl_status_b = tk.Label(frame_b, text="unlinked //", bg='#14141a', fg='#555566', font=('Consolas', 9, 'italic'))
        self.lbl_status_b.pack(side='left', padx=10, pady=8)

        # Routing Configurations Script Form
        frame_macro = tk.Frame(self.root, bg='#0b0b0f')
        frame_macro.pack(fill='x', padx=25, pady=15)
        
        lbl_macro = tk.Label(frame_macro, text="Bind Macro Sliders (Target Params Mapping IDs):", bg='#0b0b0f', fg='#ffffff', font=('Consolas', 10, 'bold'))
        lbl_macro.pack(anchor='w', pady=5)
        
        self.entry_macro_ids = tk.Entry(frame_macro, bg='#14141a', fg='#00ffaa', insertbackground='white', font=('Consolas', 11), bd=1, relief='solid')
        self.entry_macro_ids.insert(0, "0,1") # Hooks first parameters together inside memory mapping arrays
        self.entry_macro_ids.pack(fill='x', ipady=4, pady=2)

        # Master Process Trigger
        self.btn_merge = tk.Button(self.root, text="COMPILE & MERJ ARCHITECTURES", bg='#ffffff', fg='#000000', font=('Consolas', 11, 'bold'), command=self.process_merj_matrix, activebackground='#dddddd', borderwidth=0)
        self.btn_merge.pack(fill='x', padx=25, ipady=10, pady=15)

    def fetch_layout_a(self):
        path = filedialog.askopenfilename(filetypes=[("UI Description manifests", "*.uidesc *.xml"), ("All Files", "*.*")])
        if path:
            self.file_a_path = path
            self.lbl_status_a.config(text=f"linked // {os.path.basename(path)}", fg='#00ffaa')

    def fetch_layout_b(self):
        path = filedialog.askopenfilename(filetypes=[("UI Description manifests", "*.uidesc *.xml"), ("All Files", "*.*")])
        if path:
            self.file_b_path = path
            self.lbl_status_b.config(text=f"linked // {os.path.basename(path)}", fg='#00ffaa')

    def process_merj_matrix(self):
        if not self.file_a_path or not self.file_b_path:
            messagebox.showerror("merj // Error", "Execution aborted. Missing structural source directory anchors.")
            return

        macro_tags = self.entry_macro_ids.get().strip()
        if not macro_tags:
            messagebox.showerror("merj // Error", "Execution aborted. Multi-mapping control parameters field is empty.")
            return

        try:
            # 1. Digest raw structural files data strings
            with open(self.file_a_path, 'r', encoding='utf-8') as f:
                data_stream_a = f.read()
            with open(self.file_b_path, 'r', encoding='utf-8') as f:
                data_stream_b = f.read()

            # 2. Extract layout component grid lists via regular expressions matching tags
            view_nodes_b = re.findall(r'(<view\s+class="[^"]+".*?/>)', data_stream_b, re.DOTALL)

            if not view_nodes_b:
                messagebox.showerror("merj // Fail", "Failed to resolve control nodes within targeted schema B file.")
                return

            # 3. Patch attributes strings dynamically to inject single control variables paths
            patched_elements_b = []
            for node in view_nodes_b:
                # Force standard parameter routing over original tags
                new_node = re.sub(r'control-tag="[^"]+"', f'control-tag="{macro_tags}"', node)
                
                # Canvas alignment coordinate transformation shifting layout objects rightward
                if 'origin="' in new_node:
                    coords = re.search(r'origin="(\d+),\s*(\d+)"', new_node)
                    if coords:
                        shifted_x = int(coords.group(1)) + 150 # Shifting 150 pixels on visual canvas grid
                        new_node = re.sub(r'origin="\d+,\s*\d+"', f'origin="{shifted_x}, {coords.group(2)}"', new_node)
                patched_elements_b.append(new_node)

            # 4. Splice compiled strings into parent XML structure node configurations
            final_stitched_views = "\n\t\t".join(patched_elements_b)
            
            if "</vstgui-ui-description>" in data_stream_a:
                output_payload = data_stream_a.replace("</vstgui-ui-description>", f"\t\t{final_stitched_views}\n</vstgui-ui-description>")
            elif "</template>" in data_stream_a:
                output_payload = data_stream_a.replace("</template>", f"\t\t{final_stitched_views}\n</template>")
            else:
                output_payload = data_stream_a + f"\n<!-- merj automated sequence block -->\n{final_stitched_views}"

            # 5. Export out your finished standalone manifest sheet map layout
            target_save_name = filedialog.asksaveasfilename(defaultextension=".uidesc", filetypes=[("UI Description map", "*.uidesc"), ("XML code sheet", "*.xml")])
            if target_save_name:
                with open(target_save_name, 'w', encoding='utf-8') as f:
                    f.write(output_payload)
                messagebox.showinfo("merj // Complete", "Compilation matrix successfully executed! Use Resource Hacker to write this back into your host data slot directory bundle.")

        except Exception as e:
            messagebox.showerror("merj // Mainframe Fault", f"System thread crash encountered: {str(e)}")

if __name__ == "__main__":
    window = tk.Tk()
    app = MerjPluginUtilityApp(window)
    window.mainloop()
