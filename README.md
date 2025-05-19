## Selenium 与 EdgeDriver 安装配置指南

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

   ![EdgeDriver 版本选择示例](你的图片链接或本地图片)

3. **解压并重命名驱动文件**  
   下载的压缩包解压后，会得到一个 `msedgedriver.exe` 文件。  
   将 `msedgedriver.exe` 复制到你的 Python 根目录下，并重命名为 `MicrosoftWebDriver.exe`。

4. **添加环境变量**  
   - 将 Python 根目录（即 `MicrosoftWebDriver.exe` 所在目录）添加到系统环境变量 `Path` 中。
   - 同时将 Edge 浏览器的安装路径（如 `C:\Program Files (x86)\Microsoft\Edge\Application\`）也添加到 `Path`。

   ![环境变量配置示例](你的图片链接或本地图片)

---

### 3. 验证安装

在命令行输入以下命令，检查驱动是否配置成功：

```bash
MicrosoftWebDriver.exe --version
```

如果显示版本号，则说明配置成功。

---

如需进一步帮助，请参考本项目的详细说明或联系开发者。 