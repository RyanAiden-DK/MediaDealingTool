import sys

from PIL import Image
import os

# 功能1：格式转换-尺寸不变压缩图片
#带有防止透明层变黑功能的格式转换
def handle_image_mode(img):
    if img.mode in ("RGBA", "P"):
        # 创建白色背景
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        # 粘贴时使用 img 自身作为蒙版（mask）
        background.paste(img, (0, 0), img)
        return background
    elif img.mode != 'RGB':
        return img.convert('RGB')
    return img
# 正式处理
def compress_by_quality(input_path, output_path, aim_quality=80):
    try:
        with Image.open(input_path) as img:
            new_img = handle_image_mode(img)
            #额外花点 CPU 时间去计算更优的霍夫曼编码表，节约空间
            new_img.save(output_path, "JPEG", optimize=True, quality=aim_quality)
            print(f"成功压缩至{output_path}")
    except Exception as e:
        print(f"error: {e}")


# 功能2：几何变换-缩放
# 默认不输入为原图尺寸
def resize_image(input_path, width_ratio, height_ratio, output_path):
    try:
        with Image.open(input_path) as img:
            original_format = img.format
            if (width_ratio is None) and (height_ratio is None):
                return img

            width, height = img.size
            if (width_ratio is not None) and (height_ratio is None):
                height_ratio = width_ratio
            elif (width_ratio is None) and (height_ratio is not None):
                width_ratio = height_ratio
            new_width = int(width * width_ratio/100)
            new_height = int(height * height_ratio/100)
            new_img = img.resize((new_width, new_height), resample=Image.LANCZOS)
            new_img.save(output_path, format=original_format, optimize=True, quality=100)
            print(f"缩放至：{output_path}")
            return None
    except Exception as e:
        print(f"error: {e}")
        return None