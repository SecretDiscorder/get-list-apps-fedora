import os
import glob
import configparser
from collections import defaultdict
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from os.path import basename

# Initialize Qt application (required for QIcon)
app = QApplication([])

# Settings
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm
ICON_SIZE = 20 * mm
TEXT_HEIGHT = 7 * mm
LINE_HEIGHT = ICON_SIZE + 5 * mm
FONT_SIZE = 9
CATEGORY_FONT_SIZE = 12

# Directories
app_dirs = {
    'Flatpak': os.path.expanduser('~/.local/share/flatpak/exports/share/applications'),
    'Snap': '/var/lib/snapd/desktop/applications',
    'RPM': '/usr/share/applications'
}

def find_windows_installer_icon():
    candidates = [
        "/var/lib/snapd/snap/gtk-common-themes/current/share/icons/Yaru/48x48/mimetypes/application-x-ms-dos-executable.png",
        "/usr/share/icons/Paper/48x48/mimetypes/gnome-mime-application-x-ms-dos-executable.png",
        "/usr/share/icons/Mint-X/mimetypes/48/application-x-ms-dos-executable.png"
    ]
    for path in candidates:
        if os.path.exists(path):
            print(f"[find_icon] Menggunakan ikon Windows Installer dari {path}")
            return path
    print("[find_icon] Ikon Windows Installer tidak ditemukan di lokasi prioritas")
    return None
def extract_description(entry, file_path, source):
    comment = entry.get('Comment', '')
    generic = entry.get('GenericName', '')
    version = entry.get('Version', '')
    description = comment or generic or ''

    # Tambahkan versi jika tersedia
    version_info = ''
    name_field = entry.get('Name', '').strip()

    if source == 'Flatpak':
        try:
            out = subprocess.check_output(['flatpak', 'info', name_field], stderr=subprocess.DEVNULL).decode()
            for line in out.splitlines():
                if line.startswith("Version:"):
                    version_info = line.split(":", 1)[1].strip()
                    break
        except:
            pass
    elif source == 'Snap':
        try:
            out = subprocess.check_output(['snap', 'info', name_field], stderr=subprocess.DEVNULL).decode()
            for line in out.splitlines():
                if line.strip().startswith("installed:"):
                    version_info = line.split()[1]
                    break
        except:
            pass
    elif source == 'RPM':
        try:
            pkg_name = os.path.splitext(os.path.basename(file_path))[0]
            out = subprocess.check_output(['rpm', '-qi', pkg_name], stderr=subprocess.DEVNULL).decode()
            for line in out.splitlines():
                if line.startswith("Version"):
                    version_info = line.split(":", 1)[1].strip()
                    break
        except:
            pass

    # Gabungkan
    if version_info:
        description = f"{description} | Versi: {version_info}" if description else f"Versi: {version_info}"
    elif version:
        description = f"{description} | Versi: {version}" if description else f"Versi: {version}"

    return description.strip()

def find_icon(icon_name):
    # Custom mapping ikon khusus hasil pencarian dan klarifikasi
    custom_icon_map = {
        "vlc": "/usr/share/icons/hicolor/48x48/apps/vlc.png",
        "audacious": "/usr/share/icons/hicolor/48x48/apps/audacious.png",
        "org.gnome.NetworkDisplays": "/usr/share/icons/hicolor/48x48/apps/org.gnome.NetworkDisplays.png",
        "org.kde.krecorder": "/usr/share/icons/hicolor/48x48/apps/org.kde.krecorder.png",
        "simplescreenrecorder": "/usr/share/icons/hicolor/48x48/apps/simplescreenrecorder.png",
        "multimedia-volume-control": "/usr/share/icons/hicolor/48x48/apps/audio-volume-high.png",
        "java-21-openjdk": "/usr/share/icons/hicolor/48x48/apps/java.png",
        "unityhub": "/usr/share/pixmaps/unityhub.png",
        "org.gnome.Calendar": "/usr/share/icons/hicolor/48x48/apps/org.gnome.Calendar.png",
        "org.gnome.Maps": "/usr/share/icons/hicolor/48x48/apps/org.gnome.Maps.png",
        "org.kde.kclock": "/usr/share/icons/hicolor/48x48/apps/kclock.png",
        "digikam": "/usr/share/icons/hicolor/48x48/apps/digikam.png",
        "kdenlive": "/usr/share/icons/hicolor/48x48/apps/kdenlive.png",
        "krita": "/usr/share/icons/hicolor/48x48/apps/krita.png",
        "firefox": "/usr/share/icons/hicolor/48x48/apps/firefox.png",
        "chromium-browser": "/usr/share/icons/hicolor/48x48/apps/chromium.png",
        "gparted": "/usr/share/icons/hicolor/48x48/apps/gparted.png",
        "leafpad": "/usr/share/pixmaps/leafpad.png",
        "lxterminal": "/usr/share/pixmaps/lxterminal.png",
        "libreoffice-writer": "/usr/share/icons/hicolor/48x48/apps/libreoffice-writer.png",
        "libreoffice-calc": "/usr/share/icons/hicolor/48x48/apps/libreoffice-calc.png",
        "libreoffice-draw": "/usr/share/icons/hicolor/48x48/apps/libreoffice-draw.png",
        "libreoffice-impress": "/usr/share/icons/hicolor/48x48/apps/libreoffice-impress.png",
        "libreoffice-base": "/usr/share/icons/hicolor/48x48/apps/libreoffice-base.png",
        "okular": "/usr/share/icons/hicolor/48x48/apps/okular.png",
        "org.kde.dolphin": "/usr/share/icons/hicolor/48x48/apps/system-file-manager.png",
        "disk-space-saver": "/var/lib/snapd/snap/easy-disk-cleaner/current/meta/gui/icon.png",
        "ppsspp-emu": "/var/lib/snapd/snap/ppsspp-emu/current/meta/gui/icon.png",
        "quran-hadith": "/var/lib/snapd/snap/quran-hadith/current/meta/gui/Logo.png",
        "mtpaint": "/usr/share/pixmaps/mtpaint.png",
        "rawstudio": "/usr/share/icons/rawstudio.png",
        "nvidia-settings": "/usr/share/pixmaps/nvidia-settings.png",
        "tkiaxphone": "/usr/share/pixmaps/tkiaxphone.png",
        "easy-disk-cleaner": "/var/lib/snapd/snap/easy-disk-cleaner/current/meta/gui/icon.png",
    }
    if icon_name in ["windows-installer", "disk-space-saver", "ppsspp-emu", "quran-hadith"]:
        path = custom_icon_map.get(icon_name)
        if path and os.path.exists(path):
            print(f"[find_icon] Khusus: menggunakan custom icon untuk {icon_name} -> {path}")
            return path
    if icon_name == "windows-installer":
        path_candidates = [
            "/usr/share/icons/hicolor/48x48/mimetypes/application-x-msdos-program.png",
            "/usr/share/icons/hicolor/48x48/mimetypes/application-x-msdos-executable.png",
        ]
        for path in path_candidates:
            if os.path.exists(path):
                print(f"[find_icon] Menggunakan ikon Windows Installer dari {path}")
                return path
        print("[find_icon] Ikon Windows Installer tidak ditemukan di lokasi standar")
        return None
    # Coba ambil dari custom map lain (non-khusus)
    if icon_name in custom_icon_map:
        path = custom_icon_map[icon_name]
        if os.path.exists(path):
            print(f"[find_icon] Menggunakan custom icon untuk {icon_name}: {path}")
            return path

    # Ambil dari tema ikon sistem
    icon = QIcon.fromTheme(icon_name)
    if not icon.isNull():
        pixmap = icon.pixmap(int(ICON_SIZE), int(ICON_SIZE))
        if not pixmap.isNull():
            basename_icon = basename(icon_name)
            if not basename_icon.lower().endswith('.png'):
                basename_icon += '.png'
            path = f"/tmp/{basename_icon}"
            pixmap.save(path)
            try:
                img = Image.open(path).convert("RGBA")
                img.save(path, icc_profile=None)
            except Exception as e:
                print(f"[find_icon] Warning: gagal hapus ICC profile di {path}: {e}")
            print(f"[find_icon] Dapatkan icon tema untuk {icon_name} di {path}")
            return path

    # Cari ikon Snap sebagai alternatif
    snap_icon_dirs = [
        os.path.expanduser("~/.local/share/icons/"),
        "/var/lib/snapd/desktop/icons/",
    ]
    for icon_dir in snap_icon_dirs:
        for ext in ['.png', '.svg']:
            full_path = os.path.join(icon_dir, f"{icon_name}{ext}")
            if os.path.exists(full_path):
                print(f"[find_icon] Dapatkan icon Snap untuk {icon_name} di {full_path}")
                return full_path

    # Fallback ikon umum
    fallback_icon = "./Unduhan/terminal.png"
    if os.path.exists(fallback_icon):
        print(f"[find_icon] Gunakan fallback icon di {fallback_icon}")
        return fallback_icon

    print(f"[find_icon] Icon tidak ditemukan untuk {icon_name}")
    return None

# Kumpulkan aplikasi berdasarkan kategori dan pisahkan berdasar ada icon atau tidak
apps_with_icon = defaultdict(list)
apps_without_icon = defaultdict(list)

for source, path in app_dirs.items():
    if not os.path.isdir(path):
        continue
    for file in glob.glob(os.path.join(path, '*.desktop')):
        config = configparser.ConfigParser(interpolation=None)
        try:
            config.read(file, encoding='utf-8')
            if 'Desktop Entry' not in config:
                continue
            entry = config['Desktop Entry']
            if entry.get('NoDisplay', 'false').lower() == 'true':
                continue
            name = entry.get('Name', 'Unknown')
            icon_name = entry.get('Icon', '')
            description = extract_description(entry, file, source)
            terminal = entry.get('Terminal', 'false').lower() == 'true'
            categories = entry.get('Categories', 'Other').split(';')
            main_cat = categories[0] if categories else 'Other'

            # Terminal apps masuk ke no icon meskipun punya icon
            if terminal:
                apps_without_icon[main_cat].append((name, source, ''))
                continue

            icon_path = find_icon(icon_name)
            if icon_path:
                apps_with_icon[main_cat].append((name, icon_path, source, entry.get('Comment', '')))
            else:
                apps_without_icon[main_cat].append((name, source, ''))



        except Exception:
            continue

# Tambahan: cari aplikasi CLI yang tidak ada di daftar .desktop
import subprocess

def get_executables_in_path():
    executables = set()
    for path_dir in os.environ.get('PATH', '').split(os.pathsep):
        if os.path.isdir(path_dir):
            for fname in os.listdir(path_dir):
                fpath = os.path.join(path_dir, fname)
                if os.access(fpath, os.X_OK) and not os.path.isdir(fpath):
                    executables.add(fname)
    return executables

# Ambil semua nama aplikasi dari desktop files yang sudah di-scan
apps_desktop_names = set()
for cat_apps in apps_with_icon.values():
    for app in cat_apps:
        name = app[0]
        apps_desktop_names.add(name)

for cat_apps in apps_without_icon.values():
    for app in cat_apps:
        name = app[0]
        apps_desktop_names.add(name)

# Cari executable CLI yang tidak ada di daftar desktop apps
cli_apps_only = []
executables = get_executables_in_path()
for exe in executables:
    if exe not in apps_desktop_names:
        cli_apps_only.append(exe)

# Masukkan CLI-only apps ke kategori "CLI Only" tanpa icon
for cli_app in sorted(cli_apps_only):
    apps_without_icon["CLI Only"].append((cli_app, "PATH", ''))


# ======================= fungsi baru untuk generate tabel =======================

def generate_pdf_table(filename, apps_with_icon, apps_without_icon):
    c = canvas.Canvas(filename, pagesize=A4)
    x, y = MARGIN, PAGE_HEIGHT - MARGIN

    col_icon_w = ICON_SIZE + 4 * mm
    col_name_w = 90 * mm
    col_source_w = PAGE_WIDTH - MARGIN*2 - col_icon_w - col_name_w
    row_height = ICON_SIZE + 3 * mm

    DEFAULT_ICON_PATH = "./Unduhan/terminal.png"

    def draw_table_header(title, y):
        c.setFont("Helvetica-Bold", CATEGORY_FONT_SIZE)
        c.drawString(x, y, f"\U0001F4C2 {title}")
        return y - row_height

    def draw_row(y, icon_path, name, source, description=''):
    # Gambar ikon jika tersedia
        try:
            if icon_path and os.path.exists(icon_path):
                img = Image.open(icon_path).convert("RGBA")
            else:
                img = Image.open(DEFAULT_ICON_PATH).convert("RGBA")
            img = img.resize((int(ICON_SIZE), int(ICON_SIZE)))
            img_io = ImageReader(img)
            c.drawImage(img_io, x, y - ICON_SIZE + 2, width=ICON_SIZE, height=ICON_SIZE)
        except Exception as e:
            print(f"[draw_row] Gagal load icon {icon_path} untuk {name}: {e}")

    # Gambar nama aplikasi
        c.setFont("Helvetica", FONT_SIZE)
        c.drawString(x + col_icon_w, y - ICON_SIZE / 2 + 4, name)

    # Gambar sumber aplikasi
        c.setFont("Helvetica-Oblique", FONT_SIZE - 1)
        c.drawString(x + col_icon_w + col_name_w, y - ICON_SIZE / 2 + 4, f"({source})")

    # Gambar deskripsi jika ada
        if description:
            c.setFont("Helvetica-Oblique", FONT_SIZE - 1)
            c.drawString(x + col_icon_w, y - ICON_SIZE / 2 - 4, description)
            c.setFont("Helvetica", FONT_SIZE)

        return y - row_height

    # Bagian 1: apps dengan ikon
    for category in sorted(apps_with_icon):
        y = draw_table_header(f"{category} (With Icon)", y)
        c.setFont("Helvetica", FONT_SIZE)

        for name, icon_path, source, description in apps_with_icon[category]:
            y = draw_row(y, icon_path, name, source, description)

            if y < MARGIN + row_height:
                c.showPage()
                y = PAGE_HEIGHT - MARGIN

        y -= row_height
        if y < MARGIN + row_height:
            c.showPage()
            y = PAGE_HEIGHT - MARGIN

    # Bagian 2: apps tanpa ikon
    for category in sorted(apps_without_icon):
        y = draw_table_header(f"{category} (No Icon)", y)
        c.setFont("Helvetica", FONT_SIZE)

        for name, source, description in apps_without_icon[category]:
            y = draw_row(y, None, name, source, description)

            if y < MARGIN + row_height:
                c.showPage()
                y = PAGE_HEIGHT - MARGIN

        y -= row_height
        if y < MARGIN + row_height:
            c.showPage()
            y = PAGE_HEIGHT - MARGIN

    c.save()

# Panggil fungsi baru generate_pdf_table() untuk output PDF tabel
generate_pdf_table("output.pdf", apps_with_icon, apps_without_icon)
