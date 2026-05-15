import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# 导入三个核心功能
from processor import compress_by_quality, resize_image, add_watermark
import datetime
import os
import threading


class ImageToolUI:
    def __init__(self, root):
        self.root = root

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        win_width = int(screen_width * 0.4)
        win_height = int(screen_height * 0.35)

        position_x = int((screen_width - win_width) / 2)
        position_y = int((screen_height - win_height) / 2)

        self.root.geometry(f"{win_width}x{win_height}+{position_x}+{position_y}")
        self.root.title("极简图像处理工具 by RyanAidenDK")
        self.root.iconbitmap(os.path.join(os.path.dirname(__file__), "RyanAiden-DKicon.ico"))
        self.root.resizable(False, False)

        # 1-公共文件选择区域
        self.setup_file_selection()

        # 2-创建选项卡控件
        self.tab_control = ttk.Notebook(self.root)

        # 3-创建三个功能页面
        self.tab_compress = ttk.Frame(self.tab_control)
        self.tab_resize = ttk.Frame(self.tab_control)
        self.tab_watermark = ttk.Frame(self.tab_control)

        # 4-添加到选项卡中
        self.tab_control.add(self.tab_compress, text=' 压缩图片 ')
        self.tab_control.add(self.tab_resize, text=' 缩放尺寸 ')
        self.tab_control.add(self.tab_watermark, text=' 添加水印 ')
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        # 5-分别布局三个功能的界面
        self.setup_compress_ui()
        self.setup_resize_ui()
        self.setup_watermark_ui()

        # 6-日志提示框
        self.log_area = tk.Text(self.root, height=10, font=("Consolas", 9), state="disabled")
        self.log_area.pack(padx=(5, 5), pady=10, fill="x")
        self.log_area.tag_config("black", foreground="black")
        self.log_area.tag_config("green", foreground="green")
        self.log_area.tag_config("red", foreground="red")

        self.log("欢迎使用极简图像处理工具", color="black")
        self.log("准备就绪，请选择待处理图片...", color="black")



        #小项目用简易的填充布局(只学了这个，下次学自定义）
    def setup_file_selection(self):
        #选取文件栏
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=10, fill="x", padx=20)
        #实时检测输入路径，方便输入路径
        self.input_path = tk.StringVar()
        tk.Label(file_frame, text="待处理图片:").pack(side="left")
        tk.Entry(file_frame, textvariable=self.input_path).pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(file_frame, text="选择", command=self.select_file).pack(side="left")

    # 压缩 UI
    def setup_compress_ui(self):
        tk.Label(self.tab_compress, text="压缩质量 (1-100):", font=("Arial",20)).pack(pady=40)
        self.quality_val = tk.Scale(self.tab_compress, from_=1, to=100, orient="horizontal", length=350, tickinterval=10)
        self.quality_val.set(90)
        self.quality_val.pack()
        tk.Button(self.tab_compress, text="开始压缩", command=self.run_compress, bg="#2196F3", fg="white").pack(pady=20)

    # 缩放 UI
    def setup_resize_ui(self):
        tk.Label(self.tab_resize, text="宽度比例 (%):", font=("微软雅黑", 15)).pack(pady=(50,10))
        self.w_ratio = tk.Entry(self.tab_resize)
        self.w_ratio.insert(0, "50")
        self.w_ratio.pack()

        tk.Label(self.tab_resize, text="高度比例 (%):", font=("微软雅黑", 15)).pack(pady=10)
        self.h_ratio = tk.Entry(self.tab_resize)
        self.h_ratio.insert(0, "50")
        self.h_ratio.pack()

        tk.Button(self.tab_resize, text="开始缩放", command=self.run_resize, bg="#4CAF50", fg="white").pack(pady=20)

    # 水印 UI
    def setup_watermark_ui(self):
        tk.Label(self.tab_watermark, text="水印内容:", font=("微软雅黑", 15)).pack(pady=(50,10))
        self.wm_text = tk.Entry(self.tab_watermark)
        self.wm_text.insert(0, "RyanAiden-DK")
        self.wm_text.pack()

        tk.Label(self.tab_watermark, text="位置选择:", font=("微软雅黑", 15)).pack(pady=10)
        self.wm_pos = ttk.Combobox(self.tab_watermark, values=["对角线和右下角", "仅右下角", "仅对角线"])
        self.wm_pos.current(0)
        self.wm_pos.pack()

        tk.Label(self.tab_watermark, text="透明度（0-100）:", font=("微软雅黑", 15)).pack(pady=10)
        self.wm_trs = tk.Entry(self.tab_watermark)
        self.wm_trs.pack()

        tk.Button(self.tab_watermark, text="添加水印", command=self.run_watermark, bg="#FF9800", fg="white").pack(
            pady=20)

    # 按钮触发逻辑
    def select_file(self):
        path = filedialog.askopenfilename()
        if path: self.input_path.set(path)

    def get_output_path(self, suffix):
        root, ext = os.path.splitext(self.input_path.get())
        return f"{root}_{suffix}{ext}"

    def run_compress(self):
        if not self.input_path.get():
            self.log("请先选择图片文件", color="red")
            return
        def task():
            try:
                q_val = self.quality_val.get()
                op_path = self.get_output_path(f"compressed_{q_val}")
                compress_by_quality(self.input_path.get(), op_path, q_val)
                self.root.after(0, lambda: self.log(f"压缩完成，文件保存至{op_path}", color="green"))
                self.root.after(0, lambda: messagebox.showinfo("提示", "压缩成功！"))
            except Exception as e:
                msg = "请检查文件路径是否正确" if "list index" in str(e) else f"压缩失败: {e}"
                self.root.after(0, lambda m=msg: self.log(m, color="red"))
        threading.Thread(target=task, daemon=True).start()

    def run_resize(self):
        if not self.input_path.get():
            self.log("请先选择图片文件", color="red")
            return
        def task():
            try:
                size_w = float(self.w_ratio.get())
                size_h = float(self.h_ratio.get())
                if size_w <= 0 or size_h <= 0:
                    self.root.after(0, lambda: self.log("比例必须大于0", color="red"))
                    return
                suffix = f"resized_{size_w}{size_h}"
                op_path = self.get_output_path(suffix)
                resize_image(self.input_path.get(), size_w, size_h, op_path)
                self.root.after(0, lambda: self.log(f"缩放完成，文件保存至{op_path}", color="green"))
                self.root.after(0, lambda: messagebox.showinfo("提示", "缩放成功！"))
            except Exception as e:
                msg = "请检查文件路径是否正确" if "list index" in str(e) else f"缩放失败: {e}"
                self.root.after(0, lambda m=msg: self.log(m, color="red"))
        threading.Thread(target=task, daemon=True).start()

    def run_watermark(self):
        if not self.input_path.get():
            self.log("请先选择图片文件", color="red")
            return
        def task():
            try:
                watermark_text = self.wm_text.get() or "RyanAiden-DK"
                op_path = self.get_output_path(f"wm_{watermark_text}")
                add_watermark(self.input_path.get(), op_path, watermark_text, self.wm_pos.get(), self.wm_trs.get())
                self.root.after(0, lambda: self.log(f"水印添加完成，文件保存至{op_path}", color="green"))
                self.root.after(0, lambda: messagebox.showinfo("提示", "水印添加成功！"))
            except Exception as e:
                msg = "请检查文件路径是否正确" if "list index" in str(e) else f"水印添加失败: {e}"
                self.root.after(0, lambda m=msg: self.log(m, color="red"))
        threading.Thread(target=task, daemon=True).start()

    def log(self, message, color="black"):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{current_time}]:{message}\n"
        self.log_area.config(state="normal")
        self.log_area.insert("end", full_msg, color)
        self.log_area.see("end")
        self.log_area.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToolUI(root)
    root.mainloop()