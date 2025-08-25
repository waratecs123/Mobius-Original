import qrcode
from PIL import Image, ImageOps
import os
import random
import webbrowser
from datetime import datetime
import io
import pyperclip
import zxingcpp
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser


class QRCodeFunctions:
    def __init__(self, gui):
        self.gui = gui
        self.current_qr = None
        self.qr_logo = None

        # Настройки по умолчанию
        self.settings = {
            "qr_size": 300,
            "qr_version": 1,
            "qr_error_correction": qrcode.constants.ERROR_CORRECT_H,
            "qr_fill_color": "#000000",
            "qr_back_color": "#FFFFFF",
            "qr_border": 4,
            "qr_data": "https://example.com",
            "qr_type": "URL"
        }

    def update_content_fields(self, event=None):
        try:
            content_type = self.gui.content_type.get()
            self.gui.data_entry.delete("1.0", tk.END)

            if content_type == "URL":
                self.gui.data_entry.insert("1.0", "https://example.com")
            elif content_type == "Text":
                self.gui.data_entry.insert("1.0", "Sample text for QR code")
            elif content_type == "vCard":
                self.gui.data_entry.insert("1.0",
                                           "BEGIN:VCARD\nVERSION:3.0\nN:Last;First\nORG:Company\nTEL:+1234567890\nEMAIL:email@example.com\nEND:VCARD")
            elif content_type == "WiFi":
                self.gui.data_entry.insert("1.0", "WIFI:T:WPA;S:MyWiFi;P:password;;")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update fields: {str(e)}")

    def choose_color(self, color_type):
        try:
            color = colorchooser.askcolor(title=f"Выберите цвет {'кода' if color_type == 'fill' else 'фона'}")
            if color[1]:
                if color_type == "fill":
                    self.settings["qr_fill_color"] = color[1]
                    self.gui.color_btn.config(bg=color[1], fg="#ffffff" if self.is_dark(color[1]) else "#000000")
                else:
                    self.settings["qr_back_color"] = color[1]
                    self.gui.bg_color_btn.config(bg=color[1], fg="#ffffff" if self.is_dark(color[1]) else "#000000")
                self.generate_qr()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выбрать цвет: {str(e)}")

    def is_dark(self, hex_color):
        try:
            # Преобразуем HEX в RGB
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            # Рассчитываем яркость по формуле
            brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
            return brightness < 128
        except:
            return False

    def add_logo(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
            if file_path:
                self.qr_logo = Image.open(file_path)
                messagebox.showinfo("Успех", "Логотип успешно добавлен")
                self.generate_qr()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {str(e)}")

    def remove_logo(self):
        self.qr_logo = None
        messagebox.showinfo("Успех", "Логотип удален")
        self.generate_qr()

    def generate_qr(self):
        try:
            # Получаем настройки из интерфейса
            self.settings["qr_data"] = self.gui.data_entry.get("1.0", tk.END).strip()
            self.settings["qr_size"] = int(self.gui.size_entry.get())
            self.settings["qr_border"] = int(self.gui.border_entry.get())
            self.settings["qr_version"] = int(self.gui.version_entry.get())

            # Коррекция ошибок
            correction_map = {
                "Низкая": qrcode.constants.ERROR_CORRECT_L,
                "Средняя": qrcode.constants.ERROR_CORRECT_M,
                "Высокая": qrcode.constants.ERROR_CORRECT_H,
                "Максимальная": qrcode.constants.ERROR_CORRECT_Q
            }
            self.settings["qr_error_correction"] = correction_map[self.gui.error_correction.get()]

            # Создаем QR-код
            qr = qrcode.QRCode(
                version=self.settings["qr_version"],
                error_correction=self.settings["qr_error_correction"],
                box_size=10,
                border=self.settings["qr_border"]
            )

            qr.add_data(self.settings["qr_data"])
            qr.make(fit=True)

            # Создаем изображение QR-кода
            img = qr.make_image(
                fill_color=self.settings["qr_fill_color"],
                back_color=self.settings["qr_back_color"]
            ).convert('RGB')

            # Добавляем логотип, если есть
            if self.qr_logo:
                # Масштабируем логотип
                logo_size = min(img.size[0] // 4, img.size[1] // 4)
                logo = self.qr_logo.resize((logo_size, logo_size))

                # Позиционируем логотип по центру
                pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)

                # Создаем белую подложку для логотипа
                mask = Image.new('L', logo.size, 255)
                img.paste(logo, pos, mask)

            # Масштабируем изображение для отображения
            img.thumbnail((self.settings["qr_size"], self.settings["qr_size"]))
            self.current_qr = img

            # Отображаем QR-код
            self.gui.display_qr(img)

            # Обновляем информацию
            self.gui.qr_info.config(
                text=f"Размер: {img.size[0]}x{img.size[1]} | Тип: {self.gui.content_type.get()} | Данные: {self.settings['qr_data'][:30]}..."
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать QR-код: {str(e)}")

    def generate_random_qr(self):
        try:
            # Генерируем случайные данные
            content_type = random.choice(["URL", "Текст", "vCard", "WiFi"])
            self.gui.content_type.set(content_type)
            self.update_content_fields()

            # Случайные цвета
            colors = ["#000000", "#FF0000", "#00FF00", "#0000FF", "#FF00FF", "#00FFFF", "#FFA500"]
            self.settings["qr_fill_color"] = random.choice(colors)
            self.gui.color_btn.config(bg=self.settings["qr_fill_color"],
                                    fg="#ffffff" if self.is_dark(self.settings["qr_fill_color"]) else "#000000")

            # Генерируем QR-код
            self.generate_qr()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать случайный QR-код: {str(e)}")

    def export_png(self):
        if not self.current_qr:
            messagebox.showerror("Ошибка", "Нет QR-кода для экспорта")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=f"qr_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )

            if file_path:
                # Создаем полноразмерное изображение без масштабирования
                qr = qrcode.QRCode(
                    version=self.settings["qr_version"],
                    error_correction=self.settings["qr_error_correction"],
                    box_size=20,
                    border=self.settings["qr_border"]
                )
                qr.add_data(self.settings["qr_data"])
                qr.make(fit=True)

                img = qr.make_image(
                    fill_color=self.settings["qr_fill_color"],
                    back_color=self.settings["qr_back_color"]
                ).convert('RGB')

                # Добавляем логотип, если есть
                if self.qr_logo:
                    logo_size = min(img.size[0] // 4, img.size[1] // 4)
                    logo = self.qr_logo.resize((logo_size, logo_size))
                    pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
                    mask = Image.new('L', logo.size, 255)
                    img.paste(logo, pos, mask)

                img.save(file_path)
                messagebox.showinfo("Успех", f"QR-код успешно сохранен как {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def export_svg(self):
        if not self.current_qr:
            messagebox.showerror("Ошибка", "Нет QR-кода для экспорта")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".svg",
                filetypes=[("SVG files", "*.svg"), ("All files", "*.*")],
                initialfile=f"qr_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg"
            )

            if file_path:
                qr = qrcode.QRCode(
                    version=self.settings["qr_version"],
                    error_correction=self.settings["qr_error_correction"],
                    box_size=10,
                    border=self.settings["qr_border"]
                )
                qr.add_data(self.settings["qr_data"])
                qr.make(fit=True)

                # Создаем SVG файл
                factory = qrcode.image.svg.SvgPathImage
                img = qr.make_image(
                    image_factory=factory,
                    fill_color=self.settings["qr_fill_color"],
                    back_color=self.settings["qr_back_color"]
                )

                img.save(file_path)
                messagebox.showinfo("Успех", f"QR-код успешно сохранен как {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def copy_to_clipboard(self):
        if not self.current_qr:
            messagebox.showerror("Ошибка", "Нет QR-кода для копирования")
            return

        try:
            # Создаем временный файл в памяти
            output = io.BytesIO()
            self.current_qr.save(output, format="PNG")
            output.seek(0)

            # Копируем изображение в буфер обмена
            self.gui.root.clipboard_clear()
            self.gui.root.clipboard_append(output.getvalue(), type='image/png')
            messagebox.showinfo("Успех", "QR-код скопирован в буфер обмена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скопировать QR-код: {str(e)}")

    def load_image_for_scan(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
            if file_path:
                img = Image.open(file_path)

                # Отображаем изображение
                self.gui.display_scan_image(img)

                # Сканируем QR-код
                results = zxingcpp.read_barcodes(img)

                if results:
                    self.gui.scan_result.delete("1.0", tk.END)
                    for result in results:
                        self.gui.scan_result.insert("1.0", f"Тип: {result.format}\nДанные: {result.text}\n\n")
                else:
                    self.gui.scan_result.delete("1.0", tk.END)
                    self.gui.scan_result.insert("1.0", "QR-код не обнаружен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить или сканировать изображение: {str(e)}")