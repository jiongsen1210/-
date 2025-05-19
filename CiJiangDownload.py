from selenium.webdriver import Edge, EdgeOptions as Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
import os
import glob
import shutil
import traceback
import sys

DEFAULT_ASIN_FILE = r'C:\Users\16044\Desktop\Asin.txt'

def read_asin_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def clear_search_input(web, search_input):
    """主要使用DELETE键清空搜索框"""
    try:
        # 主要方法: 使用键盘组合键删除
        search_input.click()
        time.sleep(0.5)

        # 使用DELETE键删除内容
        search_input.send_keys(Keys.DELETE)
        time.sleep(0.2)

        # 检查输入框是否已清空
        value = web.execute_script("return arguments[0].value;", search_input)
        if value:
            print(f"搜索框未完全清空，当前值: {value}，尝试逐个字符删除")
            # 如果全选删除失败，尝试使用多个DELETE键删除
            for i in range(len(value) + 5):  # 多删几次以确保完全清空
                search_input.send_keys(Keys.DELETE)
                search_input.send_keys(Keys.BACKSPACE)

            # 再次检查
            value = web.execute_script("return arguments[0].value;", search_input)
        else:
            print("搜索框已成功清空")

        return True
    except Exception as e:
        print(f"清空搜索框时出错: {e}")
        traceback.print_exc()
        return False


def wait_for_download_and_rename(asin, timeout=60):
    """
    返回:
    - bool: 是否成功重命名
    """
    # 指定下载文件夹路径
    download_path = r"C:\Users\16044\Downloads"
    print(f"开始监测下载文件夹: {download_path}")

    # 记录下载前的CSV文件列表
    before_download = set(glob.glob(os.path.join(download_path, "*.csv")))
    print(f"下载前的CSV文件数量: {len(before_download)}")
    print(f"现有CSV文件: {[os.path.basename(f) for f in before_download]}")

    # 等待新文件出现
    start_time = time.time()
    new_file = None

    while time.time() - start_time < timeout:
        current_files = set(glob.glob(os.path.join(download_path, "*.csv")))
        new_files = current_files - before_download

        # 也检查正在下载中的临时文件
        temp_files = set(glob.glob(os.path.join(download_path, "*.csv.crdownload"))) | \
                     set(glob.glob(os.path.join(download_path, "*.csv.part"))) | \
                     set(glob.glob(os.path.join(download_path, "*.csv.tmp")))

        if temp_files:
            print(f"检测到下载中的临时文件: {[os.path.basename(f) for f in temp_files]}")
            # 继续等待下载完成
            time.sleep(1)
            continue

        if new_files:
            if len(new_files) > 1:
                # 如果同时有多个新文件，按照修改时间排序，选择最新的文件
                new_file = max(new_files, key=os.path.getmtime)
                print(f"检测到多个新文件，选择最新的: {os.path.basename(new_file)}")
            else:
                new_file = list(new_files)[0]
                print(f"检测到新下载的文件: {os.path.basename(new_file)}")
            break

        time.sleep(1)  # 每秒检查一次

    # 如果找到新文件，将其重命名
    if new_file:
        try:
            # 创建新的文件名
            base_name = os.path.basename(new_file)
            new_name = f"{asin}.csv"
            new_path = os.path.join(download_path, new_name)

            # 如果目标文件已存在，先删除
            if os.path.exists(new_path):
                try:
                    os.remove(new_path)
                    print(f"已删除已存在的同名文件: {new_name}")
                except Exception as e:
                    print(f"删除已存在文件失败: {e}")
                    # 使用时间戳生成唯一文件名
                    new_path = os.path.join(download_path, f"{asin}_{int(time.time())}.csv")

            # 确保文件不在使用中
            time.sleep(2)

            # 重命名文件
            shutil.move(new_file, new_path)
            print(f"成功将文件 {base_name} 重命名为 {new_name}")
            return True
        except Exception as e:
            print(f"重命名文件失败: {e}")
            traceback.print_exc()
            return False
    else:
        print(f"等待 {timeout} 秒后未检测到新下载的CSV文件")
        all_files = glob.glob(os.path.join(download_path, "*.csv"))
        print(f"当前所有CSV文件: {[os.path.basename(f) for f in all_files]}")
        return False


def process_all_pages_and_download(web, wait, asin):
    """
    处理搜索结果：全选、翻页到第五页或末页(以先到者为准)、下载数据

    参数:
    - asin: 当前处理的ASIN，用于文件重命名
    """
    try:
        # 等待搜索结果加载
        time.sleep(3)

        # 1. 点击全选按钮
        try:
            select_all_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.el-button.el-button--primary.el-button--small")
            ))
            select_all_button.click()
            print("已点击全选按钮")
            time.sleep(1)
        except Exception as e:
            print(f"点击全选按钮失败: {e}")

        # 2. 翻页到第五页或最后一页(以先到者为准)
        has_next_page = True
        page_count = 0
        max_pages = 5  # 设置最大页数限制为5页，修改原来的100页

        while has_next_page and page_count < max_pages:
            try:
                # 查找下一页按钮
                next_page_button = web.find_element(By.CSS_SELECTOR, "button.btn-next")

                # 检查下一页按钮是否可点击
                is_disabled = next_page_button.get_attribute("disabled")

                if is_disabled == "true" or is_disabled == True:
                    print("已到达最后一页")
                    has_next_page = False
                else:
                    next_page_button.click()
                    page_count += 1
                    print(f"已翻到第 {page_count + 1} 页")

                    # 检查是否已达到最大页数限制
                    if page_count >= max_pages - 1:  # 因为page_count从0开始，所以比较时减1
                        print(f"已达到设定的最大页数限制({max_pages}页)，停止翻页")
                        has_next_page = False

                    # 等待页面加载
                    time.sleep(2)

                    # 继续点击全选按钮确保所有页的数据都被选中
                    try:
                        select_all_button = wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "button.el-button.el-button--primary.el-button--small")
                        ))
                        select_all_button.click()
                        print(f"已在第 {page_count + 1} 页点击全选按钮")
                        time.sleep(1)
                    except:
                        print(f"在第 {page_count + 1} 页点击全选按钮失败")
            except Exception as e:
                print(f"翻页过程中出错: {e}")
                has_next_page = False

        # 3. 点击下载按钮
        try:
            download_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.el-button.el-button--primary.linearBacBnt.el-tooltip__trigger")
            ))
            download_button.click()
            print("已点击下载按钮")

            # 等待下拉菜单出现
            time.sleep(1)

            # 4. 选择CSV格式
            try:
                # 使用文本内容精确定位CSV选项
                csv_option = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//li[contains(@class, 'el-dropdown-menu__item')]/span[text()='CSV']/parent::li")
                ))
                csv_option.click()
                print("已选择CSV格式下载")

                # 等待确认框出现
                time.sleep(2)

                # 5. 点击确认按钮 - 使用多种方法尝试点击
                success = False

                # 方法1: 精确定位确认按钮
                try:
                    confirm_xpath = "//button[@aria-disabled='false'][@type='button'][@class='el-button el-button--primary linearBacBnt']/span[text()='确定']/parent::button"
                    confirm_button = wait.until(EC.presence_of_element_located(
                        (By.XPATH, confirm_xpath)
                    ))
                    # 使用JavaScript点击
                    web.execute_script("arguments[0].click();", confirm_button)
                    print("已点击导出确认框的确定按钮(方法1)")
                    success = True
                except Exception as e:
                    print(f"方法1点击确认按钮失败: {e}")

                # 等待文件下载并重命名
                if success:
                    print(f"等待文件下载完成并将其重命名为 {asin}.csv")
                    # 等待下载完成并重命名
                    if wait_for_download_and_rename(asin):
                        print(f"文件已成功重命名为 {asin}.csv")
                    else:
                        print("文件重命名失败或下载超时")
                else:
                    print("所有尝试点击确认按钮的方法都失败了")

            except Exception as e:
                print(f"选择CSV格式失败: {e}")
                traceback.print_exc()

            # 等待一段时间确保下载操作完成
            time.sleep(3)

        except Exception as e:
            print(f"点击下载按钮失败: {e}")
            traceback.print_exc()

        return True
    except Exception as e:
        print(f"处理页面和下载数据时出错: {e}")
        traceback.print_exc()
        return False


def process_asin(web, wait, asin):
    try:
        # 定位搜索框
        search_input = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@placeholder='请输入小类排名前100的ASIN,例如Top1的ASIN']")
        ))

        # 如果上面的方法失败，尝试使用CSS选择器组合定位
        if not search_input:
            search_input = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "input.el-input__inner")
            ))

        # 使用DELETE键清空搜索框
        clear_success = clear_search_input(web, search_input)
        if not clear_success:
            print("警告：可能无法完全清空搜索框")

        # 重新点击输入框确保焦点
        search_input.click()
        time.sleep(0.5)

        # 输入新的ASIN
        search_input.send_keys(asin)
        print(f"已在搜索框中输入ASIN: {asin}")

        # 检查输入是否正确
        current_value = web.execute_script("return arguments[0].value;", search_input)
        print(f"搜索框当前值: {current_value}")

        if current_value != asin:
            print(f"警告：输入值与预期不符，尝试重新输入")
            clear_search_input(web, search_input)
            time.sleep(0.5)
            search_input.send_keys(asin)

        # 定位并点击搜索按钮
        search_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.el-button.el-button--primary.linearBacBnt")
        ))
        search_button.click()
        print(f"已点击搜索按钮")

        # 等待弹框出现
        time.sleep(2)

        # 尝试查找弹框中的"创建新的搜索"按钮
        try:
            # 尝试定位"创建新的搜索"按钮
            new_search_button = None

            # 方法：根据文本内容定位
            try:
                new_search_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//span[text()='创建新的搜索']/parent::button")
                ))
            except:
                print("未找到按钮")

            if new_search_button:
                if new_search_button is not True:  # 如果不是JavaScript方法找到的
                    print(f"成功找到'创建新的搜索'按钮")
                    new_search_button.click()
                    print(f"已点击'创建新的搜索'按钮")

                # 等待页面刷新
                time.sleep(2)
            else:
                raise Exception("无法找到'创建新的搜索'按钮")

        except Exception as e:
            print(f"未找到'创建新的搜索'按钮或点击失败: {e}")
            traceback.print_exc()
            # 如果找不到按钮，尝试点击弹框中的关闭按钮，然后继续
            try:
                close_button = web.find_element(By.CSS_SELECTOR, "button.el-dialog__headerbtn")
                close_button.click()
                print("找不到创建新的搜索按钮，已点击关闭弹框")
                time.sleep(1)
            except:
                print("尝试关闭弹框也失败")

        # 处理搜索结果：全选、翻页至末页、下载
        print("开始处理搜索结果页面...")
        process_all_pages_and_download(web, wait, asin)  # 传递当前的ASIN用于文件重命名

        # 等待操作完成
        time.sleep(2)
        print(f"已完成ASIN: {asin}的处理")
    except Exception as e:
        print(f"处理ASIN {asin} 时出错: {e}")
        traceback.print_exc()


def print_usage():
    """打印程序使用说明"""
    print("使用方法:")
    print("python CiJiangDownload.py [ASIN文件路径]")
    print("\n参数说明:")
    print("  ASIN文件路径: 包含ASIN列表的文本文件路径")
    print("                如果不提供，将提示用户输入或使用默认路径")
    print("\n示例:")
    print("  python CiJiangDownload.py C:\\Users\\16044\\Desktop\\MyAsin.txt")


def main():
    # 处理命令行参数
    asin_file = None

    # 如果提供了命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help', '/?']:
            print_usage()
            sys.exit(0)
        asin_file = sys.argv[1]
        print(f"使用命令行参数指定的ASIN文件路径: {asin_file}")
    else:
        # 交互式询问用户是否使用自定义路径
        print(f"默认ASIN文件路径: {DEFAULT_ASIN_FILE}")
        choice = input("是否使用自定义路径? (y/n): ").strip().lower()

        if choice == 'y' or choice == 'yes':
            custom_path = input("请输入ASIN文件完整路径: ").strip()
            if custom_path:
                asin_file = custom_path
                print(f"使用自定义路径: {asin_file}")
            else:
                print("未输入有效路径，使用默认路径")
                asin_file = DEFAULT_ASIN_FILE
        else:
            print("使用默认路径")
            asin_file = DEFAULT_ASIN_FILE

    # 检查文件是否存在
    if not os.path.exists(asin_file):
        print(f"错误：ASIN文件不存在: {asin_file}")
        retry = input("是否重新输入文件路径? (y/n): ").strip().lower()
        if retry == 'y' or retry == 'yes':
            new_path = input("请输入ASIN文件完整路径: ").strip()
            if new_path and os.path.exists(new_path):
                asin_file = new_path
            else:
                print("无效路径或文件不存在，程序退出")
                sys.exit(1)
        else:
            sys.exit(1)

    # 造浏览器配置对象
    Edge_op = Options()
    # 配置浏览器，9222是浏览器的运行端口
    Edge_op.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # 让浏览器带着这个配置运行
    web = Edge(options=Edge_op)

    # 创建等待对象，设置超时时间为15秒，增加稳定性
    wait = WebDriverWait(web, 15)

    try:
        # 从文件读取ASIN列表
        asin_list = read_asin_file(asin_file)
        if not asin_list:
            print(f"警告：ASIN文件为空: {asin_file}")
            continue_anyway = input("文件为空，是否继续? (y/n): ").strip().lower()
            if continue_anyway != 'y' and continue_anyway != 'yes':
                print("程序退出")
                sys.exit(0)
        
        print(f"共读取到 {len(asin_list)} 个ASIN")

        # 逐行处理ASIN
        for i, asin in enumerate(asin_list, 1):
            print(f"正在处理第 {i}/{len(asin_list)} 个ASIN: {asin}")
            process_asin(web, wait, asin)
            # 添加操作间隔，提高稳定性
            time.sleep(3)

        print("全部数据已处理完毕。")
    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        traceback.print_exc()
    finally:
        # 如果需要关闭浏览器，取消下面这行的注释
        # web.quit()
        pass

if __name__ == "__main__":
    main()