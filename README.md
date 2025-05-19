### 1. 安装 Selenium 库

在命令行中执行以下命令安装 Selenium：

```bash
pip install selenium
```

---

### 2. 下载并配置 Edge 浏览器驱动

1. **查找你的 Edge 浏览器版本**  
   打开 Edge 浏览器，点击右上角菜单 → 帮助和反馈 → 关于 Microsoft Edge，查看你的浏览器版本号（如：120.0.2210.61）。

2. **下载对应版本的 EdgeDriver**  
   在浏览器中搜索 `edgedriver`，或访问 [EdgeDriver 官方下载页面](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)，选择与你的 Edge 浏览器版本一致的驱动进行下载。

3. **解压并重命名驱动文件**  
   下载的压缩包解压后，会得到一个 `msedgedriver.exe` 文件。  
   将 `msedgedriver.exe` 复制到你的 Python 根目录下，并重命名为 `MicrosoftWebDriver.exe`。

4. **添加环境变量**  
   - 将 Python 根目录（即 `MicrosoftWebDriver.exe` 所在目录）添加到系统环境变量 `Path` 中。
   - 同时将 Edge 浏览器的安装路径（如 `C:\Program Files (x86)\Microsoft\Edge\Application\`）也添加到 `Path`。

---

### 3. 验证安装

在命令行输入以下命令，检查驱动是否配置成功：

```bash
MicrosoftWebDriver.exe --version
```

如果显示版本号，则说明配置成功。

---

### 4. CiJiangDownload.py 使用说明

该程序用于自动处理ASIN数据，支持批量处理和自动下载CSV文件。

#### 功能介绍

- 从文本文件中读取ASIN列表
- 自动搜索每个ASIN并选择所有页面数据
- 下载数据并按ASIN命名CSV文件
- 支持自定义文件路径或使用默认路径

#### 使用方法

1. **运行前准备**
   - 确保已安装所有依赖库：`selenium`
   - 启动Edge浏览器并连接调试端口：
     ```bash
     start msedge.exe --remote-debugging-port=9222
     ```
   - 准备包含ASIN列表的文本文件，每行一个ASIN

2. **命令行启动**

   直接指定ASIN文件路径：
   ```bash
   python CiJiangDownload.py C:\Path\To\Your\Asin.txt
   ```
   
   交互式选择文件路径：
   ```bash
   python CiJiangDownload.py
   ```
   
   查看帮助信息：
   ```bash
   python CiJiangDownload.py -h
   ```

3. **交互式选择**
   
   如果不提供命令行参数，程序会提示：
   - 是否使用自定义路径
   - 文件不存在时，是否重新输入路径
   - 文件为空时，是否继续执行

#### 注意事项

- 程序需要Edge浏览器在调试模式下运行（端口9222）
- 下载的CSV文件会保存到 `C:\Users\用户名\Downloads` 目录
- 每个ASIN处理完成后会有短暂等待，以确保稳定性
- 如遇到错误，可查看控制台输出的详细错误信息

---

如需进一步帮助，请参考本项目的详细说明或联系开发者。 
