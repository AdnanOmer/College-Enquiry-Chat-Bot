import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI") 
DB_PASS = os.environ.get("DB_PASS") 

APP_DB_NAME = os.environ.get("APP_DB_NAME")
APP_COLLECTION_NAME = os.environ.get("APP_COLLECTION_NAME")

active_collection = None

if not MONGO_URI or not DB_PASS:
    raise RuntimeError("⚠️ الرجاء ضبط المتغيرات MONGO_URI و DB_PASS داخل ملف .env")

client = None
db = None
collection = None


RTL = "\u202B"
APP_FONT = ("Segoe UI", 14)



def connect_db():
    global client, db
    client = MongoClient(MONGO_URI)
    db = client[APP_DB_NAME]
    return True


def pretty_doc(doc, show_id=True):
    lines = []
    if show_id:
        lines.append(f"{RTL}🆔 _id: {doc.get('_id')}")

    if "question" in doc and "answer" in doc:
        lines.append(f"{RTL}📌 التصنيف: {doc.get('category', '')}")
        lines.append(f"{RTL}❓ السؤال: {doc.get('question', '')}")
        lines.append(f"{RTL}✅ الإجابة: {doc.get('answer', '')}")

    elif "userMessage" in doc and "botResponse" in doc:  
        lines.append(f"{RTL}👤 المستخدم: {doc.get('userMessage', '')}")
        lines.append(f"{RTL}🤖 البوت: {doc.get('botResponse', '')}")
        lines.append(f"{RTL}🕒 التاريخ: {doc.get('createdAt', '')}")

    else:  
        for k, v in doc.items():
            lines.append(f"{RTL}{k}: {v}")

    return "\n".join(lines)



def ensure_data_json(data):
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("صيغة data.json غير صحيحة")



def ask_rtl_string(title, prompt):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("530x150")
    win.grab_set() 

    lbl = tk.Label(win, text=f"{RTL}{prompt}", font=APP_FONT, anchor="e", justify="right")
    lbl.pack(pady=10, padx=10, anchor="e")

    entry = tk.Entry(win, font=APP_FONT, justify="right")
    entry.pack(pady=5, padx=10, fill="x")
    entry.focus()

    value = {"text": None}

    def submit():
        value["text"] = entry.get()
        win.destroy()

    tk.Button(win, text="✔ موافق", font=APP_FONT, command=submit).pack(pady=10)

    win.wait_window()
    return value["text"]


def show_all():
    docs = list(collection.find({}))
    if not docs:
        messagebox.showinfo("📋 عرض البيانات", f"{RTL}⚠️ لا توجد بيانات في قاعدة البيانات.")
        return

    win = tk.Toplevel(root)
    win.title("📋 جميع البيانات")
    win.geometry("800x600")

    txt = tk.Text(win, font=APP_FONT, wrap="word")
    txt.tag_configure("rtl", justify="right")
    txt.pack(fill="both", expand=True)

    for i, d in enumerate(docs, start=1):
        txt.insert("end", f"{RTL}— مدخل {i} —\n{pretty_doc(d)}\n\n", "rtl")

    txt.config(state="disabled")


def insert_single():
    cat = ask_rtl_string("➕ إضافة مدخل", "أدخل التصنيف(general , fees ,admission , location , subjects):")
    if not cat: return
    q = ask_rtl_string("➕ إضافة مدخل", "أدخل السؤال:")
    if not q: return
    a = ask_rtl_string("➕ إضافة مدخل", "أدخل الإجابة:")
    if not a: return
    collection.insert_one({
        "category": RTL + cat,
        "question": RTL + q,
        "answer": RTL + a,
        "deleted": False
    })
    messagebox.showinfo("تم", f"{RTL}✅ تم إدخال المدخل بنجاح.")


def insert_from_json():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        items = ensure_data_json(data)
        res = collection.insert_many(items)
        messagebox.showinfo("تم", f"{RTL}✅ تم إدخال {len(res.inserted_ids)} مستندات.")
    except FileNotFoundError:
        messagebox.showerror("خطأ", f"{RTL}❌ لم يتم العثور على data.json")
    except Exception as e:
        messagebox.showerror("خطأ", f"{RTL}حدث خطأ:\n{e}")


def update_entry():
    docs = list(collection.find({"deleted": {"$ne": True}}))
    if not docs:
        messagebox.showinfo("📋", f"{RTL}⚠️ لا توجد بيانات للتعديل.")
        return

    win = tk.Toplevel(root)
    win.title("✏️ تعديل مدخل")
    win.geometry("700x500")

    lbl = tk.Label(win, text=f"{RTL}📋 اختر المدخل الذي تريد تعديله:", font=APP_FONT, anchor="e", justify="right")
    lbl.pack(pady=5, fill="x")

    listbox = tk.Listbox(win, width=100, height=15, font=APP_FONT, justify="right")
    listbox.pack(pady=10, padx=10, fill="both", expand=True)

    for d in docs:
        listbox.insert("end", f"{d.get('question', '')}")

    def edit_selected():
        sel = listbox.curselection()
        if not sel:
            return
        index = sel[0]
        doc = docs[index]
        messagebox.showinfo("المدخل الحالي", pretty_doc(doc, show_id=True))

        field_choice = simpledialog.askstring(
            "اختر الحقل",
            f"{RTL}أي حقل تريد تعديله؟\n1- التصنيف\n2- السؤال\n3- الإجابة"
        )
        if not field_choice: return
        field_map = {"1": "category", "2": "question", "3": "answer"}
        field = field_map.get(field_choice.strip())
        if not field: return

        new_value = ask_rtl_string("القيمة الجديدة", f"أدخل القيمة الجديدة لـ {field}:")
        if not new_value: return

        collection.update_one({"_id": doc["_id"]}, {"$set": {field: RTL + new_value}})
        messagebox.showinfo("✅", f"{RTL}تم تعديل البيانات بنجاح.")
        win.destroy()

    tk.Button(win, text=f"{RTL}✏️ تعديل المحدد", font=APP_FONT, command=edit_selected).pack(pady=10)


def delete_entry():
    docs = list(collection.find({"deleted": {"$ne": True}}))
    if not docs:
        messagebox.showinfo("📋", f"{RTL}⚠️ لا توجد بيانات للحذف.")
        return

    win = tk.Toplevel(root)
    win.title("🗑️ حذف مدخل (مؤقت)")
    win.geometry("700x550")

    listbox = tk.Listbox(win, width=100, height=15, font=APP_FONT, justify="right", selectmode=tk.MULTIPLE)
    listbox.pack(pady=10, padx=10, fill="both", expand=True)

    for d in docs:
        listbox.insert("end", f"{d['_id']} | {d.get('userMessage', '')}")

    def select_all():
        listbox.select_set(0, tk.END)

    def delete_selected():
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("⚠️", f"{RTL}لم يتم اختيار أي عنصر.")
            return

        confirm = messagebox.askyesno("تأكيد", f"{RTL}⚠️ هل تريد حذف {len(sel)} عنصر مؤقتاً؟")
        if confirm:
            for i in sel:
                doc = docs[i]
                collection.update_one({"_id": doc["_id"]}, {"$set": {"deleted": True}})
            messagebox.showinfo("✅", f"{RTL}تم نقل {len(sel)} عنصر إلى سلة المحذوفات.")
            win.destroy()

 
    tk.Button(win, text=f"{RTL}📌 تحديد الكل", font=APP_FONT, command=select_all).pack(pady=5)
    tk.Button(win, text=f"{RTL}🗑️ حذف المحدد (مؤقت)", font=APP_FONT, command=delete_selected).pack(pady=10)


def show_deleted():
    docs = list(collection.find({"deleted": True}))
    if not docs:
        messagebox.showinfo("♻️", f"{RTL}⚠️ لا توجد عناصر محذوفة.")
        return

    win = tk.Toplevel(root)
    win.title("♻️ العناصر المحذوفة")
    win.geometry("700x600")

    listbox = tk.Listbox(win, width=100, height=15, font=APP_FONT, justify="right", selectmode=tk.MULTIPLE)
    listbox.pack(pady=10, padx=10, fill="both", expand=True)

    for d in docs:
        listbox.insert("end", f"{d['_id']} | {d.get('question', '')}")

    def select_all():
        listbox.select_set(0, tk.END)

    def restore_selected():
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("⚠️", f"{RTL}لم يتم اختيار أي عنصر.")
            return
        for i in sel:
            doc = docs[i]
            collection.update_one({"_id": doc["_id"]}, {"$set": {"deleted": False}})
        messagebox.showinfo("✅", f"{RTL}تم استرجاع {len(sel)} عنصر.")
        win.destroy()

    def delete_forever():
        sel = listbox.curselection()
        if not sel:
            messagebox.showinfo("⚠️", f"{RTL}لم يتم اختيار أي عنصر.")
            return
        confirm = messagebox.askyesno("تأكيد", f"{RTL}⚠️ هل تريد حذف {len(sel)} عنصر نهائياً؟")
        if confirm:
            for i in sel:
                doc = docs[i]
                collection.delete_one({"_id": doc["_id"]})
            messagebox.showinfo("✅", f"{RTL}تم حذف {len(sel)} عنصر نهائياً.")
            win.destroy()

    # أزرار التحكم
    tk.Button(win, text=f"{RTL}📌 تحديد الكل", font=APP_FONT, command=select_all).pack(pady=5)
    tk.Button(win, text=f"{RTL}♻️ استرجاع المحدد", font=APP_FONT, command=restore_selected).pack(pady=5)
    tk.Button(win, text=f"{RTL}❌ حذف نهائي", font=APP_FONT, command=delete_forever).pack(pady=5)


def search_entry():
    keyword = simpledialog.askstring("🔍 بحث", f"{RTL}أدخل كلمة (سؤال/تصنيف/إجابة) للبحث:")
    if not keyword: return

    docs = list(collection.find({
        "$or": [
            {"category": {"$regex": keyword, "$options": "i"}},
            {"question": {"$regex": keyword, "$options": "i"}},
            {"answer": {"$regex": keyword, "$options": "i"}}
        ]
    }))

    if not docs:
        messagebox.showinfo("🔍 نتيجة البحث", f"{RTL}❌ لا توجد نتائج عن: {keyword}")
        return

    win = tk.Toplevel(root)
    win.title(f"🔍 نتائج البحث: {keyword}")
    win.geometry("800x600")

    txt = tk.Text(win, font=APP_FONT, wrap="word")
    txt.tag_configure("rtl", justify="right")
    txt.pack(fill="both", expand=True)

    for i, d in enumerate(docs, start=1):
        txt.insert("end", f"{RTL}— نتيجة {i} —\n{pretty_doc(d)}\n\n", "rtl")

    txt.config(state="disabled")



def login():
    for attempt in range(3):
        pw = simpledialog.askstring("تسجيل الدخول", f"{RTL}أدخل كلمة المرور:", show="*")
        if pw is None: return False
        if pw == DB_PASS:
            return True
        else:
            messagebox.showwarning("خطأ", f"{RTL}❌ كلمة المرور غير صحيحة (محاولة {attempt + 1}/3)")
    return False
def choose_collection():
    global active_collection
    global collection, APP_COLLECTION_NAME
    collections = db.list_collection_names()
    if not collections:
        messagebox.showerror("⚠️", f"{RTL}لا توجد Collections في قاعدة البيانات.")
        root.destroy()
        return False

    win = tk.Toplevel(root)
    win.title("اختيار Collection")
    win.geometry("400x400")
    win.grab_set()

    lbl = tk.Label(win, text=f"{RTL}📂 اختر الـ Collection:", font=APP_FONT, anchor="e", justify="right")
    lbl.pack(pady=10)

    listbox = tk.Listbox(win, font=APP_FONT, height=5, justify="right")
    listbox.pack(pady=10, padx=20, fill="both", expand=True)

    for c in collections:
        listbox.insert("end", c)

    selected = {"name": None}

    def confirm():
        sel = listbox.curselection()
        if sel:
            selected["name"] = listbox.get(sel[0])
            win.destroy()
        else:
            messagebox.showwarning("⚠️", f"{RTL}يجب اختيار Collection أولاً.")

    def cancel():
        win.destroy()

    tk.Button(win, text="✔ موافق", font=APP_FONT, command=confirm).pack(pady=5)
    tk.Button(win, text="❌ إلغاء", font=APP_FONT, command=cancel).pack(pady=5)

    win.wait_window()
    if not selected["name"]:
        root.destroy()
        return False

    APP_COLLECTION_NAME = selected["name"]
    collection = db[APP_COLLECTION_NAME]

    build_buttons()
    return True


def change_collection():
    if choose_collection():
        messagebox.showinfo("✅", f"{RTL}تم تغيير الـ Collection إلى: {APP_COLLECTION_NAME}")


def build_buttons():
   
    for widget in frame.winfo_children():
        widget.destroy()
        

    if APP_COLLECTION_NAME == "conversations":
        buttons = [
            ("عرض البيانات 📋", show_all),
            ("🗑️ حذف مدخل", delete_entry),
            ("♻️ عرض المحذوفات", show_deleted),
            (" تغيير Collection 🔄", change_collection),
            ("خروج 🚪", root.quit),
        ]
    else: 
        buttons = [
            ("عرض البيانات 📋", show_all),
            ("➕ إضافة مدخل واحد", insert_single),
            ("إدخال من data.json 📥", insert_from_json),
            ("🗑️ حذف مدخل", delete_entry),
            ("♻️ عرض المحذوفات", show_deleted),
            ("✏️ تعديل مدخل", update_entry),
            ("البحث عن مدخل 🔍", search_entry),
            (" تغيير Collection 🔄", change_collection),
            ("خروج 🚪", root.quit),
        ]

    for text, cmd in buttons:
        tk.Button(frame, text=f"{RTL}{text}", font=APP_FONT, width=35, command=cmd).pack(pady=5)


root = tk.Tk()
root.title("إدارة قاعدة بيانات الشات بوت")
root.geometry("500x600")

global frame
frame = tk.Frame(root)
frame.pack(pady=20)




root.withdraw()
if login():
    try:
        connect_db()
        if not choose_collection():
            exit()
        messagebox.showinfo("✅", f"{RTL}تم تسجيل الدخول والاتصال بقاعدة البيانات بنجاح.")
        root.deiconify()
    except Exception as e:
        messagebox.showerror("خطأ", f"{RTL}⚠️ فشل الاتصال بقاعدة البيانات.\n{e}")
        root.destroy()
else:
    messagebox.showerror("خروج", f"{RTL}فشل تسجيل الدخول.")
    root.destroy()

root.mainloop()
