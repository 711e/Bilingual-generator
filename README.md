# Blender双语文件生成插件
在使用前你可能需要了解下面几项信息，以便更好的使用：
1. blender的翻译采用i18n标准，每一条信息由msgid（英文）和msgstr（翻译）组成，保存在文本文件.po中，再把.po编译成二进制的.mo文件，.mo文件就是blender会加载的翻译文件
2. blender自带的各种语言的.mo文件保存在blender软件的`locale`目录下，该目录下还有一个叫languages的文本文件，里面记录了这些.mo的名称和编号，blender启动时（且仅在启动时）会根据languages的内容加载.mo文件和生成语言选择UI
3. 除了blender安装目录下的`locale`，blender还会加载系统保存软件偏好设置路径下`locale`中的.mo和languages（如果存在的话会加载，没有使用过其他翻译插件的情况下有可能不存在），mac：`/Users/{用户名}/Library/Application Support/Blender`，win:`C:\Users\Administrator\AppData\Roaming\Blender Foundation\Blender`，系统偏好设置的优先级更高

根据上述3条信息可知，想要blender显示双语，只要把两个不同语言的.mo文件拼到一起，然后放到优先级最高的`locale`目录下，再修改languages文件，把新生成的文件名加进去，重新启动blender就可以了

## 版本支持：
| 系统 | 版本 |
|:------:|:-------:|
| WIN | 4.2 |
| MAC | 4.2 |

## 使用说明：
0. 首先选择一个locale文件夹，这里选定哪一个文件夹，操作就会在哪个文件夹中进行，这是一切的前提，插件会在blender软件下和系统偏好设置下搜索locale文件夹显示在此处，也可以通过右侧的按钮添加或删除项（是从列表中删除项而不是删除目录本身）
1. 点击备份对当前选定的locale文件夹做一个备份，会在该目录下拷贝locale文件夹并命名为locale.bak，当发生不可逆的错误或想消除修改时，点击恢复使用locale.bak覆盖locale
2. 点击生成将合并两个下拉菜单中选择的.mo，下拉菜单language1和2的选项来自当前选定的locale文件夹下存在的.mo文件，合并过程可能会消耗一些时间，届时blender会有些卡顿，文件较大的话可能需要几分钟，生成的文件会保存在本插件目录下，并显示在下面的复选框列表中
3. 复选框列表来自本插件目录下存在的.mo文件，点击更新可重新获取列表信息，点击删除可删除当前选择的.mo，点击应用会将选中的.mo文件拷贝到前选定的locale文件夹下，并修改该文件夹下的languages文件，显示应用成功后重启blender，在偏好设置->界面->语言中切换

## .mo文件合并规则：
1. language1位于language2前，当条目中不存在`\n`时以`·`连接，当存在`\n`时以`\n`连接，如果你不喜欢这样的连接方式可以在`BAOperator.py:BackgroundWorker->_combiningStr()`中修改
2. 当language1的条目在language2中不存在时，仅显示language1
3. 当条目中存在占位符时（包括f-string风格），仅显示language1，占位符通过下面的正则表达式进行过滤，C风格：`'%[+-]?[0-9]*\.?[0-9]*(h|l|ll|j|z|t|L)?[diouxXeEfgGaAcspnr]'`，python风格：`'\{[^{}]*\}'`，当发生错误时，你可以考虑在代码中进行修改以匹配更多的类型

## 注意事项：
1. 在应用时请注意当前选择的locale是否最高优先级
2. 在生成.mo文件时，最好不要操作blender，直到显示'SUCCESS'
3. 只有在当前选择的locale目录下存在locale.bak时才能应用