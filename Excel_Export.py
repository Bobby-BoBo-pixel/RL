'''
1、为什么要合成字典？ ---因为excel导入，最好的数据类型是pandas的Dataframe，并且字典和dataframe可以直接转换，还能直接把键值对中的键变成header，数据没header是很不好的
2、主要用的类和方法如下：
pd.DataFrame（类） --- pandas包最外层的类，用于创建dataframe(df)实例
pd.ExcelWriter（类） --- pandas包最外层的类，用于创建writer实例
df.to_excel --- df实例的实例方法
writer._save() --- writer实例的实例方法
writer.close() --- writer实例的实例方法
'''


#%%

import pandas as pd
def Excel_Export(dic,file_name):
    '''
    输入想要导出的参数构成的字典，输出包含参数的excel文件
    :param dic: 需要输出的参数所构成的字典
    :param file_name: 输出文件名/目录
    :return: 在目录下生成一个excel文件
    '''
    # DataFrame类可以直接把字典类型的数据转化为dataframe，并且key键值对中的键变成header，value键值对中的值为此列数据
    df = pd.DataFrame(dic)
    # 创建writer实例，并写进名为A的excel文件里面（ExcelWriter类的实例，这个类在pd文件夹里面）
    writer = pd.ExcelWriter(path = file_name)
    # 写入excel，to_excel其实是NDFrame类的方法，df所属类的父类是NDFrame类，所以可以使用父类方法
    df.to_excel(excel_writer=writer, sheet_name='page_1', float_format='%.5f')
    # 保存excel
    writer._save()
    # 关闭excel
    writer.close()