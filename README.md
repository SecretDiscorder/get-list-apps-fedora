# 🖥️ Linux App Report Generator

**Generate a detailed and categorized PDF report of your installed Linux applications, complete with icons, descriptions, sources, and CLI-only apps.**

---

## 🚀 Fitur Utama

* 🔍 Memindai aplikasi dari berbagai sumber:

  * Flatpak
  * Snap
  * RPM (Desktop Entry)
* 🎨 Menampilkan ikon aplikasi dengan fallback otomatis jika tidak ditemukan.
* 🗂️ Mengelompokkan berdasarkan kategori utama (`Categories`) dari `.desktop`.
* 📝 Menampilkan deskripsi (`Comment`, `GenericName`) dan versi aplikasi.
* 📜 Menambahkan aplikasi CLI-only (yang tidak memiliki file .desktop) secara otomatis.
* 📄 Mengekspor semuanya dalam format PDF bergaya tabel.

---

## 📦 Ketergantungan

Instal pustaka berikut terlebih dahulu:

```bash
pip install PyQt5 Pillow reportlab
```

---

## ▶️ Cara Menggunakan

1. Jalankan script Python:

```bash
python3 main.py
```

2. Setelah selesai, file `output.pdf` akan dihasilkan dalam direktori saat ini.

---

## 🧩 Struktur Output

* Tabel aplikasi dengan ikon
* Tabel aplikasi tanpa ikon (termasuk aplikasi CLI-only)
* Kategori ditampilkan secara terpisah

Contoh:

```
🗂️ Multimedia (With Icon)
🎨 GIMP         | Versi: 2.10.34 | Flatpak
🎵 VLC Player   | Versi: 3.0.18  | RPM

🗂️ CLI Only (No Icon)
curl           | PATH
htop           | PATH
```

---

## ⚙️ Kustomisasi

* Tambahkan ikon manual lewat `custom_icon_map` dalam skrip.
* Ganti fallback ikon terminal di `./Unduhan/terminal.png`.
* Ubah ukuran font, margin, dan layout PDF di fungsi `generate_pdf_table()`.

---

## 📂 File Terkait

```
.
├── main.py                 # Script utama
├── output.pdf              # Output akhir
├── Unduhan/terminal.png   # Fallback icon
├── README.md               # Dokumentasi
```

---

## 📃 Lisensi

MIT License – Bebas digunakan dan dimodifikasi.

---

## 👨‍💻 Kontributor

Dikembangkan oleh seorang pengguna Linux yang mencintai otomatisasi dan dokumentasi visual sistem.

Kontribusi dan penyempurnaan sangat dihargai 🙌
