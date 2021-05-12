import jieba

# 全模式
seg_list = jieba.cut("他来到上海交通大学", cut_all=True)
print("【全模式】：" + "/ ".join(seg_list))
print(type(seg_list))

# 精确模式
seg_list = jieba.cut("他来到上海交通大学", cut_all=False)
print("【精确模式】：" + "/ ".join(seg_list))

# 返回列表
seg_list = jieba.lcut("他来到上海交通大学", cut_all=True)
print("【返回列表】：{0}".format(seg_list))
print(type(seg_list))

# 搜索引擎模式
seg_list = jieba.cut_for_search("他毕业于上海交通大学机电系，后来在一机部上海电器科学研究所工作")
print("【搜索引擎模式】：" + "/ ".join(seg_list))

# 返回列表
seg_list = jieba.lcut_for_search("他毕业于上海交通大学机电系，后来在一机部上海电器科学研究所工作")
print("【返回列表】：{0}".format(seg_list))

# 未启用 HMM
seg_list = jieba.cut("他来到了网易杭研大厦", HMM=False) #默认精确模式和启用 HMM
print("【未启用 HMM】：" + "/ ".join(seg_list))

# 识别新词
seg_list = jieba.cut("他来到了网易杭研大厦") #默认精确模式和启用 HMM
print("【识别新词】：" + "/ ".join(seg_list))

# 示例文本
sample_text = "周大福是创新办主任也是云计算方面的专家"

# 未加载词典
print("【未加载词典】：" + '/ '.join(jieba.cut(sample_text)))

# 载入词典
jieba.load_userdict("userdict.txt")

# 加载词典后
print("【加载词典后】：" + '/ '.join(jieba.cut(sample_text)))