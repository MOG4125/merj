import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class OpenSourcePluginMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("No-Code Open Source Plugin Merger")
        self.root.geometry("550x420")
        self.root.configure(bg='#141419')

        # Custom Dark/Neon Theme Styles
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TButton', background='#00ffaa', foreground='#000000', font=('Arial', 10, 'bold'), borderwidth=0)
        self.style.map('TButton', background=[('active', '#00cc88')])

        # Data Trackers
        self.uidesc_a_path = ""
        self.uidesc_b_path = ""

        self.create_ui_layout()

    def create_ui_layout(self):
        # Header Title
        title = tk.Label(self.root, text="VST3 XML / UIDESC MERGER", bg='#141419', fg='#00ffaa', font=('Arial', 14, 'bold'))
        title.pack(pady=15)

        # File Selection Frame A
        frame_a = tk.Frame(self.root, bg='#1c1c24', bd=2, relief='groove')
        frame_a.pack(fill='x', padx=20, pady=10)
        
        lbl_a = tk.Label(frame_a, text="Plugin A Layout (.uidesc / .xml):", bg='#1c1c24', fg='#ffffff')
        lbl_a.pack(anchor='w', padx=10, pady=5)
        
        self.btn_load_a = ttk.Button(frame_a, text="Browse Plugin A", command=self.load_file_a)
        self.btn_load_a.pack(side='left', padx=10, pady=5)
        
        self.lbl_status_a = tk.Label(frame_a, text="No file loaded", bg='#1c1c24', fg='#888888', font=('Arial', 9, 'italic'))
        self.lbl_status_a.pack(side='left', padx=10, pady=5)

        # File Selection Frame B
        frame_b = tk.Frame(self.root, bg='#1c1c24', bd=2, relief='groove')
        frame_b.pack(fill='x', padx=20, pady=10)
        
        lbl_b = tk.Label(frame_b, text="Plugin B Layout (.uidesc / .xml):", bg='#1c1c24', fg='#ffffff')
        lbl_b.pack(anchor='w', padx=10, pady=5)
        
        self.btn_load_b = ttk.Button(frame_b, text="Browse Plugin B", command=self.load_file_b)
        self.btn_load_b.pack(side='left', padx=10, pady=5)
        
        self.lbl_status_b = tk.Label(frame_b, text="No file loaded", bg='#1c1c24', fg='#888888', font=('Arial', 9, 'italic'))
        self.lbl_status_b.pack(side='left', padx=10, pady=5)

        # Macro Controls Configuration Settings Panel
        frame_macro = tk.Frame(self.root, bg='#141419')
        frame_macro.pack(fill='x', padx=20, pady=15)
        
        lbl_macro = tk.Label(frame_macro, text="Link Single Macro Control Tag to IDs:", bg='#141419', fg='#ffffff', font=('Arial', 10, 'bold'))
        lbl_macro.pack(anchor='w', pady=5)
        
        self.entry_macro_ids = tk.Entry(frame_macro, bg='#2a2a35', fg='#ffffff', insertbackground='white', font=('Arial', 10))
        self.entry_macro_ids.insert(0, "0,1") # Default maps first parameter of each plugin together
        self.entry_macro_ids.pack(fill='x', pady=2)

        # Execution Processing Button
        self.btn_merge = tk.Button(self.root, text="⚡ MERGE PLUGIN ARCHITECTURES", bg='#ffffff', fg='#000000', font=('Arial', 11, 'bold'), command=self.execute_resource_merge, activebackground='#eeeeee')
        self.btn_merge.pack(fill='x', padx=20, pady=20)

    def load_file_a(self):
        path = filedialog.askopenfilename(filetypes=[("UI Description files", "*.uidesc *.xml"), ("All Files", "*.*")])
        if path:
            self.uidesc_a_path = path
            self.lbl_status_a.config(text=os.path.basename(path), fg='#00ffaa')

    def load_file_b(self):
        path = filedialog.askopenfilename(filetypes=[("UI Description files", "*.uidesc *.xml"), ("All Files", "*.*")])
        if path:
            self.uidesc_b_path = path
            self.lbl_status_b.config(text=os.path.basename(path), fg='#00ffaa')

    def execute_resource_merge(self):
        if not self.uidesc_a_path or not self.uidesc_b_path:
            messagebox.showerror("Error", "Please make sure to select layout files for both Plugin A and Plugin B.")
            return

        macro_tags = self.entry_macro_ids.get().strip()
        if not macro_tags:
            messagebox.showerror("Error", "Please input target parameter tracking control tags.")
            return

        try:
            # 1. Read open source textual XML data blocks
            with open(self.uidesc_a_path, 'r', encoding='utf-8') as f:
                content_a = f.read()
            with open(self.uidesc_b_path, 'r', encoding='utf-8') as f:
                content_b = f.read()

            # 2. Extract underlying visual components (<view> blocks) from Plugin B
            # This extracts individual knob/slider elements out of file B
            view_elements_b = re.findall(r'(<view\s+class="[^"]+".*?/>)', content_b, re.DOTALL)

            if not view_elements_b:
                messagebox.showerror("Parsing Failure", "Could not locate valid UI template views inside Plugin B.")
                return

            # 3. Modify extracted components to listen to the new single macro parameter control tag
            modified_views_b = []
            for element in view_elements_b:
                # Forcefully overwrite control tag parameters inside the code string
                new_element = re.sub(r'control-tag="[^"]+"', f'control-tag="{macro_tags}"', element)
                # Offset positions so controls from plugin B don't stack directly on top of plugin A
                if 'origin="' in new_element:
                    coords = re.search(r'origin="(\d+),\s*(\d+)"', new_element)
                    if coords:
                        new_x = int(coords.group(1)) + 150 # Shift 150 pixels right
                        new_element = re.sub(r'origin="\d+,\s*\d+"', f'origin="{new_x}, {coords.group(2)}"', new_element)
                modified_views_b.append(new_element)

            # 4. Inject the combined macro view elements straight into Plugin A's layout tree
            merged_views_string = "\n\t\t".join(modified_views_b)
            
            # Find the closing structural container tag inside target A
            if "</vstgui-ui-description>" in content_a:
                output_content = content_a.replace("</vstgui-ui-description>", f"\t\t{merged_views_string}\n</vstgui-ui-description>")
            elif "</template>" in content_a:
                output_content = content_a.replace("</template>", f"\t\t{merged_views_string}\n</template>")
            else:
                output_content = content_a + f"\n<!-- Merged Modules -->\n{merged_views_string}"

            # 5. Prompt to write the final unified manifest layout patch out to disk
            save_path = filedialog.asksaveasfilename(defaultextension=".uidesc", filetypes=[("UI Description file", "*.uidesc"), ("XML file", "*.xml")])
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                messagebox.showinfo("Success!", "Plugin XML layout files merged successfully! Open your host plugin container in Resource Hacker and inject this file into the DATA/XML directory slot.")

        except Exception as e:
            messagebox.showerror("Processing Error", f"An unexpected system exception occurred: {str(e)}")

if __name__ == "__main__":
    window = tk.Tk()
    app = OpenSourcePluginMergerApp(window)
    window.mainloop()
