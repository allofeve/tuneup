import customtkinter as ctk
import os
import shutil
import ctypes
import subprocess
import json

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TuneUpApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Windows & Browser Optimizer Pro")
        self.geometry("1024x768") # ปรับขนาดเล็กน้อยเพื่อรองรับปุ่มใหม่

        self.label = ctk.CTkLabel(self, text="โปรแกรมช่วยให้คอมพิวเตอร์ทำงานได้ลื่นขึ้นมานิดหน่อย", font=("Kanit", 22, "bold"))
        self.label.pack(pady=20)

        # ปุ่มเมนูต่างๆ
        self.create_button("1. ล้างไฟล์ขยะระบบ (Clean Temp)", self.optimize_files, "#3498db")
        self.create_button("2. ปิด Services & Windows Update", self.disable_services, "#e67e22")
        self.create_button("3. ปิด & ลบอัปเดต Firefox Developer", self.manage_firefox, "#e74c3c")

        self.status_label = ctk.CTkLabel(self, text="สถานะ: พร้อมใช้งาน (สิทธิ์ Administrator)", text_color="gray")
        self.status_label.pack(pady=20)

    def create_button(self, text, command, color):
        btn = ctk.CTkButton(self, text=text, command=command, fg_color=color, height=40)
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

if __name__ == "__main__":
    if ctypes.windll.shell32.IsUserAnAdmin():
        app = TuneUpApp()
        app.mainloop()
    else:
        # Re-run the program with admin rights
        import sys
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)