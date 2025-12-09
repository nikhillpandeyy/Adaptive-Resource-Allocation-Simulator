"""
Adaptive Resource Allocation Simulator — Realistic Multiprogramming
- Processes can be Ready, Waiting, Running, Completed
- CPU allocation capped at 100%, memory limited to 2048 MB
- Black execution progress bars
- Fully working Add / Delete / Reset
- Execution speed boosted ~1.5x
Requires: psutil
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# -------------------------
# Process class
# -------------------------
class Process:
    def __init__(self, pid, name, cpu_request, mem_request):
        self.pid = pid
        self.name = name
        self.cpu_request = float(cpu_request)  # requested CPU %
        self.mem_request = float(mem_request)  # requested memory MB
        self.progress = 0.0                    # execution completion %
        self.state = "Ready"                   # Ready / Waiting / Running / Completed
        self.progressbar = None

# -------------------------
# GUI / Scheduler
# -------------------------
class ResourceSchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Adaptive Resource Allocation Simulator v1.0")   # updated title
        self.root.geometry("980x800")
        self.root.resizable(True, True)

        # Data
        self.processes = {}         # pid -> Process
        self.process_lock = threading.Lock()
        self.next_pid = 1001
        self.next_proc_index = 1

        # Control
        self.updating = True

        # Simulated memory limit
        self.total_memory_mb = 2048  # cap to 2048 MB

        # Style
        self.style = ttk.Style()
        try:
            self.style.theme_use('default')
        except Exception:
            pass
        self.style.configure("black.Horizontal.TProgressbar", troughcolor='white', background='black')

        # Build UI
        self.create_ui()

        # Start threads
        threading.Thread(target=self.scheduler_loop, daemon=True).start()
        self.update_system_usage()

    # -------------------------
    # UI
    # -------------------------
    def create_ui(self):
        header = tk.Label(self.root, text="Adaptive Resource Allocation Simulator",
                          font=("Segoe UI", 14, "bold"))
        header.pack(pady=10)

        # System usage
        sys_frame = tk.Frame(self.root)
        sys_frame.pack(padx=12, pady=(0,6), fill="x")
        tk.Label(sys_frame, text="CPU Usage (%)", anchor="w").grid(row=0, column=0, sticky="w")
        self.cpu_bar = ttk.Progressbar(sys_frame, length=600, maximum=100)
        self.cpu_bar.grid(row=0, column=1, padx=8, sticky="w")
        self.cpu_percent_label = tk.Label(sys_frame, text="0.0 %", width=8)
        self.cpu_percent_label.grid(row=0, column=2, sticky="w")

        tk.Label(sys_frame, text="Memory Usage (%)", anchor="w").grid(row=1, column=0, sticky="w", pady=6)
        self.mem_bar = ttk.Progressbar(sys_frame, length=600, maximum=100)
        self.mem_bar.grid(row=1, column=1, padx=8, sticky="w")
        self.mem_percent_label = tk.Label(sys_frame, text="0.0 %", width=8)
        self.mem_percent_label.grid(row=1, column=2, sticky="w")

        # Table
        table_frame = tk.Frame(self.root)
        table_frame.pack(padx=12, pady=(6,4), fill="both", expand=True)

        columns = ("PID","Name","Requested_CPU","Allocated_CPU","Requested_Mem","Mem_Used","Progress","State")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        headings = ["PID","Process Name","Requested CPU (%)","Allocated CPU (%)","Requested Memory (MB)",
                    "Memory Used (MB)","Execution Progress (%)","State"]
        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head)
        self.tree.column("PID", width=70, anchor="center")
        self.tree.column("Name", width=180, anchor="w")
        self.tree.column("Requested_CPU", width=120, anchor="center")
        self.tree.column("Allocated_CPU", width=120, anchor="center")
        self.tree.column("Requested_Mem", width=120, anchor="center")
        self.tree.column("Mem_Used", width=120, anchor="center")
        self.tree.column("Progress", width=120, anchor="center")
        self.tree.column("State", width=100, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)

        # Progress bars under table
        tk.Label(self.root, text="Execution Progress Bars", font=("Segoe UI", 9)).pack(padx=12, anchor="w")
        self.pb_canvas_frame = tk.Frame(self.root)
        self.pb_canvas_frame.pack(padx=12, pady=(2,6), fill="x")
        self.pb_canvas = tk.Canvas(self.pb_canvas_frame, height=180, highlightthickness=0)
        self.pb_canvas.pack(side="left", fill="both", expand=True)
        self.pb_interior = tk.Frame(self.pb_canvas)
        self.pb_window = self.pb_canvas.create_window((0,0), window=self.pb_interior, anchor="nw")
        vsb.config(command=self._shared_scroll)
        self.pb_interior.bind("<Configure>", lambda e: self.pb_canvas.configure(scrollregion=self.pb_canvas.bbox("all")))
        self.pb_canvas.bind("<Configure>", self._on_canvas_configure)

        # Bottom controls
        bottom_frame = tk.Frame(self.root, relief="groove", bd=1)
        bottom_frame.pack(padx=12, pady=8, fill="x")

        # Name
        name_frame = tk.Frame(bottom_frame)
        name_frame.pack(side="left", padx=6, pady=8)
        tk.Label(name_frame, text="Process Name:").pack(anchor="w")
        self.name_var = tk.StringVar(value=f"Process_{self.next_proc_index}")
        self.name_entry = tk.Entry(name_frame, textvariable=self.name_var, width=22)
        self.name_entry.pack()

        # CPU
        cpu_frame = tk.Frame(bottom_frame)
        cpu_frame.pack(side="left", padx=20)
        tk.Label(cpu_frame, text="Requested CPU (%)").pack(anchor="w")
        self.cpu_slider = tk.Scale(cpu_frame, from_=1, to=100, orient="horizontal", length=250)
        self.cpu_slider.set(10)
        self.cpu_slider.pack()
        self.cpu_slider_label = tk.Label(cpu_frame, text=f"{self.cpu_slider.get():.0f} %")
        self.cpu_slider_label.pack(anchor="w")
        self.cpu_slider.config(command=lambda v: self.cpu_slider_label.config(text=f"{float(v):.0f} %"))

        # Memory
        mem_frame = tk.Frame(bottom_frame)
        mem_frame.pack(side="left", padx=20)
        tk.Label(mem_frame, text="Requested Memory (MB)").pack(anchor="w")
        self.mem_slider = tk.Scale(mem_frame, from_=0, to=2048, orient="horizontal", length=250)
        self.mem_slider.set(256)
        self.mem_slider.pack()
        self.mem_slider_label = tk.Label(mem_frame, text=f"{self.mem_slider.get():.0f} MB")
        self.mem_slider_label.pack(anchor="w")
        self.mem_slider.config(command=lambda v: self.mem_slider_label.config(text=f"{float(v):.0f} MB"))

        # Buttons
        btns_frame = tk.Frame(bottom_frame)
        btns_frame.pack(side="right", padx=6, pady=6)
        tk.Button(btns_frame, text="Add Process", width=14, command=self.add_process).pack(pady=4)
        tk.Button(btns_frame, text="Delete Selected Process", width=20, command=self.delete_selected_process).pack(pady=4)
        tk.Button(btns_frame, text="RESET", width=14, command=self.reset_all).pack(pady=4)

    # -------------------------
    # Scroll
    # -------------------------
    def _shared_scroll(self, *args):
        try: self.tree.yview(*args)
        except: pass
        try: self.pb_canvas.yview(*args)
        except: pass

    def _on_canvas_configure(self, event):
        try: self.pb_canvas.itemconfig(self.pb_window, width=event.width)
        except: pass

    # -------------------------
    # Add process
    # -------------------------
    def add_process(self):
        name = self.name_var.get().strip()
        if not name: messagebox.showwarning("Validation", "Process name cannot be empty."); return
        cpu_req = float(self.cpu_slider.get())
        mem_req = float(self.mem_slider.get())
        with self.process_lock:
            pid = self.next_pid
            self.next_pid += 1
            proc = Process(pid, name, cpu_req, mem_req)
            self.processes[pid] = proc
            iid = str(pid)
            self.tree.insert("", "end", iid=iid,
                             values=(pid,name,f"{cpu_req:.1f}",f"0.0",f"{mem_req:.0f}",f"0.0",f"0.0",proc.state))
            pb = ttk.Progressbar(self.pb_interior, length=900, maximum=100, style="black.Horizontal.TProgressbar")
            pb.pack(pady=3, anchor="w", fill="x")
            proc.progressbar = pb
            self.next_proc_index += 1
            self.name_var.set(f"Process_{self.next_proc_index}")
            self._adjust_pb_canvas_height()

    def _adjust_pb_canvas_height(self):
        count = len(self.processes)
        height = max(30, count*28)
        self.pb_canvas.config(height=min(max(160,height),600))
        self.pb_canvas.configure(scrollregion=self.pb_canvas.bbox("all"))

    # -------------------------
    # Delete
    # -------------------------
    def delete_selected_process(self):
        selected = self.tree.selection()
        if not selected: messagebox.showwarning("No Selection", "Select a process to delete."); return
        iid = selected[0]
        pid = int(self.tree.item(iid,"values")[0])
        with self.process_lock: proc = self.processes.pop(pid,None)
        if proc and proc.progressbar: proc.progressbar.destroy()
        self.tree.delete(iid)

    # -------------------------
    # Reset
    # -------------------------
    def reset_all(self):
        if not messagebox.askyesno("Confirm Reset","This will clear all processes. Continue?"): return
        with self.process_lock:
            self.processes.clear()
        for iid in self.tree.get_children(): self.tree.delete(iid)
        for child in self.pb_interior.winfo_children(): child.destroy()
        self.next_pid = 1001
        self.next_proc_index = 1
        self.name_var.set(f"Process_{self.next_proc_index}")
        self._adjust_pb_canvas_height()

    # -------------------------
    # Scheduler loop
    # -------------------------
    def scheduler_loop(self):
        while True:
            with self.process_lock:
                procs = list(self.processes.values())

            available_cpu = 100.0
            mem_used = 0.0
            ready_queue = []

            # Determine states based on memory
            for p in procs:
                if p.state == "Completed": continue
                if mem_used + p.mem_request > self.total_memory_mb:
                    p.state = "Waiting"
                else:
                    p.state = "Ready"
                    ready_queue.append(p)
                    mem_used += p.mem_request

            # Allocate CPU to Ready processes (respect 100% CPU cap)
            running_procs = []
            cpu_allocated = 0.0
            for p in ready_queue:
                if cpu_allocated + p.cpu_request <= 100.0:
                    p.state = "Running"
                    running_procs.append((p, p.cpu_request))
                    cpu_allocated += p.cpu_request
                else:
                    p.state = "Ready"

            # Update progress (boosted 1.5x)
            scale = 0.05*1.5
            for p, cpu_alloc in running_procs:
                p.progress = min(100.0, p.progress + cpu_alloc*scale)
                if p.progress >= 100.0:
                    p.state = "Completed"

            # Update table rows
            for p in procs:
                mem_display = p.mem_request if p.state in ["Ready","Running"] else 0.0
                alloc_cpu = next((cpu for proc,cpu in running_procs if proc==p),0.0)
                self.root.after(0, self.update_process_row, p, alloc_cpu, mem_display)

            time.sleep(0.45)

    def update_process_row(self,proc,allocated_cpu,mem_used):
        if self.tree.exists(str(proc.pid)):
            self.tree.item(str(proc.pid), values=(
                proc.pid,
                proc.name,
                f"{proc.cpu_request:.1f}",
                f"{allocated_cpu:.1f}",
                f"{proc.mem_request:.0f}",
                f"{mem_used:.0f}",
                f"{proc.progress:.1f}",
                proc.state
            ))
            if proc.progressbar: proc.progressbar['value'] = proc.progress
            color = {"Waiting":"orange","Ready":"yellow","Running":"green","Completed":"gray"}.get(proc.state,"white")
            self.tree.tag_configure(str(proc.pid), background=color)
            self.tree.item(str(proc.pid), tags=(str(proc.pid),))

    # -------------------------
    # System usage
    # -------------------------
    def update_system_usage(self):
        with self.process_lock:
            total_cpu = sum(p.cpu_request for p in self.processes.values() if p.state=="Running")
            total_mem = sum(p.mem_request for p in self.processes.values() if p.state in ["Ready","Running"])
        self.cpu_bar['value'] = min(100.0,total_cpu)
        self.cpu_percent_label.config(text=f"{min(100.0,total_cpu):.1f} %")
        mem_percent = min(100.0,(total_mem/self.total_memory_mb)*100.0)
        self.mem_bar['value'] = mem_percent
        self.mem_percent_label.config(text=f"{mem_percent:.1f} %")
        if self.updating: self.root.after(500,self.update_system_usage)

    # -------------------------
    # Stop
    # -------------------------
    def stop(self): self.updating=False

# -------------------------
# Main
# -------------------------
def main():
    root = tk.Tk()
    app = ResourceSchedulerGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()

if __name__=="__main__":
    main()

