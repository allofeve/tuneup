import customtkinter as ctk
import os
import shutil
import ctypes
import subprocess
import json
import threading 
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TuneUpApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Windows & Browser Optimizer Pro")
        self.geometry("1024x800") # ขยายความสูงเล็กน้อยเพื่อรองรับปุ่มใหม่

        self.label = ctk.CTkLabel(self, text="โปรแกรมช่วยให้คอมพิวเตอร์ทำงานได้ไวขึ้น", font=("Kanit", 22, "bold"))
        self.label.pack(pady=20)

        # --- เพิ่มปุ่มพิเศษ All-in-One ไว้ด้านบนสุด ---
        self.create_button("🚀 คลิกเดียว... ปรับแต่งครบทุกฟังก์ชัน (All-in-One)", self.optimize_all_in_one, "#f1c40f")
        
        # เส้นคั่นโซนเพื่อความสวยงาม
        separator = ctk.CTkLabel(self, text="----------------------------------------------------------------------", text_color="gray")
        separator.pack(pady=5)

        # ปุ่มเมนูแยกทำงานทีละอย่าง (คงไว้เหมือนเดิม)
        self.create_button("1. ล้างไฟล์ขยะระบบ (Clean Temp)", self.optimize_files, "#3498db")
        self.create_button("2. ปิด Services & Windows Update", self.disable_services, "#e67e22")
        self.create_button("3. ปิด & ลบอัปเดต Firefox Developer", self.manage_firefox, "#e74c3c")
        self.create_button("4. ปิด & ลบไฟล์ไม่จำเป็นอื่นๆ", self.optimize_system_extra, "#18a134")
        self.create_button("5. เรียกคืนแรม & ปิดโปรแกรมส่วนเกิน", self.optimize_ram_and_processes, "#9b59b6")

        # Progress Bar และ Label แจ้งสถานะ
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0) 
        self.progress_bar.pack(pady=15)

        self.status_label = ctk.CTkLabel(self, text="สถานะ: พร้อมใช้งาน", font=("Kanit", 14), text_color="gray")
        self.status_label.pack(pady=10)

    def start_thread(self, target_func):
        thread = threading.Thread(target=target_func)
        thread.daemon = True 
        thread.start()
    
    def create_button(self, text, command, color):
        btn = ctk.CTkButton(self, text=text, command=lambda: self.start_thread(command), fg_color=color, height=40, font=("Kanit", 14))
        btn.pack(pady=8, fill="x", padx=100)

    def run_command(self, command):
        """ช่วยรันคำสั่ง CMD แบบเบื้องหลัง"""
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
            return True
        except:
            return False

    # ==========================================
    # ฟังก์ชันใหม่: รันทุกอย่างในปุ่มเดียว
    # ==========================================
    def optimize_all_in_one(self):
        self.status_label.configure(text="เริ่มการปรับแต่งระบบแบบ All-in-One...", text_color="#f1c40f")
        self.progress_bar.set(0)
        
        # ฟังก์ชันทั้งหมดที่จะรันเรียงลำดับ (ย้าย logic หลักไปไว้ใน helper เพื่อไม่ให้ขัดแย้งกับ UI thread)
        tasks = [
            ("กำลังล้างไฟล์ขยะระบบ...", self.run_optimize_files),
            ("กำลังปิด Services ที่ไม่จำเป็น...", self.run_disable_services),
            ("กำลังจัดการ Firefox Developer...", self.run_manage_firefox),
            ("กำลังดำเนินการขั้นสูง (ลบ OneDrive/จัด Startup)...", self.run_optimize_system_extra),
            ("กำลังคืนพื้นที่แรมและปิดโปรแกรมส่วนเกิน...", self.run_optimize_ram_and_processes)
        ]
        
        total_tasks = len(tasks)
        
        for index, (status_text, task_func) in enumerate(tasks):
            # อัปเดตข้อความสถานะในแต่ละขั้นตอนหลัก
            self.status_label.configure(text=f"[ขั้นตอนที่ {index+1}/{total_tasks}] {status_text}", text_color="yellow")
            
            # รันฟังก์ชันย่อย (คำนวณเบื้องหลัง)
            task_func()
            
            # อัปเดต Progress Bar หลักตามสัดส่วนงานที่ทำเสร็จ
            self.progress_bar.set((index + 1) / total_tasks)
            
        self.status_label.configure(text="🎉 ปรับแต่งระบบ All-in-One เสร็จสิ้นสมบูรณ์ทุกขั้นตอน!", text_color="#2ecc71")

    # ==========================================
    # แยกส่วนการคำนวณ (Business Logic) ออกมาเพื่อให้เรียกใช้ได้ทั้งแบบแยกปุ่มและแบบรวมปุ่ม
    # ==========================================
    def run_optimize_files(self):
        folders = [os.environ.get('TEMP'), r'C:\Windows\Temp', r'C:\Windows\Prefetch']
        for f in folders:
            if os.path.exists(f):
                try:
                    for item in os.listdir(f):
                        path = os.path.join(f, item)
                        if os.path.isfile(path): os.unlink(path)
                        else: shutil.rmtree(path)
                except: continue

    def optimize_files(self):
        self.status_label.configure(text="กำลังลบไฟล์ขยะ...", text_color="yellow")
        self.progress_bar.set(0.3)
        self.run_optimize_files()
        self.progress_bar.set(1.0)
        self.status_label.configure(text="ลบไฟล์ขยะระบบเรียบร้อยแล้ว", text_color="#2ecc71")

    def run_disable_services(self):
        services_to_disable = ["wuauserv", "bits", "SysMain", "TabletInputService", "WSearch"]
        for svc in services_to_disable:
            self.run_command(f"sc stop {svc}")
            self.run_command(f"sc config {svc} start= disabled")

    def disable_services(self):
        self.status_label.configure(text="กำลังปิดบริการที่ไม่จำเป็น...", text_color="yellow")
        self.progress_bar.set(0.3)
        self.run_disable_services()
        self.progress_bar.set(1.0)
        self.status_label.configure(text="ปิดบริการที่ไม่จำเป็นเรียบร้อย", text_color="#2ecc71")

    def run_manage_firefox(self):
        try:
            ff_path = r"C:\Program Files\Firefox Developer Edition"
            policy_path = os.path.join(ff_path, "distribution")
            if not os.path.exists(policy_path): os.makedirs(policy_path)
            
            policy_data = {"policies": {"DisableAppUpdate": True}}
            with open(os.path.join(policy_path, "policies.json"), "w") as f:
                json.dump(policy_data, f, indent=4)

            ff_updates = os.path.join(os.environ.get('LOCALAPPDATA'), "Mozilla", "updates")
            if os.path.exists(ff_updates):
                shutil.rmtree(ff_updates)
                os.makedirs(ff_updates)
        except: pass

    def manage_firefox(self):
        self.status_label.configure(text="กำลังจัดการ Firefox Developer Edition...", text_color="yellow")
        self.progress_bar.set(0.5)
        self.run_manage_firefox()
        self.progress_bar.set(1.0)
        self.status_label.configure(text="จัดการ Firefox สำเร็จ!", text_color="#2ecc71")

    def run_optimize_system_extra(self):
        self.run_command('schtasks /change /tn "\\Microsoft\\Windows\\Defrag\\ScheduledDefrag" /disable')
        self.run_command('reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 1 /f')
        self.run_command('sc config TermService start= disabled')
        self.run_command('sc stop TermService')

        self.run_command("taskkill /f /im OneDrive.exe")
        if os.path.exists(r"C:\Windows\System32\OneDriveSetup.exe"):
            self.run_command(r"C:\Windows\System32\OneDriveSetup.exe /uninstall")
        elif os.path.exists(r"C:\Windows\SysWOW64\OneDriveSetup.exe"):
            self.run_command(r"C:\Windows\SysWOW64\OneDriveSetup.exe /uninstall")

        startup_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
        ]
        for path in startup_paths:
            self.run_command(f'reg delete "HKEY_LOCAL_MACHINE\\{path}" /va /f')
            self.run_command(f'reg delete "HKEY_CURRENT_USER\\{path}" /va /f')

        self.run_command("dism /online /cleanup-image /startcomponentcleanup /resetbase")

    def optimize_system_extra(self):
        self.status_label.configure(text="กำลังดำเนินการขั้นสูง (อาจใช้เวลาหลายนาที)...", text_color="yellow")
        self.progress_bar.set(0.3)
        self.run_optimize_system_extra()
        self.progress_bar.set(1.0)
        self.status_label.configure(text="ดำเนินการขั้นสูงเสร็จสิ้น!", text_color="#2ecc71")

    def run_optimize_ram_and_processes(self):
        apps_to_kill = ["AnyDesk.exe", "TeamViewer.exe", "msedge.exe", "skype.exe", "discord.exe"]
        for app in apps_to_kill:
            self.run_command(f"taskkill /F /IM {app} /T")
        
        ps_command = (
            "powershell -command \"$processes = Get-Process; "
            "foreach($proc in $processes) { "
            "  try { "
            "    $proc.MaxWorkingSet = $proc.MinWorkingSet; "
            "  } catch {} "
            "}\""
        )
        self.run_command(ps_command)

    def optimize_ram_and_processes(self):
        self.status_label.configure(text="กำลังเพิ่มพื้นที่แรมและปิด Process...", text_color="yellow")
        self.progress_bar.set(0.5)
        self.run_optimize_ram_and_processes()
        self.progress_bar.set(1.0)
        self.status_label.configure(text="เพิ่มแรมและปิดโปรแกรมส่วนเกินสำเร็จ!", text_color="#2ecc71")

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        app = TuneUpApp()
        app.mainloop()
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)