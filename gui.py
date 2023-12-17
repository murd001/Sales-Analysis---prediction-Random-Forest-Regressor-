from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, filedialog, ttk
import pandas as pd
from joblib import load
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import joblib
from sklearn.preprocessing import LabelEncoder
import numpy as np
from PIL import Image, ImageTk

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\mdmur\OneDrive\Pictures\MohasProject\assets\frame0")

model = joblib.load('simprandom_r_mlV001.joblib')
label_encoder = LabelEncoder()

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        load_sales_data(file_path)
        plot_bar_graph()

def load_sales_data(file_path):
    global df
    df = pd.read_csv(file_path)

def plot_bar_graph():
    unique_products = df['product'].unique()
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_products)))

    color_dict = {product: color for product, color in zip(unique_products, colors)}

    data_to_plot = df[['product', 'quantity_sold_that_month']]

    fig, ax = plt.subplots()
    bars = ax.bar(data_to_plot['product'], data_to_plot['quantity_sold_that_month'], color="deepskyblue")

    for bar, product in zip(bars, data_to_plot['product']):
        bar.set_color(color_dict[product])

    ax.set_facecolor("#d4f0f8")
    ax.set_xlabel('Product')
    ax.set_ylabel('Quantity Sold')
    ax.set_title('Quantity Sold; Products')
    ax.grid(visible=True)
    
    ax.set_xticks(np.arange(len(unique_products)))
    ax.set_xticklabels(unique_products, rotation=270, ha='left', fontsize=6)

    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.place(
        x=8.0,
        y=46.0,
        width=481.0,
        height=481.0,
    )

    table_columns = list(df.columns)  
    display_columns = ['order_id', 'product', 'quantity_ordered', 'price_each', 'order_date', 'quantity_sold_that_month']

    table = ttk.Treeview(master=window, columns=display_columns, show="headings")

    for column in display_columns:
        table.heading(column=column, text=column)
        table.column(column=column, width=70)

    for index, row_data in df.iterrows():
        table.insert(parent="", index="end", values=list(row_data[display_columns]))
        
    style = ttk.Style()
    style.theme_use("classic")
    style.configure("Treeview", background="#484764", fieldbackground="#484764", foreground="white")
    style.configure("Treeview.Heading", background="#0a283d", fieldbackground="#0a283d", foreground="white")
    style.map("Treeview", background=[("selected", "#E5BEEC")])

    table.place(x=502, y=336, width=589, height=322)
    
    dfpred = df.groupby('product').agg({
        'quantity_sold_last_month': 'first',
        'quantity_sold_that_month': 'first'
    }).reset_index()
    
    dfpred = dfpred.sort_values(by='quantity_sold_that_month', ascending=False)
    
    dfpred = dfpred.drop_duplicates(subset='product')
    dfpred = dfpred.reset_index(drop=True)
    label_encoder.fit_transform(dfpred['product'])
    dfpred['product_encoded'] = label_encoder.transform(dfpred['product'])
    predictions = []
    
    for index, row in dfpred.iterrows():
        user_input = pd.DataFrame({
            'product_encoded': [row['product_encoded']],
            'quantity_sold_last_month': [row['quantity_sold_last_month']],
            'quantity_sold_that_month': [row['quantity_sold_that_month']]
        })
        prediction = model.predict(user_input)
        predictions.append(prediction[0])
    
    dfpred['next_months_prediction'] = predictions
    
    dfpred_columns = list(dfpred.columns)

    dfpred_display_columns = ['product', 'quantity_sold_last_month', 'quantity_sold_that_month', 'next_months_prediction']

    dfpred_table = ttk.Treeview(master=window, columns=dfpred_display_columns, show="headings")

    for column in dfpred_display_columns:
        dfpred_table.heading(column=column, text=column)
        dfpred_table.column(column=column, width=70)

    for index, row_data in dfpred.iterrows():
        dfpred_table.insert(parent="", index="end", values=list(row_data[dfpred_display_columns]))

    style_treeview = ttk.Style()
    style_treeview.configure("Treeview", background="#d4f0f8", fieldbackground="#d4f0f8", foreground="black")
    style_treeview.configure("Treeview.Heading", background="#C7C7DB", fieldbackground="#C7C7DB", foreground="black")

    dfpred_table.place(x=502, y=53, width=589, height=279)

def create_rounded_rectangle(canvas, x, y, width, height, radius, color): 
    x1, y1, x2, y2 = x, y, x + width, y + height
    canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, outline=color, width=2)
    canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, outline=color, width=2)
    canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, outline=color, width=2)
    canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, outline=color, width=2)
    canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, outline=color, width=2)
    canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, outline=color, width=2)

window = Tk()
window.title("Restocking Guide")
window.geometry("1099x672")
window.configure(bg="#2B2A31")

canvas = Canvas(
    window,
    bg="#2B2A31",
    height=672,
    width=1099,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)
canvas.create_rectangle(
    8.0,
    53.0,
    490.0,
    517.0,
    fill="#F4E2E2",
    outline=""
)

image_path = relative_to_assets("bargraph.gif")
gif_image = Image.open(image_path)
tk_image = ImageTk.PhotoImage(gif_image)

image_item = canvas.create_image(250, 285, anchor="center", image=tk_image)

#create_rounded_rectangle(canvas, 8, 53, 304, 329, 10, "#7C6767")

canvas.create_text(
    19.0,
    62.0,
    anchor="nw",
    text="Sales",
    fill="#1D1B1B",
    font=("Inter Bold", 15 * -1)
)

canvas.create_rectangle(
    502.0,
    53.0,
    1091.0,
    332.0,
    fill="#C7C6DA",
    outline="")

#create_rounded_rectangle(canvas, 332, 46, 656, 394, 10, "#C97373")
table_image_path = relative_to_assets("table.png")
table_photo_image = PhotoImage(file=table_image_path)

table_image_item = canvas.create_image(502.0, 53.0, anchor="nw", image=table_photo_image)

canvas.create_rectangle(
    8.0,
    533.0,
    490.0,
    667.0,
    fill="#F5EDED",
    outline="")

#create_rounded_rectangle(canvas, 8, 340, 324, 532, 10, "#F54E4E")
instructions_image_path = relative_to_assets("instructions.png")
instructions_photo_image = PhotoImage(file=instructions_image_path)

instructions_image_item = canvas.create_image(8.0, 533.0, anchor="nw", image=instructions_photo_image)


button_csv = Button(
    text="Import CSV",
    command=browse_file,
    relief="flat",
    bg="#7C6767",
    fg="#FFFFFF",
    font=("Inter Bold", 10 * -1)
)
button_csv.place(
    x=998.0,
    y=7.0,
    width=93.0,
    height=36.0
)
#create_rounded_rectangle(canvas, 566, 7, 93, 36, 10, "#7C6767")
create_rounded_rectangle(canvas, 998, 7, 93, 36, 10, "#7C6767")

table_1_image_path = relative_to_assets("table_1.png")
table_1_photo_image = PhotoImage(file=table_1_image_path)

table_1_image_item = canvas.create_image(502.0, 336.0, anchor="nw", image=table_1_photo_image)


window.resizable(False, False)
window.mainloop()
