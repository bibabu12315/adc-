import pandas as pd
import numpy as np

def load_excel(file_path):
    """
    使用 pandas 读取 Excel，支持 xlsx 和 xls。
    返回 DataFrame，自动处理数据并过滤缺失值。
    """
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        raise Exception(f"读取 Excel 文件失败: {str(e)}")

def convert_to_valid_data(raw_series):
    """
    将一列包含字符串或数字的混合数据序列清洗为标准的 numpy 数组。
    如果发现类似 '0000 0010' 格式的二进制字符串，会自动转为十进制整形。
    """
    data_list = []
    for val in raw_series.dropna():
        if isinstance(val, str):
            val_clean = val.strip().replace(" ", "")
            # 判断是否为纯二进制字符串
            if val_clean and all(c in '01' for c in val_clean):
                data_list.append(int(val_clean, 2))
                continue
            try:
                data_list.append(int(val_clean))
            except ValueError:
                pass
        else:
            data_list.append(int(val))
    return np.array(data_list)
