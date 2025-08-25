# controller.py
import os
import pandas as pd
from PIL import Image
import json
import csv
import shutil


class ConverterController:
    def __init__(self):
        # Поддерживаемые форматы
        self.supported_formats = {
            'images': ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff', 'webp'],
            'data': ['csv', 'json', 'xlsx', 'xls', 'txt']
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
                        # Сохраняем пропорции если нужно
                        if options.get('keep_aspect', True):
                            img.thumbnail((width, height), Image.Resampling.LANCZOS)
                        else:
                            img = img.resize((width, height), Image.Resampling.LANCZOS)

                # Конвертируем цветовое пространство если нужно
                if output_format in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'LA', 'P']:
                    if img.mode == 'P' and 'transparency' in img.info:
                        img = img.convert('RGBA')
                    else:
                        img = img.convert('RGB')

                # Параметры сохранения
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

            # Чтение данных
            if input_ext in ['csv']:
                df = pd.read_csv(input_path)
            elif input_ext in ['xlsx', 'xls']:
                df = pd.read_excel(input_path)
            elif input_ext in ['json']:
                df = pd.read_json(input_path)
            elif input_ext in ['txt']:
                # Для текстовых файлов
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
                            if line.strip():  # Пропускаем пустые строки
                                writer.writerow([line])
                    return True
                elif output_format in ['xlsx', 'xls']:
                    lines = content.split('\n')
                    df = pd.DataFrame(lines, columns=['Content'])
                    df.to_excel(output_path, index=False)
                    return True
                else:
                    # TXT to TXT (просто копирование)
                    return self._copy_file(input_path, output_path)
            else:
                raise ValueError(f"Неподдерживаемый входной формат: {input_ext}")

            # Запись данных для DataFrame
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

            # Дополнительная информация для изображений
            if info['format'].lower() in self.supported_formats['images']:
                try:
                    with Image.open(file_path) as img:
                        info['width'] = img.width
                        info['height'] = img.height
                        info['mode'] = img.mode
                except:
                    pass

            return info

        except Exception as e:
            raise Exception(f"Ошибка получения информации о файле: {e}")