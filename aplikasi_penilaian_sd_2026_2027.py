# ================================================================
# APLIKASI PENILAIAN SD - TA 2026/2027
# Versi awal untuk Pydroid 3
# Python + Tkinter + SQLite (tanpa library tambahan)
# ================================================================

import tkinter
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from pathlib import Path
from datetime import datetime

APP_TITLE = "Aplikasi Penilaian SD - Tahun Ajaran 2026/2027"
DB_FILE = Path(__file__).with_name("penilaian_sd_2026_2027.db")

# ---------- Database ----------
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS sekolah (
    id INTEGER PRIMARY KEY,
    nama TEXT, npsn TEXT, alamat TEXT, kepala TEXT
);

CREATE TABLE IF NOT EXISTS siswa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nisn TEXT, nama TEXT NOT NULL, jk TEXT, kelas TEXT, rombel TEXT
);

CREATE TABLE IF NOT EXISTS mapel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nilai (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    siswa_id INTEGER NOT NULL,
    mapel_id INTEGER NOT NULL,
    kelas TEXT,
    semester TEXT,
    nilai_harian REAL DEFAULT 0,
    sumatif REAL DEFAULT 0,
    sas REAL DEFAULT 0,
    nilai_akhir REAL DEFAULT 0,
    predikat TEXT,
    deskripsi TEXT,
    UNIQUE(siswa_id, mapel_id, kelas, semester)
);

CREATE TABLE IF NOT EXISTS dokumen (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jenis TEXT NOT NULL,
    mapel TEXT,
    kelas TEXT,
    semester TEXT,
    isi TEXT,
    UNIQUE(jenis, mapel, kelas, semester)
);
""")
conn.commit()

# Default mapel
for nama in ["Pendidikan Agama", "Pendidikan Pancasila", "Bahasa Indonesia",
             "Matematika", "IPAS", "PJOK", "Seni", "Bahasa Inggris"]:
    cur.execute("INSERT OR IGNORE INTO mapel(nama) VALUES(?)", (nama,))
conn.commit()

# ---------- Helpers ----------
def rata(*vals):
    nums = [float(v) for v in vals if str(v).strip() != ""]
    return round(sum(nums) / len(nums), 2) if nums else 0

def predikat(n):
    try:
        n = float(n)
    except Exception:
        n = 0
    if n >= 90: return "A"
    if n >= 80: return "B"
    if n >= 70: return "C"
    return "D"

def refresh_tree(tree, rows):
    for x in tree.get_children():
        tree.delete(x)
    for row in rows:
        tree.insert("", "end", values=row)

def clear_entries(frame):
    for w in frame.winfo_children():
        if isinstance(w, (tk.Entry, ttk.Combobox)):
            try:
                w.delete(0, "end")
            except Exception:
                pass

# ---------- Main window ----------
root = tk.Tk()
root.title(APP_TITLE)
root.geometry("1000x700")
root.minsize(780, 550)

style = ttk.Style()
try:
    style.theme_use("clam")
except Exception:
    pass

style.configure("Title.TLabel", font=("helvetica", 18, "bold"))
style.configure("Head.TLabel", font=("helvetica", 12, "bold"))
style.configure("TButton", padding=6)
style.configure("Treeview", rowheight=30, font=("helvetica", 10))
style.configure("Treeview.Heading", font=("helvetica", 10, "bold"))

# ---------- Sidebar ----------
sidebar = ttk.Frame(root, padding=10)
sidebar.pack(side="left", fill="y")

content = ttk.Frame(root, padding=10)
content.pack(side="right", fill="both", expand=True)

ttk.Label(sidebar, text="PENILAIAN SD", style="Title.TLabel").pack(pady=(5,2))
ttk.Label(sidebar, text="TA 2026/2027").pack(pady=(0,15))

def show_page(page_func):
    for w in content.winfo_children():
        w.destroy()
    page_func()

buttons = [
    ("🏠 Dashboard", None),
    ("🏫 Identitas Sekolah", "sekolah"),
    ("👨‍🎓 Peserta Didik", "siswa"),
    ("📚 Mata Pelajaran", "mapel"),
    ("📊 Penilaian", "nilai"),
    ("📘 CP", "cp"),
    ("📝 TP", "tp"),
    ("🗂 ATP", "atp"),
    ("📅 Prota", "prota"),
    ("📆 Prosem", "prosem"),
    ("📋 Rekap Nilai", "rekap"),
]

# ---------- Pages ----------
def dashboard():
    for w in content.winfo_children(): w.destroy()
    ttk.Label(content, text=APP_TITLE, style="Title.TLabel").pack(anchor="w", pady=10)
    ttk.Label(content, text="Versi awal — database lokal SQLite", style="Head.TLabel").pack(anchor="w")
    ttk.Label(content, text=(
        "\nGunakan menu di sebelah kiri untuk mengelola data.\n\n"
        "Modul tersedia:\n"
        "• Identitas sekolah dan peserta didik\n"
        "• Mata pelajaran\n"
        "• Penilaian dan rekap nilai\n"
        "• CP, TP, ATP\n"
        "• Prota dan Prosem\n\n"
        "Catatan: format dokumen kurikulum pada versi ini dibuat fleksibel "
        "agar dapat disesuaikan setelah surat edaran/ketentuan resmi sekolah "
        "diberikan."
    ), wraplength=700).pack(anchor="w", pady=15)

    info = ttk.Frame(content)
    info.pack(fill="x", pady=10)
    counts = [
        ("Siswa", "SELECT COUNT(*) FROM siswa"),
        ("Mapel", "SELECT COUNT(*) FROM mapel"),
        ("Nilai", "SELECT COUNT(*) FROM nilai"),
        ("Dokumen CP/TP/ATP/Prota/Prosem", "SELECT COUNT(*) FROM dokumen"),
    ]
    for i, (label, sql) in enumerate(counts):
        cur.execute(sql)
        val = cur.fetchone()[0]
        box = ttk.LabelFrame(info, text=label, padding=15)
        box.grid(row=0, column=i, padx=5, sticky="nsew")
        ttk.Label(box, text=str(val), font=("helvetica", 20, "bold")).pack()
    for i in range(4):
        info.columnconfigure(i, weight=1)

def sekolah_page():
    ttk.Label(content, text="Identitas Sekolah", style="Title.TLabel").pack(anchor="w")
    form = ttk.Frame(content, padding=10)
    form.pack(fill="x")
    fields = {}
    labels = [("Nama Sekolah", "nama"), ("NPSN", "npsn"),
              ("Alamat", "alamat"), ("Kepala Sekolah", "kepala")]
    for r, (lab, key) in enumerate(labels):
        ttk.Label(form, text=lab).grid(row=r, column=0, sticky="w", pady=5)
        e = ttk.Entry(form, width=60)
        e.grid(row=r, column=1, sticky="ew", pady=5)
        fields[key] = e
    form.columnconfigure(1, weight=1)

    cur.execute("SELECT nama,npsn,alamat,kepala FROM sekolah WHERE id=1")
    row = cur.fetchone()
    if row:
        for (k, e), v in zip(fields.items(), row):
            e.insert(0, v or "")

    def simpan():
        vals = [fields[k].get().strip() for k in ["nama","npsn","alamat","kepala"]]
        cur.execute("""INSERT INTO sekolah(id,nama,npsn,alamat,kepala)
                       VALUES(1,?,?,?,?)
                       ON CONFLICT(id) DO UPDATE SET
                       nama=excluded.nama,npsn=excluded.npsn,
                       alamat=excluded.alamat,kepala=excluded.kepala""", vals)
        conn.commit()
        messagebox.showinfo("Berhasil", "Identitas sekolah tersimpan.")

    ttk.Button(form, text="Simpan", command=simpan).grid(row=4, column=1, sticky="w", pady=10)

def siswa_page():
    ttk.Label(content, text="Peserta Didik", style="Title.TLabel").pack(anchor="w")
    form = ttk.Frame(content, padding=5)
    form.pack(fill="x")
    entries = {}
    for i, (lab, key) in enumerate([("NISN","nisn"),("Nama","nama"),("JK","jk"),
                                     ("Kelas","kelas"),("Rombel","rombel")]):
        ttk.Label(form,text=lab).grid(row=0,column=i,sticky="w")
        e=ttk.Entry(form,width=16 if key!="nama" else 25)
        e.grid(row=1,column=i,padx=3)
        entries[key]=e

    tree = ttk.Treeview(content, columns=("id","nisn","nama","jk","kelas","rombel"),
                        show="headings")
    for c,t in zip(tree["columns"],["ID","NISN","Nama","JK","Kelas","Rombel"]):
        tree.heading(c,text=t)
    tree.pack(fill="both",expand=True,pady=10)

    def load():
        cur.execute("SELECT id,nisn,nama,jk,kelas,rombel FROM siswa ORDER BY nama")
        refresh_tree(tree, cur.fetchall())

    def simpan():
        if not entries["nama"].get().strip():
            messagebox.showwarning("Validasi","Nama siswa wajib diisi.")
            return
        cur.execute("""INSERT INTO siswa(nisn,nama,jk,kelas,rombel)
                       VALUES(?,?,?,?,?)""",
                    tuple(entries[k].get().strip() for k in entries))
        conn.commit()
        for e in entries.values(): e.delete(0,"end")
        load()

    ttk.Button(form,text="Tambah Siswa",command=simpan).grid(row=1,column=5,padx=5)
    load()

    def hapus():
        sel=tree.selection()
        if not sel: return
        sid=tree.item(sel[0],"values")[0]
        if messagebox.askyesno("Hapus","Hapus siswa terpilih?"):
            cur.execute("DELETE FROM siswa WHERE id=?",(sid,))
            cur.execute("DELETE FROM nilai WHERE siswa_id=?",(sid,))
            conn.commit(); load()
    ttk.Button(content,text="Hapus Terpilih",command=hapus).pack(anchor="e")

def mapel_page():
    ttk.Label(content,text="Mata Pelajaran",style="Title.TLabel").pack(anchor="w")
    form=ttk.Frame(content,padding=5); form.pack(fill="x")
    e=ttk.Entry(form,width=45); e.pack(side="left")
    tree=ttk.Treeview(content,columns=("id","nama"),show="headings")
    tree.heading("id",text="ID"); tree.heading("nama",text="Mata Pelajaran")
    tree.column("id",width=70); tree.pack(fill="both",expand=True,pady=10)

    def load():
        cur.execute("SELECT id,nama FROM mapel ORDER BY nama")
        refresh_tree(tree,cur.fetchall())
    def add():
        nama=e.get().strip()
        if nama:
            cur.execute("INSERT INTO mapel(nama) VALUES(?)",(nama,))
            conn.commit(); e.delete(0,"end"); load()
    ttk.Button(form,text="Tambah",command=add).pack(side="left",padx=5)
    load()

def nilai_page():
    ttk.Label(content,text="Penilaian",style="Title.TLabel").pack(anchor="w")
    form=ttk.Frame(content,padding=5); form.pack(fill="x")

    ttk.Label(form,text="Siswa").grid(row=0,column=0)
    siswa_cb=ttk.Combobox(form,width=28,state="readonly")
    siswa_cb.grid(row=1,column=0,padx=3)
    ttk.Label(form,text="Mapel").grid(row=0,column=1)
    mapel_cb=ttk.Combobox(form,width=22,state="readonly")
    mapel_cb.grid(row=1,column=1,padx=3)
    ttk.Label(form,text="Kelas").grid(row=0,column=2)
    kelas=ttk.Entry(form,width=10); kelas.grid(row=1,column=2,padx=3)
    ttk.Label(form,text="Semester").grid(row=0,column=3)
    sem=ttk.Combobox(form,values=["1","2"],width=8,state="readonly")
    sem.set("1"); sem.grid(row=1,column=3,padx=3)

    nums={}
    for j,(lab,key) in enumerate([("Harian","harian"),("Sumatif","sumatif"),("SAS","sas")],4):
        ttk.Label(form,text=lab).grid(row=0,column=j)
        x=ttk.Entry(form,width=9); x.grid(row=1,column=j,padx=3); nums[key]=x

    desc=ttk.Entry(form,width=45)
    ttk.Label(form,text="Deskripsi").grid(row=2,column=0,pady=5)
    desc.grid(row=2,column=1,columnspan=4,sticky="ew",pady=5)

    tree=ttk.Treeview(content,columns=("id","siswa","mapel","kelas","sem","h","s","sas","akhir","pred"),
                      show="headings")
    heads=["ID","Siswa","Mapel","Kelas","Sem","Harian","Sumatif","SAS","Akhir","Pred"]
    for c,t in zip(tree["columns"],heads): tree.heading(c,text=t)
    tree.pack(fill="both",expand=True,pady=10)

    cur.execute("SELECT id,nama FROM siswa ORDER BY nama")
    siswa_rows=cur.fetchall()
    siswa_map={f"{r[0]} - {r[1]}":r[0] for r in siswa_rows}
    siswa_cb["values"]=list(siswa_map)
    cur.execute("SELECT id,nama FROM mapel ORDER BY nama")
    mapel_rows=cur.fetchall()
    mapel_map={f"{r[0]} - {r[1]}":r[0] for r in mapel_rows}
    mapel_cb["values"]=list(mapel_map)

    def load():
        cur.execute("""SELECT n.id,s.nama,m.nama,n.kelas,n.semester,
                              n.nilai_harian,n.sumatif,n.sas,n.nilai_akhir,n.predikat
                       FROM nilai n JOIN siswa s ON s.id=n.siswa_id
                       JOIN mapel m ON m.id=n.mapel_id
                       ORDER BY s.nama,m.nama""")
        refresh_tree(tree,cur.fetchall())

    def simpan():
        if not siswa_cb.get() or not mapel_cb.get():
            messagebox.showwarning("Validasi","Pilih siswa dan mata pelajaran.")
            return
        try:
            h=float(nums["harian"].get() or 0)
            su=float(nums["sumatif"].get() or 0)
            sas=float(nums["sas"].get() or 0)
        except ValueError:
            messagebox.showwarning("Validasi","Nilai harus berupa angka.")
            return
        akhir=rata(h,su,sas)
        sid=siswa_map[siswa_cb.get()]; mid=mapel_map[mapel_cb.get()]
        p=predikat(akhir)
        cur.execute("""INSERT INTO nilai
            (siswa_id,mapel_id,kelas,semester,nilai_harian,sumatif,sas,nilai_akhir,predikat,deskripsi)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(siswa_id,mapel_id,kelas,semester) DO UPDATE SET
            nilai_harian=excluded.nilai_harian,sumatif=excluded.sumatif,
            sas=excluded.sas,nilai_akhir=excluded.nilai_akhir,
            predikat=excluded.predikat,deskripsi=excluded.deskripsi""",
            (sid,mid,kelas.get().strip(),sem.get(),h,su,sas,akhir,p,desc.get().strip()))
        conn.commit(); load()
        for x in nums.values(): x.delete(0,"end")
        desc.delete(0,"end")

    ttk.Button(form,text="Simpan Nilai",command=simpan).grid(row=2,column=5,pady=5)
    load()

def dokumen_page(jenis, judul):
    ttk.Label(content,text=judul,style="Title.TLabel").pack(anchor="w")
    form=ttk.Frame(content,padding=5); form.pack(fill="x")
    labels=[("Mapel","mapel"),("Kelas","kelas"),("Semester","semester")]
    es={}
    for i,(lab,key) in enumerate(labels):
        ttk.Label(form,text=lab).grid(row=0,column=i,sticky="w")
        e=ttk.Entry(form,width=20); e.grid(row=1,column=i,padx=4); es[key]=e
    ttk.Label(form,text="Isi / Materi").grid(row=2,column=0,sticky="w",pady=5)
    text=tk.Text(form,height=8,wrap="word")
    text.grid(row=3,column=0,columnspan=4,sticky="nsew",pady=5)
    form.columnconfigure(3,weight=1)

    tree=ttk.Treeview(content,columns=("id","mapel","kelas","semester","isi"),show="headings")
    for c,t in zip(tree["columns"],["ID","Mapel","Kelas","Semester","Isi"]):
        tree.heading(c,text=t)
    tree.column("isi",width=500)
    tree.pack(fill="both",expand=True,pady=10)

    def load():
        cur.execute("SELECT id,mapel,kelas,semester,isi FROM dokumen WHERE jenis=? ORDER BY id DESC",(jenis,))
        refresh_tree(tree,cur.fetchall())

    def save():
        cur.execute("""INSERT INTO dokumen(jenis,mapel,kelas,semester,isi)
                       VALUES(?,?,?,?,?)
                       ON CONFLICT(jenis,mapel,kelas,semester) DO UPDATE SET isi=excluded.isi""",
                    (jenis,es["mapel"].get().strip(),es["kelas"].get().strip(),
                     es["semester"].get().strip(),text.get("1.0","end").strip()))
        conn.commit(); load()
        for e in es.values(): e.delete(0,"end")
        text.delete("1.0","end")
    ttk.Button(form,text="Simpan",command=save).grid(row=4,column=0,pady=5)
    load()

def rekap_page():
    ttk.Label(content,text="Rekap Nilai",style="Title.TLabel").pack(anchor="w")
    ttk.Label(content,text="Data dapat disalin dari tabel atau dikembangkan menjadi ekspor Excel/PDF pada versi berikutnya.").pack(anchor="w",pady=5)
    tree=ttk.Treeview(content,columns=("siswa","mapel","kelas","sem","akhir","pred","des"),
                      show="headings")
    for c,t in zip(tree["columns"],["Siswa","Mapel","Kelas","Sem","Nilai Akhir","Predikat","Deskripsi"]):
        tree.heading(c,text=t)
    tree.column("des",width=350)
    tree.pack(fill="both",expand=True,pady=10)
    cur.execute("""SELECT s.nama,m.nama,n.kelas,n.semester,n.nilai_akhir,n.predikat,n.deskripsi
                   FROM nilai n JOIN siswa s ON s.id=n.siswa_id
                   JOIN mapel m ON m.id=n.mapel_id
                   ORDER BY s.nama,m.nama""")
    refresh_tree(tree,cur.fetchall())

pages = {
    "sekolah": sekolah_page,
    "siswa": siswa_page,
    "mapel": mapel_page,
    "nilai": nilai_page,
    "cp": lambda: dokumen_page("CP","CP — Capaian Pembelajaran"),
    "tp": lambda: dokumen_page("TP","TP — Tujuan Pembelajaran"),
    "atp": lambda: dokumen_page("ATP","ATP — Alur Tujuan Pembelajaran"),
    "prota": lambda: dokumen_page("PROTA","PROTA — Program Tahunan"),
    "prosem": lambda: dokumen_page("PROSEM","PROSEM — Program Semester"),
    "rekap": rekap_page,
}

for text, key in buttons:
    cmd = dashboard if key is None else pages[key]
    ttk.Button(sidebar,text=text,width=23,command=cmd).pack(fill="x",pady=2)

ttk.Separator(sidebar).pack(fill="x",pady=12)
ttk.Label(sidebar,text="Database:\n" + DB_FILE.name,wraplength=180).pack()

def close_app():
    conn.commit()
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_app)
dashboard()
root.mainloop()
