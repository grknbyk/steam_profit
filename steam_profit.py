import csv
import json
import time
import tkinter as tk
import webbrowser
from threading import Thread
from tkinter import ttk

import requests
from bs4 import BeautifulSoup

IS_STARTED = False
SETTINGS = {}
SETTINGS_FILE = "settings.json"
try:
    with open(SETTINGS_FILE, 'r') as f:
        SETTINGS = json.load(f)
except FileNotFoundError:
    SETTINGS = {
      "cookie": {"sessionid": "",
    "steamLoginSecure": ""},
  "game_price_limit": 4,
  "min_profit_lower_limit": 60,
  "avg_profit_lower_limit": 60,
  "delay": 0.3,
  "games": [
  ]
}
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(SETTINGS, f)

delay = SETTINGS["delay"]

def save_data():
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(SETTINGS, f)

def save_data_on_close():
    is_started = False
    time.sleep(delay)
    save_data()
    root.destroy()

def gameCardPrices(gameId):
    url = "https://steamcommunity.com/market/search/render/?query=&start=0&count=15&search_descriptions=0&sort_column=price&sort_dir=asc&appid=753&category_753_Game%5B%5D=tag_app_"+gameId+"&category_753_cardborder%5B%5D=tag_cardborder_0&category_753_item_class%5B%5D=tag_item_class_2"
    r = requests.get(url = url, cookies=SETTINGS["cookie"])
    html_data = dict(r.json())['results_html']
    soup = BeautifulSoup(html_data, 'html.parser')
    prices = [int(x.find("span", {"class": "normal_price"})["data-price"]) for x in soup.find_all("span", {"class": "market_table_value normal_price"})]
    return prices

def calculateAvgProfit(gamePrice, cardPrices):
    avgCardPrice = sum(cardPrices)/len(cardPrices)*0.87
    cardsToDrop = int((len(cardPrices)+1)/2)
    avgProfit = avgCardPrice * cardsToDrop - gamePrice
    return int(avgProfit)

def calculateMinProfit(gamePrice, cardPrices):
    minCardPrice = min(cardPrices)*0.87
    cardsToDrop = int((len(cardPrices)+1)/2)
    minProfit = minCardPrice * cardsToDrop - gamePrice
    return int(minProfit)

def totalresults(url):
    r = requests.get(url,cookies=SETTINGS["cookie"])
    data = dict(r.json())
    totalresults = data['total_count']
    return int(totalresults)
 
def on_item_double_click(event):
    selected = table.selection()  
    if selected: 
        item = table.item(selected[0])  
        url = "https://store.steampowered.com/app/"+ str (item['values'][0]) 
        webbrowser.open(url)  
      
root = tk.Tk()
root.geometry("900x605")
root.resizable(False, False)
root.title("Steam Profitable Game Finder by grkn")


canvas = tk.Canvas(root, width=900, height=80)
canvas.pack()

canvas.create_line(0, 80, 900, 80, fill="black")
canvas.create_line(47, 0, 47, 38.3, fill="black")
canvas.create_line(266, 0, 266, 38.3, fill="black")
canvas.create_line(830, 35, 830, 80, fill="black")
canvas.create_line(690, 35, 690, 80, fill="black")

label1 = tk.Label(root, text="Game price limit:")
label1.place(x=50, y=9)

def reset_button_clicked():
    if IS_STARTED:
        show_info_label("Please wait until the process is finished or stop it.")
        return
    SETTINGS["games"] = []
    for item in table.get_children():
        table.delete(item)
    totalGamesLabel.config(text=str(len(SETTINGS["games"])))
    save_data()
    show_info_label("Games reset successfully.")

resetButton = tk.Button(root, text="Reset", width=4, height=1,command=reset_button_clicked)
resetButton.place(x=5, y=4)

spinbox = tk.Spinbox(root, from_=1, to=10,width=3)
spinbox.delete(0, "end")
spinbox.insert(0, SETTINGS["game_price_limit"])
spinbox.place(x=145, y=9)

minProfitScale = tk.Scale(root, from_=10, to=300, orient=tk.HORIZONTAL, resolution=1, length=150)
minProfitScale.set(SETTINGS["min_profit_lower_limit"])
minProfitScale.place(x=125, y=30)

label2 = tk.Label(root, text="Min profit lower limit:")
label2.place(x=5, y=50)

avgProfiScale = tk.Scale(root, from_=10, to=300, orient=tk.HORIZONTAL, resolution=1, length=150)
avgProfiScale.set(SETTINGS["avg_profit_lower_limit"])
avgProfiScale.place(x=420, y=30)

label3 = tk.Label(root, text="Avg profit lower limit:")
label3.place(x=300, y=50)

def filter_button_clicked():
    if IS_STARTED:
        show_info_label("Please wait until the process is finished or stop it.")
        return
    for item in table.get_children():
        table.delete(item)
    avgProfit = avgProfiScale.get()
    minProfit = minProfitScale.get()
    new_games = filter(lambda x: x[3] >= minProfit and x[4] >= avgProfit, SETTINGS["games"])
    for game in new_games:
        table.insert("", "end", values=(game[0], game[1], game[2], game[3], game[4], game[5], game[6]))
    show_info_label("Filter applied successfully.")


filterButton = tk.Button(root, text="Filter", width=4, height=1, command=filter_button_clicked)
filterButton.place(x=580, y=45)

canvas2 = tk.Canvas(root, width=900, height=1, bg="black")
canvas2.place(x=0, y=33)

label5 = tk.Label(text="sessionid:")
label5.place(x=275, y=9)

sessionidEntry = tk.Entry(root, width=25)
sessionidEntry.delete(0, "end")
sessionidEntry.insert(0, SETTINGS["cookie"]["sessionid"])
sessionidEntry.place(x=330, y=9)

label6 = tk.Label(text="steamLoginSecure:")
label6.place(x=485, y=9)

steamLoginSecureEntry = tk.Entry(root, width=40)
steamLoginSecureEntry.delete(0, "end")
steamLoginSecureEntry.insert(0, SETTINGS["cookie"]["steamLoginSecure"])
steamLoginSecureEntry.place(x=590, y=9)

table = ttk.Treeview(root, columns=("id", "title", "price", "min_profit", "avg_profit","cards_in_set","set_price"), show="headings", height=24)
table.heading("id", text="ID", command=lambda: sortBy(table, "id", "ID", False))
table.column("id", width=80, )
table.heading("title", text="Title", command=lambda: sortBy(table, "title", "Title", False))
table.column("title", width=370, )
table.heading("price", text="Price", command=lambda: sortBy(table, "price", "Price", False))
table.column("price", width=90, )
table.heading("cards_in_set", text="Cards In Set", command=lambda: sortBy(table, "cards_in_set", "Cards In Set", False))
table.column("cards_in_set", width=80, )
table.heading("set_price", text="Set Price", command=lambda: sortBy(table, "set_price", "Set Price", False))
table.column("set_price", width=80, )
table.heading("min_profit", text="Min Profit", command=lambda: sortBy(table, "min_profit", "Min Profit", False))
table.column("min_profit", width=90, )
table.heading("avg_profit", text="Avg Profit", command=lambda: sortBy(table, "avg_profit", "Avg Profit", False))
table.column("avg_profit", width=90, )

table.place(x=0, y=80)

scrollbar = tk.Scrollbar(root, orient="vertical", command=table.yview)
scrollbar.place(x=882, y=82, height=505)

table.configure(yscrollcommand=scrollbar.set)

table.bind('<Double-1>', on_item_double_click)

def prevent_resize(event):
    if table.identify_region(event.x, event.y) == "separator":
        return "break"
table.bind('<Button-1>', prevent_resize)
table.bind('<Motion>', prevent_resize)

def converter(x, index):
    if index == 1:
        return x[1]
    return int(x[index])

def sortBy(table, col, text, reverse):
    index = table["columns"].index(col)
    index = int(index)
    new_list = sorted(get_all_data(), key=lambda x: converter(x,index), reverse=reverse)
    for item in table.get_children():
        table.delete(item)
    for game in new_list:
        table.insert("", "end", values=(game[0], game[1], game[2], game[3], game[4],game[5],game[6]))
    table.heading(col, text=text, command=lambda: sortBy(table, col, text, not reverse))

for game in SETTINGS["games"]:
    table.insert("", "end", values=(game[0], game[1], game[2], game[3], game[4],game[5],game[6]))

def get_all_data():
    return [list(table.item(item_id)['values']) for item_id in table.get_children()]

label7 = tk.Label(text="Total games:")
label7.place(x=55, y=586)

totalGamesLabel = tk.Label(text=str(len(SETTINGS["games"])))
totalGamesLabel.place(x=125, y=586)

label4 = tk.Label(text="Info:")
label4.place(x=157, y=586)

def show_info_label(text_data):
    def worker():
        infoLabel = tk.Label(text=" "*999)
        infoLabel.place(x=185, y=586)
        infoLabel2 = tk.Label(text=text_data+ time.strftime("  ( %H:%M:%S  %d-%m-%Y )"))
        infoLabel2.place(x=185, y=586)
        time.sleep(5)
    Thread(target=worker).start()

def save_button_clicked():
    if IS_STARTED:
        show_info_label("Please wait until the process is finished or stop it.")
        return
    SETTINGS["cookie"]["sessionid"] = sessionidEntry.get()
    SETTINGS["cookie"]["steamLoginSecure"] = steamLoginSecureEntry.get()
    SETTINGS["game_price_limit"] = int(spinbox.get())
    SETTINGS["min_profit_lower_limit"] = minProfitScale.get()
    SETTINGS["avg_profit_lower_limit"] = avgProfiScale.get()
    save_data()
    show_info_label("Settings saved successfully.")

saveButton = tk.Button(root, text="Save", width=5, height=1, command=save_button_clicked)
saveButton.place(x=840, y=4)

def backup_button_clicked():
    if IS_STARTED:
        show_info_label("Please wait until the process is finished or stop it.")
        return
    with open('backup.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Title", "Price", "Min Profit", "Avg Profit","Cards In Set","Set Price"])
        writer.writerows(get_all_data())
    show_info_label("Backup created successfully.")
        
backupButton = tk.Button(root, text="Backup", width=5, height=1, command=backup_button_clicked)
backupButton.place(x=845, y=45)

def unfilter_button_clicked():
    if IS_STARTED:
        show_info_label("Please wait until the process is finished or stop it.")
        return
    for item in table.get_children():
        table.delete(item)
    for game in SETTINGS["games"]:
        table.insert("", "end", values=(game[0], game[1], game[2], game[3], game[4],game[5],game[6]))
    minProfitScale.set(10)
    avgProfiScale.set(10)
    show_info_label("Filter removed successfully.")

unfilter = tk.Button(root, text="Unfilter", width=6, height=1, command=unfilter_button_clicked)
unfilter.place(x=625, y=45)


def find_failed_games_button_clicked():
    if IS_STARTED:
        show_info_label("Please wait until the process is finished or stop it.")
        return
    for item in table.get_children():
        table.delete(item)
    new_list = filter(lambda x: x[3] == -404 or x[4] == -404 or x[5] == -404 or x[6] == -404, SETTINGS["games"])
    for game in new_list:
        table.insert("", "end", values=(game[0], game[1], game[2], game[3], game[4],game[5],game[6]))
            

reButton = tk.Button(root, text="Find Failed Games", width=15, height=1, command=find_failed_games_button_clicked)
reButton.place(x=700, y=45)


def searchGames():
    start = len(SETTINGS["games"])
    url = "https://store.steampowered.com/search/results/?query&start=0&count=50&dynamic_data=&sort_by=Price_ASC&snr=1_7_7_2300_7&specials=1&hidef2p=1&maxprice=10&category1=998&category2=29&infinite=1"
    urlHead = url[:59]
    urlTail = url[60:]
    totres = totalresults(url)
    for x in range(start, totres, 50):
        url = urlHead+str(x)+urlTail
        data_html = requests.get(url,cookies=SETTINGS["cookie"]).json()['results_html']
        games = BeautifulSoup(data_html, 'html.parser').find_all("a")
        for game in games:
            if not IS_STARTED:
                return
            _id = game.get("data-ds-appid")
            if _id in [x[0] for x in SETTINGS["games"]]:
                continue
            price = game.find("div", {"class": "col search_price_discount_combined responsive_secondrow"})["data-price-final"]
            price = int(price)
            if price >  int(spinbox.get())*100:
                show_info_label("Process finished.")
                IS_STARTED = False
                return
            title = game.find("span", {"class": "title"}).text
            try:
                cardPrices = gameCardPrices(_id)
                cardsInSet = len(cardPrices)
                setPrice = sum(cardPrices)
                avgProfit = calculateAvgProfit(price, cardPrices)
                minProfit = calculateMinProfit(price, cardPrices)
                SETTINGS["games"].append([_id, title, price, minProfit, avgProfit,cardsInSet,setPrice])
                table.insert("", "end", values=(_id, title, price, minProfit, avgProfit,cardsInSet,setPrice))
            except Exception:
                table.insert("", "end", values=(_id, title, price, -404, -404,-404,-404))
                SETTINGS["games"].append([_id, title, price, -404, -404,-404,-404])
            totalGamesLabel.config(text=str(len(SETTINGS["games"])))
            time.sleep(delay)
    

def start_finding():
    Thread(target=searchGames).start()
            

def toggle_button_clicked():
    global IS_STARTED
    if IS_STARTED:
        IS_STARTED = False
        toggleButton.config(text="Start Finding")
        show_info_label("Process stopped.")
    else:
        IS_STARTED = True
        start_finding()
        toggleButton.config(text="Stop Finding")
        show_info_label("Process started.")

toggleButton = tk.Button(root, text="Start Finding", width=9, height=1,command=toggle_button_clicked)
toggleButton.place(x=185, y=4)

gitLabel = tk.Label(text="GitHub", fg="blue", cursor="hand2")
gitLabel.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/grknbyk"))
gitLabel.place(x=5, y=586)

root.protocol("WM_DELETE_WINDOW", save_data_on_close)

root.mainloop()
