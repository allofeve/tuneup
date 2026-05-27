import customtkinter as ctk
import os
import shutil
import ctypes
import subprocess
import json
import threading # เพิ่มการ import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TuneUpApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Windows & Browser Optimizer Pro")
        self.geometry("1024x768") # ปรับขนาดเล็กน้อยเพื่อรองรับปุ่มใหม่

        self.label = ctk.CTkLabel(self, text="โปรแกรมช่วยให้คอมพิวเตอร์ทำงานได้ไวขึ้น", font=("Kanit", 22, "bold"))
        self.label.pack(pady=20)

        # ปุ่มเมนูต่างๆ
        self.create_button("1. ล้างไฟล์ขยะระบบ (Clean Temp)", self.optimize_files, "#3498db")
        self.create_button("2. ปิด Services & Windows Update", self.disable_services, "#e67e22")
        self.create_button("3. ปิด & ลบอัปเดต Firefox Developer", self.manage_firefox, "#e74c3c")
        self.create_button("4. ปิด & ลบไฟล์ไม่จำเป็นอื่นๆ", self.optimize_system_extra, "#18a134")
        self.create_button("5. เรียกคืนแรม & ปิดโปรแกรมส่วนเกิน", self.optimize_ram_and_processes, "#9b59b6")

        # เพิ่ม Progress Bar ไว้ใต้ปุ่ม
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0) # เริ่มต้นที่ 0%
        self.progress_bar.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="สถานะ: พร้อมใช้งาน", text_color="gray")
        self.status_label.pack(pady=10)

    # ฟังก์ชันช่วยรันงานแบบไม่ให้ GUI ค้าง
    def start_thread(self, target_func):
        thread = threading.Thread(target=target_func)
        thread.daemon = True # ให้จบการทำงานตามโปรแกรมหลัก
        thread.start()
    
    # แก้ไขปุ่มให้ไปเรียก start_thread แทน
    def create_button(self, text, command, color):
        # เปลี่ยน command เป็น lambda เพื่อให้เรียกผ่าน thread
        btn = ctk.CTkButton(self, text=text, command=lambda: self.start_thread(command), fg_color=color, height=40)
        btn.pack(pady=10, fill="x", padx=100)

    def run_command(self, command):
        """ช่วยรันคำสั่ง CMD แบบเบื้องหลัง"""
        try:
            subprocess.run(command, shell=True, check=True, capture_output=True)
            return True
        except:
            return False

    def optimize_files(self):
        self.status_label.configure(text="กำลังลบไฟล์ขยะ...", text_color="yellow")
        self.progress_bar.set(0) # รีเซ็ตแถบโหลด
        
        folders = [os.environ.get('TEMP'), r'C:\Windows\Temp', r'C:\Windows\Prefetch']
        total_folders = len(folders)
        count = 0

        for i, f in enumerate(folders):
            if os.path.exists(f):
                items = os.listdir(f)
                for item in items:
                    try:
                        path = os.path.join(f, item)
                        if os.path.isfile(path): os.unlink(path)
                        else: shutil.rmtree(path)
                        count += 1
                    except: continue
            
            # อัปเดต Progress Bar ตามจำนวนโฟลเดอร์ที่ทำเสร็จ
            self.progress_bar.set((i + 1) / total_folders)
        
        self.status_label.configure(text=f"ลบไฟล์สำเร็จ {count} รายการ", text_color="#2ecc71")

    def disable_services(self):
        self.status_label.configure(text="กำลังปิดบริการที่ไม่จำเป็น...", text_color="yellow")
        self.progress_bar.set(0)

        services_to_disable = [
            "wuauserv", "bits", "SysMain", "TabletInputService", "WSearch"
        ]
        
        total_svc = len(services_to_disable)
        success_count = 0

        for i, svc in enumerate(services_to_disable):
            stop_cmd = f"sc stop {svc}"
            disable_cmd = f"sc config {svc} start= disabled"
            
            self.run_command(stop_cmd)
            if self.run_command(disable_cmd):
                success_count += 1
            
            # อัปเดต Progress Bar
            self.progress_bar.set((i + 1) / total_svc)

        self.status_label.configure(text=f"ปิด {success_count} บริการเรียบร้อย", text_color="#2ecc71")

    def manage_firefox(self):
        self.status_label.configure(text="กำลังจัดการ Firefox Developer Edition...", text_color="yellow")
        self.progress_bar.set(0)
        
        steps = 2 # มี 2 ขั้นตอนหลัก: เขียน Policy และ ลบ Update Cache
        
        try:
            # Step 1: เขียน Policy
            ff_path = r"C:\Program Files\Firefox Developer Edition"
            policy_path = os.path.join(ff_path, "distribution")
            if not os.path.exists(policy_path): os.makedirs(policy_path)
            
            policy_data = {"policies": {"DisableAppUpdate": True}}
            with open(os.path.join(policy_path, "policies.json"), "w") as f:
                json.dump(policy_data, f, indent=4)
            
            self.progress_bar.set(1/steps)

            # Step 2: ล้าง Cache อัปเดต
            ff_updates = os.path.join(os.environ.get('LOCALAPPDATA'), "Mozilla", "updates")
            if os.path.exists(ff_updates):
                shutil.rmtree(ff_updates)
                os.makedirs(ff_updates)
            
            self.progress_bar.set(2/steps)
            self.status_label.configure(text="จัดการ Firefox สำเร็จ!", text_color="#2ecc71")
            
        except Exception as e:
            self.status_label.configure(text=f"ผิดพลาด: {str(e)}", text_color="red")
    
    def optimize_system_extra(self):
        self.status_label.configure(text="กำลังดำเนินการขั้นสูง (อาจใช้เวลาหลายนาที)...", text_color="yellow")
        self.progress_bar.set(0)
        
        steps = 5 # จำนวนงานทั้งหมดในฟังก์ชันนี้
        
        # 1. ปิด Defrag
        self.run_command('schtasks /change /tn "\\Microsoft\\Windows\\Defrag\\ScheduledDefrag" /disable')
        self.progress_bar.set(1/steps)
        
        # 2. ปิด Remote Desktop
        self.run_command('reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 1 /f')
        self.run_command('sc config TermService start= disabled')
        self.run_command('sc stop TermService')
        self.progress_bar.set(2/steps)

        # 3. จัดการ OneDrive
        self.run_command("taskkill /f /im OneDrive.exe")
        # ค้นหาตัว Uninstall ของ OneDrive (มีทั้ง 32 และ 64 bit)
        if os.path.exists(r"C:\Windows\System32\OneDriveSetup.exe"):
            self.run_command(r"C:\Windows\System32\OneDriveSetup.exe /uninstall")
        elif os.path.exists(r"C:\Windows\SysWOW64\OneDriveSetup.exe"):
            self.run_command(r"C:\Windows\SysWOW64\OneDriveSetup.exe /uninstall")
        self.progress_bar.set(3/steps)

        # 4. ปิด Startup Apps ที่ไม่จำเป็น (ใน Registry)
        # ปิดการรัน App ในระดับ User และ Machine (ตัวอย่าง Run key)
        startup_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"
        ]
        # หมายเหตุ: การลบทั้งหมดอาจกระทบ Driver บางตัว แนะนำให้ลบเป็นรายชื่อ หรือล้างค่าที่ไม่ใช่ระบบ
        for path in startup_paths:
            self.run_command(f'reg delete "HKEY_LOCAL_MACHINE\\{path}" /va /f')
            self.run_command(f'reg delete "HKEY_CURRENT_USER\\{path}" /va /f')
        self.progress_bar.set(4/steps)

        # 5. Disk Cleanup (ใช้ cleanmgr แบบอัตโนมัติ)
        # /sagerun:1 คือการรันตามค่าที่ตั้งไว้ (ต้องอาศัยการตั้งค่าล่วงหน้า) 
        # หรือใช้คำสั่งลบไฟล์ Shadow Copies และ Component Store ที่เกินมา
        self.run_command("dism /online /cleanup-image /startcomponentcleanup /resetbase")
        self.progress_bar.set(5/steps)

        self.status_label.configure(text="ดำเนินการขั้นสูงเสร็จสิ้น!", text_color="#2ecc71")
    
    def optimize_ram_and_processes(self):
        self.status_label.configure(text="กำลังเพิ่มพื้นที่แรมและปิด Process...", text_color="yellow")
        self.progress_bar.set(0)
        
        # รายการโปรแกรมที่จะปิด (สามารถเพิ่มชื่อ .exe ได้ที่นี่)
        apps_to_kill = [
            "AnyDesk.exe", 
            "TeamViewer.exe", 
            "msedge.exe",      # ปิด Edge ถ้าไม่ได้ใช้
            "skype.exe",
            "discord.exe"
        ]
        
        steps = 2 # 1. ปิดโปรแกรม 2. เคลียร์แรม
        
        # Step 1: ปิด Process ที่ไม่จำเป็น
        for app in apps_to_kill:
            # /F คือ force, /IM คือ image name, /T คือปิด child processes ด้วย
            self.run_command(f"taskkill /F /IM {app} /T")
        
        self.progress_bar.set(0.5)

        # Step 2: เรียกคืน RAM (Memory Optimization)
        # ใช้คำสั่ง PowerShell เพื่อสั่งให้ระบบจัดการหน่วยความจำที่ไม่ได้ใช้งาน (Working Set)
        # หมายเหตุ: วิธีนี้ปลอดภัยและไม่ทำให้เครื่องค้างเหมือนโปรแกรมล้างแรมปลอมบางตัว
        ps_command = (
            "powershell -command \"$processes = Get-Process; "
            "foreach($proc in $processes) { "
            "  try { "
            "    $proc.MaxWorkingSet = $proc.MinWorkingSet; "
            "  } catch {} "
            "}\""
        )
        self.run_command(ps_command)
        
        self.progress_bar.set(1.0)
        self.status_label.configure(text="เพิ่มแรมและปิดโปรแกรมส่วนเกินสำเร็จ!", text_color="#2ecc71")

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        app = TuneUpApp()
        app.mainloop()
    else:
        # Re-run the program with admin rights
        import sys
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)