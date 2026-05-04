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


#功能3：水印
def add_watermark(input_path, output_path, text, font_size, transparency, position):
    try:
        with Image.open(input_path).convert("RGBA") as base:
            text_layer = Image.new("RGBA", base.size, (0,0,0,0))
            # 加载字体
            try:
                font_rb = ImageFont.truetype("arial.ttf", font_size)
                font_d = ImageFont.truetype("arial.ttf", int(font_size*3))
            # 默认字体可能不支持中文
            except IOError:
                font_rb = ImageFont.load_default()
                font_d = ImageFont.load_default()

            draw = ImageDraw.Draw(text_layer)

            if position in ["right_bottom", "both"]:
                #测量文字尺寸
                bbox = draw.textbbox((0,0),text,font=font_rb)
                text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                # 留白防止超出
                x = base.width-text_width-15
                y = base.height-text_height-40

                draw.text((x, y), text, font=font_rb, fill=(0,0,0,transparency))


            if position in ["diagonal", "both"]:
                # 同样先测量文字大小
                bbox_d = draw.textbbox((0, 0), text, font=font_d)
                tw, th = bbox_d[2] - bbox_d[0], bbox_d[3] - bbox_d[1]

                # 创建一个小画布，大小刚好够放字
                # 留白防止旋转时边缘切割                                        黑色水印用透明黑
                txt_img = Image.new("RGBA", (tw + 10, th + 10), (0, 0, 0, 0))
                d = ImageDraw.Draw(txt_img)
                d.text((5, 5), text, font=font_d, fill=(0, 0, 0, transparency))

                # 旋转画布向右上方倾斜
                # expand=True 会自动适应文字旋转后大小                      BICUBIC适用于文字旋转
                rotated_txt = txt_img.rotate(45, expand=True, resample=Image.BICUBIC)

                # 计算中心点，把旋转后的水印贴到 text_layer 中心
                # 使用 rotated_txt 自身作为蒙版
                cx = (base.width - rotated_txt.width) // 2
                cy = (base.height - rotated_txt.height) // 2
                text_layer.paste(rotated_txt, (cx, cy), rotated_txt)

            # 透明合成比paste好
            out = Image.alpha_composite(base, text_layer)

            # 转回 RGB 保存（JPEG不支持透明度）
            out.convert("RGB").save(output_path, "JPEG")
            print(f"水印添加成功: {output_path}")

    except Exception as e:
        print(f"添加水印失败: {e}")
