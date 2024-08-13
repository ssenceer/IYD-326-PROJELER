from tkinter import Tk, Label, Entry, Button, Listbox, END, Toplevel, StringVar, OptionMenu, W
import sqlite3

class Urun:
    def __init__(self, ad, fiyat, kategori):
        self.ad = ad
        self.fiyat = fiyat
        self.kategori = kategori

    def __str__(self):
        return f"{self.ad} - {self.fiyat:.2f} ({self.kategori})"

class EnvanterYonetimSistemi:
    def __init__(self, master):
        self.master = master
        master.title("Envanter Yönetim Sistemi")

        # Veritabanı bağlantısı
        self.vt_baglanti = sqlite3.connect("envanter.db")
        self.imlec = self.vt_baglanti.cursor()
        self.imlec.execute("""CREATE TABLE IF NOT EXISTS urunler (
                                ad TEXT PRIMARY KEY,
                                fiyat REAL,
                                kategori TEXT
                            )""")

        # Etiketler ve giriş alanları
        self.urun_adi_etiket = Label(master, text="Ürün Adı:")
        self.urun_adi_etiket.grid(row=0, column=0)
        self.urun_adi_giris = Entry(master)
        self.urun_adi_giris.grid(row=0, column=1)

        self.urun_fiyati_etiket = Label(master, text="Ürün Fiyatı:")
        self.urun_fiyati_etiket.grid(row=1, column=0)
        self.urun_fiyati_giris = Entry(master)
        self.urun_fiyati_giris.grid(row=1, column=1)

        # Kategori seçimi
        self.kategori_etiket = Label(master, text="Kategori:")
        self.kategori_etiket.grid(row=2, column=0)
        self.kategori_degisken = StringVar(master)
        self.kategori_degisken.set("Elektronik")  # Varsayılan kategori
        self.kategori_secenekleri = ["Elektronik", "Giyim", "Ev Eşyaları"]
        self.kategori_acilir_menu = OptionMenu(master, self.kategori_degisken, *self.kategori_secenekleri)
        self.kategori_acilir_menu.grid(row=2, column=1, sticky=W)

        # Butonlar
        self.ekle_buton = Button(master, text="Ekle", command=self.urun_ekle)
        self.ekle_buton.grid(row=3, column=0)

        self.guncelle_buton = Button(master, text="Güncelle", command=self.urun_guncelle)
        self.guncelle_buton.grid(row=3, column=1)

        self.sil_buton = Button(master, text="Sil", command=self.urun_sil)
        self.sil_buton.grid(row=3, column=2)

        self.listele_buton = Button(master, text="Tüm Ürünleri Listele", command=self.urunleri_listele)
        self.listele_buton.grid(row=4, column=0, columnspan=3)

        # Liste kutusu
        self.urun_listesi = Listbox(master, width=50)
        self.urun_listesi.grid(row=5, column=0, columnspan=3)

        self.urunleri_listele()  # Başlangıçta veritabanındaki ürünleri listele

    def urun_ekle(self):
        urun_adi = self.urun_adi_giris.get()
        urun_fiyati = self.urun_fiyati_giris.get()
        kategori = self.kategori_degisken.get()

        try:
            yeni_urun = Urun(urun_adi, float(urun_fiyati), kategori)
            self.imlec.execute("INSERT INTO urunler VALUES (?, ?, ?)", (yeni_urun.ad, yeni_urun.fiyat, yeni_urun.kategori))
            self.vt_baglanti.commit()
            self.urun_listesi.insert(END, str(yeni_urun))

            # Giriş alanlarını temizle
            self.urun_adi_giris.delete(0, END)
            self.urun_fiyati_giris.delete(0, END)
        except ValueError:
            print("Ürün fiyatı sayısal olmalı.")
        except sqlite3.IntegrityError:
            print("Bu ürün adı zaten mevcut.")

    def urun_guncelle(self):
        secilen_urun = self.urun_listesi.curselection()
        if secilen_urun:
            urun_adi = self.urun_listesi.get(secilen_urun).split(" - ")[0]
            self.urun_guncelleme_pencere(urun_adi)
        else:
            print("Güncellenecek bir ürün seçin.")

    def urun_guncelleme_pencere(self, urun_adi):
        pencere = Toplevel(self.master)
        pencere.title("Ürün Güncelle")

        self.imlec.execute("SELECT * FROM urunler WHERE ad=?", (urun_adi,))
        urun_bilgileri = self.imlec.fetchone()

        urun_adi_etiket = Label(pencere, text="Ürün Adı:")
        urun_adi_etiket.grid(row=0, column=0)
        urun_adi_giris = Entry(pencere)
        urun_adi_giris.insert(0, urun_bilgileri[0])
        urun_adi_giris.config(state="readonly")  # Ürün adını düzenlemeye kapat
        urun_adi_giris.grid(row=0, column=1)

        urun_fiyati_etiket = Label(pencere, text="Yeni Fiyat:")
        urun_fiyati_etiket.grid(row=1, column=0)
        urun_fiyati_giris = Entry(pencere)
        urun_fiyati_giris.insert(0, urun_bilgileri[1])
        urun_fiyati_giris.grid(row=1, column=1)

        kategori_etiket = Label(pencere, text="Yeni Kategori:")
        kategori_etiket.grid(row=2, column=0)
        kategori_degisken = StringVar(pencere)
        kategori_degisken.set(urun_bilgileri[2])
        kategori_acilir_menu = OptionMenu(pencere, kategori_degisken, *self.kategori_secenekleri)
        kategori_acilir_menu.grid(row=2, column=1, sticky=W)

        kaydet_buton = Button(pencere, text="Kaydet", command=lambda: self.guncellemeyi_kaydet(urun_adi, urun_fiyati_giris.get(), kategori_degisken.get(), pencere))
        kaydet_buton.grid(row=3, column=0, columnspan=2)

    def guncellemeyi_kaydet(self, urun_adi, yeni_fiyat, yeni_kategori, pencere):
        try:
            self.imlec.execute("UPDATE urunler SET fiyat=?, kategori=? WHERE ad=?", (float(yeni_fiyat), yeni_kategori, urun_adi))
            self.vt_baglanti.commit()
            self.urunleri_listele()  # Listeyi güncelle
            pencere.destroy()
        except ValueError:
            print("Ürün fiyatı sayısal olmalı.")

    def urun_sil(self):
        secilen_urun = self.urun_listesi.curselection()
        if secilen_urun:
            urun_adi = self.urun_listesi.get(secilen_urun).split(" - ")[0]
            self.imlec.execute("DELETE FROM urunler WHERE ad=?", (urun_adi,))
            self.vt_baglanti.commit()
            self.urunleri_listele()  # Listeyi güncelle
        else:
            print("Silinecek bir ürün seçin.")

    def urunleri_listele(self):
        self.urun_listesi.delete(0, END)
        self.imlec.execute("SELECT * FROM urunler")
        urunler = self.imlec.fetchall()
        for urun in urunler:
            self.urun_listesi.insert(END, f"{urun[0]} - {urun[1]:.2f} ({urun[2]})")

root = Tk()
envanter_sistemi = EnvanterYonetimSistemi(root)
root.mainloop()