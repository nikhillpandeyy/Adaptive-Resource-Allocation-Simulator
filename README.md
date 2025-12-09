# Adaptive Resource Allocation Simulator

This project is a real-time operating system simulation that demonstrates how CPU and memory resources are allocated to multiple processes in a multiprogramming environment.

The simulator dynamically adjusts the state of each process (Ready, Running, Waiting, Completed) based on available system resources. A Tkinter-based GUI provides a live visualization of:
- CPU allocation
- Memory allocation
- Execution progress bars
- Process states and scheduling queue

---

## 🚀 Features

- Real-time CPU and memory scheduling
- Total memory capped at 2048 MB and CPU at 100%
- Add / Delete / Reset processes dynamically
- Live progress bars for each active process
- Automatic state transition of processes
- Clean and intuitive graphical interface

---

## 📦 Technology Stack

| Component | Technology |
|----------|-------------|
| Language | Python |
| GUI Library | Tkinter |
| System Monitoring | psutil |
| OS Concept | Multiprogramming / Resource Allocation |

---

## 📂 Project File Structure

```
Adaptive-Resource-Allocation-Simulator/
│── project.py      ← Main source code
│── README.md       ← Documentation
│── requirements.txt← Dependencies
└── screenshots/    ← GUI screenshots for demonstration
```

---

## 🖥️ How to Run

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Run the simulator
```bash
python project.py
```

---

## 📝 Output Preview

| Visualization | Description |
|--------------|-------------|
| CPU & Memory Bars | Live system consumption |
| Progress Bars | Execution speed per process |
| Process Table | State, resources, and progress |
| Buttons | Add / Delete / Reset process |

(Insert screenshots here — optional)
```
![Simulator Running](screenshots/ss1.png)
![Multiple Processes](screenshots/ss2.png)
```

---

## 🎯 Learning Outcome

This project helps understand:
- OS resource allocation
- Process scheduling and memory management
- Concurrency in multiprogramming systems
- Event-driven simulation through GUI

---

## 🔮 Future Enhancements

- Priority scheduling
- Round Robin CPU scheduling
- Dark mode theme
- Export logs to CSV
- Pause / resume processes

---

## 📄 License

This project is open-source and free to use for academic purposes.
<img width="1920" height="1020" alt="Screenshot 2025-12-10 002309" src="https://github.com/user-attachments/assets/b4d9cb17-454a-4c08-99fe-cd6a3eadb7dd" />
<img width="1920" height="1020" alt="Screenshot 2025-12-10 002303" src="https://github.com/user-attachments/assets/e8dad908-6b7e-4d79-a95a-80149579b433" />
<img width="1920" height="1020" alt="Screenshot 2025-12-10 002228" src="https://github.com/user-attachments/assets/3724c901-feb7-4be7-8521-54331de0ab83" />
