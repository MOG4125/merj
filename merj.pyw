import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class MerjFourSlotUtilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("merj v4.0 // Quad Engine Audio Core Grid Utility")
        self.root.geometry("600x520")
        self.root.configure(bg='#0b0b0f')

        # Custom Dark & Neon Terminal Style Sheet
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TButton', background='#00ffaa', foreground='#000000', font=('Consolas', 10, 'bold'), borderwidth=0)
        self.style.map('TButton', background=[('active', '#00cc88')])

        # Core File Data Buffers for 4 Slots
        self.file_paths = ["", "", "", ""]
        self.lbl_statuses = []

        self.build_merj_interface()

    def build_merj_interface(self):
        # Header Logotype Banner
        title = tk.Label(self.root, text="[ merj v4.0 // QUAD ENGINE XML MERGER ]", bg='#0b0b0f', fg='#00ffaa', font=('Consolas', 13, 'bold'))
        title.pack(pady=15)

        # Generate 4 File Selection Slots Automatically
        slot_letters = ['A', 'B', 'C', 'D']
        for i in range(4):
            frame = tk.Frame(self.root, bg='#14141a', bd=1, relief='solid')
            frame.pack(fill='x', padx=25, pady=6)
            
            lbl = tk.Label(frame, text=f"Source Engine {slot_letters[i]} (.uidesc / .xml):", bg='#14141a', fg='#888899', font=('Consolas', 9))
            lbl.pack(anchor='w', padx=15, pady=2)
            
            # Using a default argument to pin the current iteration index in memory loop
            btn = ttk.Button(frame, text=f"LOAD ENGINE {slot_letters[i]}", command=lambda idx=i: self.fetch_layout_file(idx))
            btn.pack(side='left', padx=15, pady=6)
            
            lbl_status = tk.Label(frame, text="unlinked // optional slot" if i > 1 else "unlinked // required slot", bg='#14141a', fg='#555566', font=('Consolas', 9, 'italic'))
            lbl_status.pack(side='left', padx=10, pady=6)
            self.lbl_statuses.append(lbl_status)

        # Routing Configurations Script Form
        frame_macro = tk.Frame(self.root, bg='#0b0b0f')
        frame_macro.pack(fill='x', padx=25, pady=10)
        
        lbl_macro = tk.Label(frame_macro, text="Bind Macro Sliders (Target Params Mapping IDs):", bg='#0b0b0f', fg='#ffffff', font=('Consolas', 10, 'bold'))
        lbl_macro.pack(anchor='w', pady=3)
        
        self.entry_macro_ids = tk.Entry(frame_macro, bg='#14141a', fg='#00ffaa', insertbackground='white', font=('Consolas', 11), bd=1, relief='solid')
        self.entry_macro_ids.insert(0, "0,1,2,3") # Hooks up to four parameter slots across system tracking matrix array
        self.entry_macro_ids.pack(fill='x', ipady=4, pady=2)

        # Master Process Trigger
        self.btn_merge = tk.Button(self.root, text="COMPILE & MERJ ALL ENGINE LAYOUTS", bg='#ffffff', fg='#000000', font=('Consolas', 11, 'bold'), command=self.process_quad_merj, activebackground='#dddddd', borderwidth=0)
        self.btn_merge.pack(fill='x', padx=25, ipady=10, pady=15)

    def fetch_layout_file(self, index):
        path = filedialog.askopenfilename(filetypes=[("UI Description manifests", "*.uidesc *.xml"), ("All Files", "*.*")])
        if path:
            self.file_paths[index] = path
            self.lbl_statuses[index].config(text=f"linked // {os.path.basename(path)}", fg='#00ffaa')

    def process_quad_merj(self):
        # Validation: We need at least the first two slots occupied to execute a merge
        if not self.file_paths[0] or not self.file_paths[1]:
            messagebox.showerror("merj // Error", "Execution aborted. You must load at least Engine A and Engine B to merge.")
            return

        macro_tags = self.entry_macro_ids.get().strip()
        if not macro_tags:
            messagebox.showerror("merj // Error", "Execution aborted. Multi-mapping control parameters field is empty.")
            return

        try:
            # 1. Start with Engine A as the baseline structural shell canvas
            with open(self.file_paths[0], 'r', encoding='utf-8') as f:
                master_payload = f.read()

            all_patched_nodes = []

            # 2. Iterate through secondary plugin slots (B, C, and D) dynamically
            for i in range(1, 4):
                current_path = self.file_paths[i]
                if not current_path:
                    continue # Skip empty optional slots seamlessly

                with open(current_path, 'r', encoding='utf-8') as f:
                    data_stream = f.read()

                # Find layout controls inside the loaded code string
                view_nodes = re.findall(r'(<view\s+class="[^"]+".*?/>)', data_stream, re.DOTALL)
                
                # Smart 2x2 Grid Offsetting Rule Calculations:
                # Slot B (Index 1) -> Shifts 160px Right
                # Slot C (Index 2) -> Shifts 140px Down
                # Slot D (Index 3) -> Shifts 160px Right AND 140px Down
                shift_x = 160 if (i == 1 or i == 3) else 0
                shift_y = 140 if (i == 2 or i == 3) else 0

                for node in view_nodes:
                    # Inject our multi-mapped control parameters parameter
                    new_node = re.sub(r'control-tag="[^"]+"', f'control-tag="{macro_tags}"', node)
                    
                    # Coordinate transform manipulation
                    if 'origin="' in new_node:
                        coords = re.search(r'origin="(\d+),\s*(\d+)"', new_node)
                        if coords:
                            new_x = int(coords.group(1)) + shift_x
                            new_y = int(coords.group(2)) + shift_y
                            new_node = re.sub(r'origin="\d+,\s*\d+"', f'origin="{new_x}, {new_y}"', new_node)
                    all_patched_nodes.append(new_node)

            # 3. Stitch the grid of components together
            final_stitched_views = "\n\t\t".join(all_patched_nodes)
            
            # Splicing into the XML root structure tags of Engine A
            if "</vstgui-ui-description>" in master_payload:
                output_payload = master_payload.replace("</vstgui-ui-description>", f"\t\t{final_stitched_views}\n</vstgui-ui-description>")
            elif "</template>" in master_payload:
                output_payload = master_payload.replace("</template>", f"\t\t{final_stitched_views}\n</template>")
            else:
                output_payload = master_payload + f"\n<!-- merj quad grid system block -->\n{final_stitched_views}"

            # 4. Export out your massive 4-plugin manifest sheet canvas layout map
            target_save_name = filedialog.asksaveasfilename(defaultextension=".uidesc", filetypes=[("UI Description map", "*.uidesc"), ("XML code sheet", "*.xml")])
            if target_save_name:
                with open(target_save_name, 'w', encoding='utf-8') as f:
                    f.write(output_payload)
                messagebox.showinfo("merj // Complete", "Quad Compilation successfully executed! Use Resource Hacker to write this back into your host data slot directory bundle.")

        except Exception as e:
            messagebox.showerror("merj // Mainframe Fault", f"System thread crash encountered: {str(e)}")

if __name__ == "__main__":
    window = tk.Tk()
    app = MerjFourSlotUtilityApp(window)
    window.mainloop()
