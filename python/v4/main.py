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
        self.update_idletasks()
        
        folders = [os.environ.get('TEMP'), r'C:\Windows\Temp', r'C:\Windows\Prefetch']
        count = 0
        for f in folders:
            if os.path.exists(f):
                for item in os.listdir(f):
                    try:
                        path = os.path.join(f, item)
                        if os.path.isfile(path): os.unlink(path)
                        else: shutil.rmtree(path)
                        count += 1
                    except: continue
        
        self.status_label.configure(text=f"ลบไฟล์สำเร็จ {count} รายการ", text_color="#2ecc71")

    def disable_services(self):
        self.status_label.configure(text="กำลังปิดบริการที่ไม่จำเป็น...", text_color="yellow")
        self.update_idletasks()

        # รายชื่อ Service ที่จะปิด (wuauserv = Windows Update)
        # สามารถเพิ่มชื่อ service อื่นๆ ได้ใน list นี้
        services_to_disable = [
            "wuauserv",      # Windows Update
            "bits",          # Background Intelligent Transfer Service
            "SysMain",       # Superfetch (สำหรับ HDD เก่าอาจจะเร็วขึ้น แต่ SSD อาจไม่จำเป็นต้องปิด)
            "TabletInputService" # Touch Keyboard and Handwriting Panel
            "WSearch"            # Windows Search (เพิ่มตัวนี้เข้าไปครับ)
        ]

        success_count = 0
        for svc in services_to_disable:
            # คำสั่ง stop และตั้งค่าเป็น Disabled
            stop_cmd = f"sc stop {svc}"
            disable_cmd = f"sc config {svc} start= disabled"
            
            self.run_command(stop_cmd)
            if self.run_command(disable_cmd):
                success_count += 1

        self.status_label.configure(text=f"ปิด {success_count} บริการและ Windows Update แล้ว", text_color="#2ecc71")
    
    def manage_firefox(self):
        self.status_label.configure(text="กำลังจัดการ Firefox Developer Edition...", text_color="yellow")
        self.update_idletasks()

        # 1. สร้างนโยบาย (Policies) เพื่อปิดการอัปเดตถาวร
        # โดยปกติ Firefox จะติดตั้งที่ C:\Program Files\Firefox Developer Edition
        ff_path = r"C:\Program Files\Firefox Developer Edition"
        policy_path = os.path.join(ff_path, "distribution")
        
        try:
            if not os.path.exists(policy_path):
                os.makedirs(policy_path)
            
            policy_data = {
                "policies": {
                    "DisableAppUpdate": True
                }
            }
            
            with open(os.path.join(policy_path, "policies.json"), "w") as f:
                json.dump(policy_data, f, indent=4)
            
            # 2. ลบไฟล์อัปเดตที่โหลดค้างไว้ (Update Archive)
            # อยู่ใน %LocalAppData%\Mozilla\updates
            ff_updates = os.path.join(os.environ.get('LOCALAPPDATA'), "Mozilla", "updates")
            if os.path.exists(ff_updates):
                shutil.rmtree(ff_updates)
                os.makedirs(ff_updates) # สร้างโฟลเดอร์เปล่าไว้

            self.status_label.configure(text="ปิดการอัปเดตและล้างไฟล์ Firefox สำเร็จ!", text_color="#2ecc71")
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

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        app = TuneUpApp()
        app.mainloop()
    else:
        # Re-run the program with admin rights
        import sys
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)