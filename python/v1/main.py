import customtkinter as ctk
import os
import shutil
import ctypes
import subprocess

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TuneUpApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Windows Turbo Optimizer Pro")
        self.geometry("600x450")

        self.label = ctk.CTkLabel(self, text="System Optimizer & Service Tweak", font=("Kanit", 22, "bold"))
        self.label.pack(pady=20)

        # ปุ่มล้างไฟล์ขยะ
        self.btn_cleanup = ctk.CTkButton(self, text="1. ล้างไฟล์ขยะ (Clean Temp)", command=self.optimize_files, fg_color="#3498db")
        self.btn_cleanup.pack(pady=10, fill="x", padx=100)

        # ปุ่มปิด Services และ Update
        self.btn_service = ctk.CTkButton(self, text="2. ปิด Services & Windows Update", command=self.disable_services, fg_color="#e67e22")
        self.btn_service.pack(pady=10, fill="x", padx=100)

        self.status_label = ctk.CTkLabel(self, text="สถานะ: พร้อมใช้งาน (สิทธิ์ Administrator)", text_color="gray")
        self.status_label.pack(pady=20)

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

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        app = TuneUpApp()
        app.mainloop()
    else:
        # Re-run the program with admin rights
        import sys
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)