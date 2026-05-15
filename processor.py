import sys
from PIL import Image, ImageDraw, ImageFont
import os

# 功能1：格式转换-尺寸不变压缩图片
#带有防止透明层变黑功能的格式转换
def handle_image_mode(img):
    if img.mode in ("RGBA", "P"):
        # 创建白色背景
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        # 粘贴时使用 img 自身作为蒙版
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
def resize_image(input_path, width_ratio, height_ratio, output_path):
    try:
        with Image.open(input_path) as img:
            width, height = img.size
            new_width = int(width * width_ratio / 100)
            new_height = int(height * height_ratio / 100)
            new_img = img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
            new_img.save(output_path, format=img.format, optimize=True)
            print(f"缩放至：{output_path}")
    except Exception as e:
        print(f"error: {e}")


# 功能3：水印
def add_watermark(input_path, output_path, text, position, transparency):
    try:
        transparency = int(transparency)
        if transparency<0:
            transparency = 0
        if transparency>100:
            transparency = 100
        with Image.open(input_path) as img:
            has_alpha = img.mode in ("RGBA", "P")
            base = img.convert("RGBA")

            text_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))

            # 根据图片宽度动态计算字号
            diag_font_size = max(40, base.width // 10)
            corner_font_size = max(16, diag_font_size // 3)

            # 加载字体
            try:
                font_corner = ImageFont.truetype("arial.ttf", corner_font_size)
                font_diag = ImageFont.truetype("arial.ttf", diag_font_size)
            except IOError:
                font_corner = ImageFont.load_default()
                font_diag = ImageFont.load_default()

            draw = ImageDraw.Draw(text_layer)

            if position in ["仅右下角", "对角线和右下角"]:
                bbox = draw.textbbox((0, 0), text, font=font_corner)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                x = base.width - tw - 15
                y = base.height - th - 40
                draw.text((x, y), text, font=font_corner, fill=(0, 0, 0, transparency))

            if position in ["仅对角线", "对角线和右下角"]:
                bbox_d = draw.textbbox((0, 0), text, font=font_diag)
                tw, th = bbox_d[2] - bbox_d[0], bbox_d[3] - bbox_d[1]
                txt_img = Image.new("RGBA", (tw + 10, th + 10), (0, 0, 0, 0))
                d = ImageDraw.Draw(txt_img)
                d.text((5, 5), text, font=font_diag, fill=(0, 0, 0, transparency))
                rotated_txt = txt_img.rotate(45, expand=True, resample=Image.Resampling.BICUBIC)
                cx = (base.width - rotated_txt.width) // 2
                cy = (base.height - rotated_txt.height) // 2
                text_layer.paste(rotated_txt, (cx, cy), rotated_txt)

            out = Image.alpha_composite(base, text_layer)

            # 保留原格式：透明图存 PNG，否则存 JPEG
            # 但压缩功能固定为 JPEG，统一行为
            if has_alpha:
                out.save(output_path, "PNG")
            else:
                out.convert("RGB").save(output_path, "JPEG")
            print(f"水印添加成功: {output_path}")

    except Exception as e:
        print(f"添加水印失败: {e}")
