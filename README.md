巨潮网批量下载年报

原始代码来自于 https://www.bilibili.com/video/BV1vM41147Ca

https://github.com/wzheyo/Juchao-Annual-Report


A股年报：

stockcode.xlsx文件放在py文件夹下，里面是需要爬取的公司代码，其中公司代码需要为字符型，数字型的保存会有问题（000520会变成520）

只修改了自动放在对应的公司名称下，自动创建年报的文件夹

annual reports cninfo.py

py的依赖包需要你手动安装

H股年报：
hkstockcode.xlsx文件放在py文件夹下，里面是需要爬取的HK公司代码，其中公司代码需要为字符型，写3位或者4位交易代码，自动会补全到5位

annual reports HK cninfo.py

这段代码是我依葫芦画瓢改的，因为巨潮网的问题，下载的港股年报不一定准确。
