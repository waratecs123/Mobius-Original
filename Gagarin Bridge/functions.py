# functions.py
import os
import pandas as pd
from PIL import Image
import json
import csv
import shutil
import subprocess
import tempfile
import fitz  # PyMuPDF для работы с PDF
from docx import Document
import pythoncom
import win32com.client
import speech_recognition as sr
from pydub import AudioSegment
import wave
import contextlib
import cv2  # Для предпросмотра видео


class ConverterController:
    def __init__(self):
        # Поддерживаемые форматы
        self.supported_formats = {
            'images': ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp'],
            'data': ['csv', 'json', 'xlsx', 'xls', 'txt'],
            'documents': ['pdf', 'doc', 'docx', 'txt', 'rtf'],
            'audio': ['mp3', 'wav', 'ogg', 'flac', 'm4a', 'wma'],
            'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm']
        }

        # Маппинг форматов для PIL
        self.pil_format_mapping = {
            'jpg': 'JPEG', 'jpeg': 'JPEG', 'png': 'PNG',
            'bmp': 'BMP', 'gif': 'GIF', 'tiff': 'TIFF',
            'webp': 'WEBP'
        }

    def get_supported_formats(self):
        """Получить список всех поддерживаемых форматов"""
        all_formats = []
        for category in self.supported_formats.values():
            all_formats.extend(category)
        return sorted(all_formats)

    def get_output_formats_for_input(self, input_format):
        """Получить доступные форматы для конвертации из входного формата"""
        input_format = input_format.lower()

        # Определяем категорию входного формата
        category = None
        for cat, formats in self.supported_formats.items():
            if input_format in formats:
                category = cat
                break

        if not category:
            return []

        # Возвращаем все форматы из той же категории, кроме исходного
        return [fmt.upper() for fmt in self.supported_formats[category] if fmt != input_format]

    def auto_convert_file(self, input_path, output_dir=None, preferred_format=None, options=None, progress_callback=None):
        """Автоматическая конвертация файла в подходящий формат"""
        if options is None:
            options = {}

        input_format = os.path.splitext(input_path)[1].lower().lstrip('.')
        possible_formats = self.get_output_formats_for_input(input_format)

        if not possible_formats:
            raise ValueError(f"Нет доступных форматов для конвертации: {input_format}")

        # Выбираем формат: предпочтительный или первый доступный
        output_format = preferred_format.lower() if preferred_format and preferred_format.lower() in [f.lower() for f in possible_formats] else possible_formats[0].lower()

        if not output_dir:
            output_dir = os.path.dirname(input_path)

        output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(input_path))[0] + f".{output_format}")

        success = self.convert_file(input_path, output_path, output_format, options, progress_callback)
        return output_path if success else None

    def convert_file(self, input_path, output_path, output_format, options, progress_callback=None):
        """Конвертировать одиночный файл"""
        try:
            input_format = os.path.splitext(input_path)[1].lower().lstrip('.')
            output_format = output_format.lower()

            if progress_callback:
                progress_callback(25)

            # Определяем тип конвертации
            if input_format in self.supported_formats['images'] and output_format in self.supported_formats['images']:
                success = self._convert_image(input_path, output_path, output_format, options)
            elif input_format in self.supported_formats['data'] and output_format in self.supported_formats['data']:
                success = self._convert_data(input_path, output_path, output_format)
            elif input_format in self.supported_formats['documents'] and output_format in self.supported_formats['documents']:
                success = self._convert_document(input_path, output_path, output_format)
            elif input_format in self.supported_formats['audio'] and output_format in self.supported_formats['audio']:
                success = self._convert_audio(input_path, output_path, output_format)
            elif input_format in self.supported_formats['video'] and output_format in self.supported_formats['video']:
                success = self._convert_video(input_path, output_path, output_format)
            else:
                # Простое копирование для неподдерживаемых форматов
                success = self._copy_file(input_path, output_path)

            if progress_callback:
                progress_callback(100 if success else 0)

            return success

        except Exception as e:
            if progress_callback:
                progress_callback(0)
            raise e

    def convert_batch(self, input_dir, output_dir, output_format, options, progress_callback=None):
        """Пакетная конвертация файлов"""
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Получаем список файлов для конвертации
            files = []
            for root, _, filenames in os.walk(input_dir):
                for filename in filenames:
                    files.append(os.path.join(root, filename))

            total_files = len(files)
            if total_files == 0:
                raise ValueError("В указанной папке нет файлов для конвертации")

            success_count = 0
            for i, file_path in enumerate(files):
                try:
                    # Создаем путь для выходного файла
                    rel_path = os.path.relpath(file_path, input_dir)
                    output_path = os.path.join(output_dir, rel_path)
                    output_path = os.path.splitext(output_path)[0] + f'.{output_format}'

                    # Создаем папки если нужно
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    # Конвертируем файл
                    if self.convert_file(file_path, output_path, output_format, options):
                        success_count += 1

                    # Обновляем прогресс
                    if progress_callback:
                        progress = (i + 1) / total_files * 100
                        progress_callback(progress)

                except Exception as e:
                    print(f"Ошибка при конвертации {file_path}: {e}")
                    continue

            return success_count > 0

        except Exception as e:
            if progress_callback:
                progress_callback(0)
            raise e

    def _convert_image(self, input_path, output_path, output_format, options):
        """Конвертировать изображение с возможностью изменения размера"""
        try:
            pil_format = self.pil_format_mapping.get(output_format, output_format.upper())

            with Image.open(input_path) as img:
                # Изменение размера если указано
                if options.get('resize_enabled', False):
                    width = options.get('width')
                    height = options.get('height')

                    if width and height:
                        if options.get('keep_aspect', True):
                            img.thumbnail((width, height), Image.Resampling.LANCZOS)
                        else:
                            img = img.resize((width, height), Image.Resampling.LANCZOS)

                if output_format in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'LA', 'P']:
                    if img.mode == 'P' and 'transparency' in img.info:
                        img = img.convert('RGBA')
                    else:
                        img = img.convert('RGB')

                save_kwargs = {}
                if output_format in ['jpg', 'jpeg']:
                    save_kwargs['quality'] = options.get('quality', 95)
                elif output_format == 'png':
                    save_kwargs['optimize'] = True

                img.save(output_path, format=pil_format, **save_kwargs)

            return os.path.exists(output_path)

        except Exception as e:
            raise Exception(f"Ошибка конвертации изображения: {e}")

    def _convert_data(self, input_path, output_path, output_format):
        """Конвертировать данные (CSV, JSON, Excel, TXT)"""
        try:
            input_ext = os.path.splitext(input_path)[1].lower().lstrip('.')

            if input_ext in ['csv']:
                df = pd.read_csv(input_path)
            elif input_ext in ['xlsx', 'xls']:
                df = pd.read_excel(input_path)
            elif input_ext in ['json']:
                df = pd.read_json(input_path)
            elif input_ext in ['txt']:
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                if output_format == 'json':
                    data = {"content": content}
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    return True
                elif output_format == 'csv':
                    lines = content.split('\n')
                    with open(output_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        for line in lines:
                            if line.strip():
                                writer.writerow([line])
                    return True
                elif output_format in ['xlsx', 'xls']:
                    lines = content.split('\n')
                    df = pd.DataFrame(lines, columns=['Content'])
                    df.to_excel(output_path, index=False)
                    return True
                else:
                    return self._copy_file(input_path, output_path)
            else:
                raise ValueError(f"Неподдерживаемый входной формат: {input_ext}")

            if output_format == 'csv':
                df.to_csv(output_path, index=False, encoding='utf-8')
            elif output_format == 'json':
                df.to_json(output_path, orient='records', indent=2, force_ascii=False)
            elif output_format in ['xlsx', 'xls']:
                df.to_excel(output_path, index=False)
            elif output_format == 'txt':
                df.to_csv(output_path, index=False, sep='\t', encoding='utf-8')

            return True

        except Exception as e:
            raise Exception(f"Ошибка конвертации данных: {e}")

    def _convert_document(self, input_path, output_path, output_format):
        """Конвертировать документы (PDF, DOC, DOCX, TXT, RTF)"""
        try:
            input_ext = os.path.splitext(input_path)[1].lower().lstrip('.')

            if input_ext == 'pdf' and output_format == 'txt':
                text = ""
                with fitz.open(input_path) as doc:
                    for page in doc:
                        text += page.get_text()

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                return True

            elif input_ext == 'pdf' and output_format in ['doc', 'docx']:
                try:
                    subprocess.run(['soffice', '--headless', '--convert-to',
                                    'docx' if output_format == 'docx' else 'doc',
                                    input_path, '--outdir', os.path.dirname(output_path)],
                                   check=True)
                    return True
                except:
                    text = ""
                    with fitz.open(input_path) as doc:
                        for page in doc:
                            text += page.get_text()

                    doc = Document()
                    doc.add_paragraph(text)
                    doc.save(output_path)
                    return True

            elif input_ext in ['doc', 'docx'] and output_format == 'pdf':
                try:
                    pythoncom.CoInitialize()
                    word = win32com.client.Dispatch("Word.Application")
                    word.Visible = False

                    doc = word.Documents.Open(input_path)
                    doc.SaveAs(output_path, FileFormat=17)
                    doc.Close()
                    word.Quit()
                    return True
                except Exception as e:
                    raise Exception(f"Ошибка конвертации Word в PDF: {e}")

            elif input_ext in ['doc', 'docx'] and output_format == 'txt':
                try:
                    doc = Document(input_path)
                    text = "\n".join([para.text for para in doc.paragraphs])

                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    return True
                except Exception as e:
                    raise Exception(f"Ошибка чтения Word документа: {e}")

            else:
                return self._copy_file(input_path, output_path)

        except Exception as e:
            raise Exception(f"Ошибка конвертации документа: {e}")

    def _convert_audio(self, input_path, output_path, output_format):
        """Конвертировать аудио файлы"""
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=output_format)
            return True

        except Exception as e:
            raise Exception(f"Ошибка конвертации аудио: {e}")

    def _convert_video(self, input_path, output_path, output_format):
        """Конвертировать видео файлы (требует ffmpeg для реального изменения формата)"""
        try:
            return self._copy_file(input_path, output_path)

        except Exception as e:
            raise Exception(f"Ошибка конвертации видео: {e}")

    def get_video_preview(self, input_path, frame_time=1.0, output_image_path=None):
        """Извлекает кадр из видео для предпросмотра"""
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 25  # fallback
        frame_number = int(fps * frame_time)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise Exception("Не удалось получить кадр из видео")

        if output_image_path:
            cv2.imwrite(output_image_path, frame)
            return output_image_path
        return frame

    def _copy_file(self, input_path, output_path):
        """Простое копирование файла"""
        try:
            shutil.copy2(input_path, output_path)
            return True
        except Exception as e:
            raise Exception(f"Ошибка копирования файла: {e}")

    def get_file_info(self, file_path):
        """Получить информацию о файле"""
        if not os.path.exists(file_path):
            return None

        try:
            info = {
                'name': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'format': os.path.splitext(file_path)[1].upper().lstrip('.'),
                'created': os.path.getctime(file_path)
            }

            if info['format'].lower() in self.supported_formats['images']:
                try:
                    with Image.open(file_path) as img:
                        info['width'] = img.width
                        info['height'] = img.height
                        info['mode'] = img.mode
                except:
                    pass

            elif info['format'].lower() in self.supported_formats['audio']:
                try:
                    if info['format'].lower() == 'wav':
                        with contextlib.closing(wave.open(file_path, 'r')) as f:
                            info['channels'] = f.getnchannels()
                            info['sample_rate'] = f.getframerate()
                            info['duration'] = f.getnframes() / float(f.getframerate())
                    else:
                        audio = AudioSegment.from_file(file_path)
                        info['duration'] = len(audio) / 1000
                        info['channels'] = audio.channels
                        info['sample_rate'] = audio.frame_rate
                except:
                    pass

            elif info['format'].lower() in self.supported_formats['video']:
                info['type'] = 'video'
                info['duration'] = 'Неизвестно (требуется ffmpeg)'

            return info

        except Exception as e:
            raise Exception(f"Ошибка получения информации о файле: {e}")
