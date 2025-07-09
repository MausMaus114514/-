import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

class FatigueGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("疲劳数据监控")
        self.root.geometry("1200x600")  # 增加宽度以适应图表和树形视图
        
        # 配置参数
        self.csv_file = 'info.csv'
        self.data = pd.DataFrame(columns=[
            "device_id",
            "timestamp",
            "status_code",
            "status_text",
            "is_alert",
            "blink_count",
            "yawn_count",
            "head_nod_count"
        ])
        
        # 定义TREEVIEW的列
        self.FIELDS = [
            "device_id",
            "timestamp",
            "status_code",
            "status_text",
            "is_alert",
            "blink_count",
            "yawn_count",
            "head_nod_count"
        ]
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        """创建GUI组件"""
        # 数据展示区域
        self.tree_frame = ttk.Frame(self.root, relief='sunken', borderwidth=1)
        self.tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tree_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=self.FIELDS,
            show="headings",
            yscrollcommand=self.tree_scroll.set
        )
        for col in self.FIELDS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scroll.config(command=self.tree.yview)
        
        # 绑定双击事件以显示详细信息
        self.tree.bind("<Double-1>", self.on_tree_double_click)
        
        # 图表区域
        self.chart_frame = ttk.Frame(self.root, relief='sunken', borderwidth=1)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 更新按钮
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.update_button = ttk.Button(self.button_frame, text="刷新数据", command=self.update_data)
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        # 可以在这里添加更多按钮或控件
        
        # 初始数据加载
        self.update_plot()
        
    def load_data(self):
        """从CSV加载数据到Treeview"""
        if os.path.exists(self.csv_file):
            try:
                self.data = pd.read_csv(self.csv_file)
                self.tree.delete(*self.tree.get_children())
                for index, row in self.data.iterrows():
                    self.tree.insert("", "end", values=tuple(row))
            except Exception as e:
                print(f"读取CSV文件时出错: {e}")
        else:
            print(f"CSV文件不存在: {self.csv_file}")
    
    def update_data(self):
        """更新数据和图表"""
        self.load_data()
        self.update_plot()
    
    def update_plot(self):
        """根据当前数据更新图表"""
        if self.data.empty:
            self.ax.clear()
            self.ax.set_title("暂无数据")
            self.canvas.draw()
            return
        
        # 清除之前的图表
        self.ax.clear()
        
        # 示例图表1：状态码分布
        status_counts = self.data['status_code'].value_counts().sort_index()
        self.ax.bar(status_counts.index.astype(str), status_counts.values, color=['green', 'orange', 'red'], label='状态码分布')
        self.ax.set_title('疲劳状态码分布')
        self.ax.set_xlabel('状态码')
        self.ax.set_ylabel('次数')
        self.ax.legend()
        
        # 示例图表2：警报次数统计
        alert_counts = self.data['is_alert'].value_counts().sort_index()
        self.ax2 = self.ax.twinx()
        colors = ['gold' if val == 0 else 'red' for val in alert_counts.index]
        self.ax2.bar(alert_counts.index.astype(str), alert_counts.values, color=colors, alpha=0.6, label='警报次数')
        self.ax2.set_ylabel('警报次数')
        self.ax2.legend(loc='upper right')
        
        # 更新图表
        self.canvas.draw()
        
        # 可以根据需要添加更多图表
        
    def on_tree_double_click(self, event):
        """双击Treeview时显示详细信息"""
        selected_item_id = self.tree.selection()
        if not selected_item_id:
            return
        
        item = self.tree.item(selected_item_id)
        values = item['values']
        detail_window = tk.Toplevel(self.root)
        detail_window.title("详细信息")
        detail_window.geometry("300x250")
        
        label_text = "\n".join([f"{field}: {value}" for field, value in zip(self.FIELDS, values)])
        label = ttk.Label(detail_window, text=label_text, justify='left')
        label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = FatigueGUI(root)
    root.mainloop()