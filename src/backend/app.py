from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import pymysql
import logging
from functools import wraps
import time
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pymysql.install_as_MySQLdb()
app = Flask(__name__)

# 配置请求头
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0"
}

# 禁用SSL警告
requests.packages.urllib3.disable_warnings()

# 数据库配置
DB_CONFIG = {
    "host": "localhost",
    "user": "testuser",
    "password": "testpassword",
    "port": 3306,
    "db": "bbbb",
    "charset": "utf8"
}

# 简单的缓存字典（生产环境建议使用Redis等专业缓存）
cache = {}

# 缓存装饰器
def cache_result(timeout=300):  # 默认缓存5分钟
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 检查缓存
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < timeout:
                    logger.info(f"Cache hit for {cache_key}")
                    return result
                else:
                    # 缓存过期，删除
                    del cache[cache_key]
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存储到缓存
            cache[cache_key] = (result, time.time())
            logger.info(f"Cache set for {cache_key}")
            
            return result
        return wrapper
    return decorator

# 数据库连接池（简化版）
def get_db_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

# 统一的错误处理装饰器
def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return jsonify({"error": "Internal server error"}), 500
    return wrapper

# 爬取学校要闻
@app.route('/xuexiaoyaowen')
@handle_errors
@cache_result(timeout=600)  # 缓存10分钟
def xuexiaoyaowen():
    logger.info("Fetching xuexiaoyaowen data")
    url = "https://www.cqcst.edu.cn/chengkezixun/xuexiaoyaowen/"
    r = requests.get(url, headers=header, verify=False)
    r.raise_for_status()  # 检查请求是否成功
    soup = BeautifulSoup(r.text, 'lxml')

    urls = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a')
    title = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.nr > h3')
    jieshao = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.nr > p')
    shijian = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.nr > span')
    imgurl = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.img > img')
    
    result = []
    for 标题, 介绍, 时间, 网址, 封面 in zip(title, jieshao, shijian, urls, imgurl):
        data = {
            'title': 标题.get_text().strip(),
            'jieshao': 介绍.get_text().strip(),
            'time': 时间.get_text().strip(),
            'url': 网址['href'],
            'imgurl': 封面['src']
        }
        result.append(data)
    return result

# 获取通知公告轮播图标题
@app.route('/gettongzhititle')
@handle_errors
@cache_result(timeout=600)  # 缓存10分钟
def gettongzhititle():
    logger.info("Fetching gettongzhititle data")
    url = "https://www.cqcst.edu.cn/chengkezixun/tongzhigonggao/"
    r = requests.get(url, headers=header, verify=False)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')

    titleurl = soup.select('#banner_list_slide > li > a')
    titletime = soup.select('#banner_list_slide > li > a > div.nr_l > span')
    titlejieshao = soup.select('#banner_list_slide > li > a > div.nr_l > h2')
    titleimage = soup.select('#banner_list_slide > li > a > div.nr_r > img')

    result = []
    for 网址, 时间, 介绍, 封面 in zip(titleurl, titletime, titlejieshao, titleimage):
        data = {
            'url': 网址['href'],
            'time': 时间.get_text().strip(),
            'jieshao': 介绍.get_text().strip(),
            'fengmian': 封面['src']
        }
        result.append(data)
    return result

# 获取通知公告列表
@app.route('/tongzhigonggao')
@handle_errors
@cache_result(timeout=300)  # 缓存5分钟
def tongzhigonggao():
    logger.info("Fetching tongzhigonggao data")
    url = "https://www.cqcst.edu.cn/chengkezixun/tongzhigonggao"
    r = requests.get(url, headers=header, verify=False)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    titles = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list1 > ul > li > a')
    times = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list1 > ul > li > span')

    result = []
    for title, time in zip(titles, times):
        item = {
            'url': title['href'],
            'title': title.get_text().strip(),
            'time': time.get_text()
        }
        result.append(item)
    return result

# 获取URL数据
@app.route('/geturldata', methods=['GET'])
@handle_errors
@cache_result(timeout=300)  # 缓存5分钟
def geturldata():
    aurl = request.args.get('url')
    if not aurl:
        return jsonify({"error": "URL parameter is required"}), 400
    
    logger.info(f"Fetching data for URL: {aurl}")
    r = requests.get(aurl, headers=header, verify=False)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')

    title = soup.select('#layout > div:nth-child(4) > div > div > div.n_body_nr > div > h2')
    title_text = title[0].get_text().strip() if title else ''

    # 提取来源
    laiyuan = soup.select('#layout > div:nth-child(4) > div > div > div.n_body_nr > div > div.info > span:nth-child(1)')
    laiyuan_text = laiyuan[0].get_text().strip() if laiyuan else ''

    # 提取发布时间
    fabutime = soup.select(
        '#layout > div:nth-child(4) > div > div > div.n_body_nr > div > div.info > span:nth-child(2)')
    fabutime_text = fabutime[0].get_text().strip() if fabutime else ''
    
    bodyps = soup.select('#bodyy')
    result = [{
        'title': title_text,
        'laiyuan': laiyuan_text,
        'fabutime': fabutime_text,
        'body': process_html_to_dict(bodyps),
        'order': get_order_list(bodyps)
    }]
    return result

# 获取通知公告更多数据（分页）
@app.route('/gettongzhimoredata', methods=['GET'])
@handle_errors
@cache_result(timeout=300)  # 缓存5分钟
def gettongzhimoredata():
    page = request.args.get('page', 1, type=int)
    logger.info(f"Fetching tongzhigonggao page {page}")
    
    url = "https://www.cqcst.edu.cn/chengkezixun/tongzhigonggao/page/"
    newurl = url + f'{page}'
    r = requests.get(newurl, headers=header, verify=False)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')

    titles = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list1 > ul > li > a')
    times = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list1 > ul > li > span')

    result = []
    for title, time in zip(titles, times):
        item = {
            'url': title['href'],
            'title': title.get_text().strip(),
            'time': time.get_text().strip()
        }
        result.append(item)
    return result

# 获取要闻更多数据（分页）
@app.route('/getyaowenmoredata', methods=['GET'])
@handle_errors
@cache_result(timeout=300)  # 缓存5分钟
def getyaowenmoredata():
    page = request.args.get('page', 1, type=int)
    logger.info(f"Fetching xuexiaoyaowen page {page}")
    
    url = "https://www.cqcst.edu.cn/chengkezixun/xuexiaoyaowen/page/"
    newurl = url + f'{page}'
    r = requests.get(newurl, headers=header, verify=False)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    
    urls = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a')
    title = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.nr > h3')
    jieshao = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.nr > p')
    shijian = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.nr > span')
    imgurl = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.img > img')
    
    result = []
    for 标题, 介绍, 时间, 网址, 封面 in zip(title, jieshao, shijian, urls, imgurl):
        data = {
            'title': 标题.get_text().strip(),
            'jieshao': 介绍.get_text().strip(),
            'time': 时间.get_text().strip(),
            'url': 网址['href'],
            'imgurl': 封面['src']
        }
        result.append(data)
    return result

# 获取校园动态
@app.route('/xiaoyuandongtai')
@handle_errors
@cache_result(timeout=300)  # 缓存5分钟
def xiaoyuandongtai():
    logger.info("Fetching xiaoyuandongtai data")
    url = "https://www.cqcst.edu.cn/chengkezixun/xiaoyuandongtai/"
    r = requests.get(url, headers=header, verify=False)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')

    urls = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a')
    title = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.nr > h3')
    jieshao = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.nr > p')
    shijian = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.nr > span')
    imgurl = soup.select('#layout > div:nth-child(3) > div > div > div.n_body_list2 > ul > li > a > div.img > img')
    
    result = []
    for 标题, 介绍, 时间, 网址, 封面 in zip(title, jieshao, shijian, urls, imgurl):
        data = {
            'title': 标题.get_text().strip(),
            'jieshao': 介绍.get_text().strip(),
            'time': 时间.get_text().strip(),
            'url': 网址['href'],
            'imgurl': 封面['src']
        }
        result.append(data)
    return result

# 处理HTML转换为字典
def process_html_to_dict(bodyps, counts=None):
    if counts is None:
        counts = {'p_count': 1, 'img_count': 1, 'table_count': 1}

    result = {}  # 最终返回的字典

    if not bodyps or len(bodyps) == 0:
        return result  # 如果bodyps为空，返回空字典

    div = bodyps[0]  # 选择列表中的第一个元素，也就是那个div

    # 遍历div中的所有直接子标签
    for child in div.children:
        # 如果是<img>标签
        if child.name == 'img':
            src = child.get('src')
            # 如果src以/开头，则在其前面加上 https://www.cqcst.edu.cn
            if src and src.startswith('/'):
                src = f'https://www.cqcst.edu.cn{src}'
            result[f'img{counts["img_count"]}'] = src  # 处理后的src属性
            counts['img_count'] += 1  # 图片计数+1
            continue  # 继续下一个循环

        # 如果是<p>标签
        if child.name == 'p':
            # 检查<p>标签中是否有<img>标签
            img = child.find('img')
            if img:
                src = img.get('src')
                # 如果src以/开头，则在其前面加上 https://www.cqcst.edu.cn
                if src and src.startswith('/'):
                    src = f'https://www.cqcst.edu.cn{src}'
                result[f'img{counts["img_count"]}'] = src  # 如果有<img>，获取处理后的src属性
                counts['img_count'] += 1  # 图片计数+1
            else:
                # 只提取<p>中的文本
                text = ''.join(child.stripped_strings)
                result[f'p{counts["p_count"]}'] = text  # 以p1, p2的形式存储
                counts['p_count'] += 1  # 段落计数+1

        # 如果是<table>标签
        elif child.name == 'table':
            table_rows = []  # 用于存储表格的每一行
            for row_index, row in enumerate(child.find_all('tr')):  # 查找所有<tr>标签
                row_data = []  # 存储每一行的列元素
                cols = row.find_all(['td', 'th'])  # 查找所有的<td>和<th>标签

                # 对于第一行，正常处理
                if row_index == 0:
                    for col in cols:
                        cell_text = ''.join(col.stripped_strings)
                        row_data.append(cell_text)
                else:
                    # 对于除第一行外的行，合并前两个单元格
                    if len(cols) > 1:
                        merged_cell_text = ''.join(cols[0].stripped_strings) + ' ' + ''.join(cols[1].stripped_strings)
                        row_data.append(merged_cell_text)  # 合并后的文本加入行数据中
                        # 继续加入剩余的单元格数据（从第三个开始）
                        for col in cols[2:]:
                            cell_text = ''.join(col.stripped_strings)
                            row_data.append(cell_text)
                    elif len(cols) == 1:
                        # 如果行中只有一个单元格，直接添加
                        for col in cols:
                            cell_text = ''.join(col.stripped_strings)
                            row_data.append(cell_text)

                table_rows.append(row_data)  # 将行数据添加到表格列表中
            result[f'table{counts["table_count"]}'] = table_rows  # 以table1, table2的形式存储
            counts['table_count'] += 1  # 表格计数+1

        # 如果是<div>标签，递归调用
        elif child.name == 'div':
            # 递归处理内部的div
            subdiv_result = process_html_to_dict([child], counts)  # 传递共享计数器
            result.update(subdiv_result)  # 合并子div的结果，不用存为subdiv

    return result

# 获取内容顺序列表
def get_order_list(bodyps, counts=None):
    if counts is None:
        counts = {'p_count': 1, 'img_count': 1, 'table_count': 1}

    order = []  # 存储数据的顺序

    if not bodyps or len(bodyps) == 0:
        return order  # 如果bodyps为空，返回空顺序列表

    div = bodyps[0]  # 选择列表中的第一个元素，也就是那个div

    # 遍历div中的所有直接子标签
    for child in div.children:
        # 如果是<img>标签
        if child.name == 'img':
            key = f'img{counts["img_count"]}'
            order.append(key)  # 记录顺序
            counts['img_count'] += 1  # 图片计数+1

        # 如果是<p>标签
        elif child.name == 'p':
            img = child.find('img')
            if img:
                key = f'img{counts["img_count"]}'
                order.append(key)  # 记录顺序
                counts['img_count'] += 1  # 图片计数+1
            else:
                key = f'p{counts["p_count"]}'
                order.append(key)  # 记录顺序
                counts['p_count'] += 1  # 段落计数+1

        # 如果是<table>标签
        elif child.name == 'table':
            key = f'table{counts["table_count"]}'
            order.append(key)  # 记录顺序
            counts['table_count'] += 1  # 表格计数+1

        # 如果是<div>标签，递归调用
        elif child.name == 'div':
            subdiv_order = get_order_list([child], counts)  # 传递计数器字典
            order.extend(subdiv_order)  # 将子div中的顺序添加进来

    return order  # 返回顺序列表

# 数据库搜索接口
@app.route('/ddatabase')
@handle_errors
def ddatabase():
    # 从 URL 参数中获取表名和搜索条目
    table = request.args.get('table')
    entry = request.args.get('entry')

    # 确保表名和输入内容不为空
    if not table or not entry:
        return jsonify({"error": "Table name and entry are required."}), 400

    logger.info(f"Database search: table={table}, entry={entry}")
    
    # 建立数据库连接
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 执行模糊搜索
        sql_query = f"SELECT * FROM `{table}` WHERE `title` LIKE %s ORDER BY `title` LIKE %s DESC"
        like_pattern = f"%{entry}%"

        cursor.execute(sql_query, (like_pattern, like_pattern))
        results = cursor.fetchall()

        return jsonify(results)  # 返回搜索结果
    except pymysql.MySQLError as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# 健康检查接口
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

# ==================== 新增API接口 ====================

# 用户登录接口
@app.route('/user/login', methods=['POST'])
@handle_errors
def user_login():
    """用户登录接口，通过微信openid获取或创建用户"""
    data = request.get_json()
    openid = data.get('openid')
    user_info = data.get('userInfo', {})
    
    if not openid:
        return jsonify({"error": "openid is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 查找用户
        cursor.execute("SELECT * FROM users WHERE openid = %s", (openid,))
        user = cursor.fetchone()
        
        if not user:
            # 创建新用户
            cursor.execute("""
                INSERT INTO users (openid, nickname, avatar_url, gender, city, province, country, language)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                openid,
                user_info.get('nickName', ''),
                user_info.get('avatarUrl', ''),
                user_info.get('gender', 0),
                user_info.get('city', ''),
                user_info.get('province', ''),
                user_info.get('country', ''),
                user_info.get('language', 'zh_CN')
            ))
            conn.commit()
            user_id = cursor.lastrowid
            
            # 重新查询用户信息
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        else:
            # 更新用户信息
            cursor.execute("""
                UPDATE users SET 
                nickname=%s, avatar_url=%s, gender=%s, city=%s, province=%s, country=%s, language=%s,
                last_login_time=CURRENT_TIMESTAMP
                WHERE openid=%s
            """, (
                user_info.get('nickName', user['nickname']),
                user_info.get('avatarUrl', user['avatar_url']),
                user_info.get('gender', user['gender']),
                user_info.get('city', user['city']),
                user_info.get('province', user['province']),
                user_info.get('country', user['country']),
                user_info.get('language', user['language']),
                openid
            ))
            conn.commit()
            
            # 重新查询用户信息
            cursor.execute("SELECT * FROM users WHERE openid = %s", (openid,))
            user = cursor.fetchone()
        
        return jsonify({
            "user": user,
            "message": "登录成功"
        })
    except Exception as e:
        logger.error(f"User login error: {e}")
        return jsonify({"error": "登录失败"}), 500
    finally:
        cursor.close()
        conn.close()

# 获取用户收藏列表
@app.route('/user/favorites', methods=['GET'])
@handle_errors
def get_user_favorites():
    """获取用户收藏列表"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM favorites 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (user_id,))
        favorites = cursor.fetchall()
        
        return jsonify({
            "favorites": favorites,
            "count": len(favorites)
        })
    except Exception as e:
        logger.error(f"Get favorites error: {e}")
        return jsonify({"error": "获取收藏列表失败"}), 500
    finally:
        cursor.close()
        conn.close()

# 添加收藏
@app.route('/user/favorite', methods=['POST'])
@handle_errors
def add_favorite():
    """添加收藏"""
    data = request.get_json()
    user_id = data.get('user_id')
    news_type = data.get('news_type')
    news_id = data.get('news_id')
    title = data.get('title')
    
    if not all([user_id, news_type, news_id, title]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查是否已收藏
        cursor.execute("""
            SELECT id FROM favorites 
            WHERE user_id=%s AND news_type=%s AND news_id=%s
        """, (user_id, news_type, news_id))
        
        if cursor.fetchone():
            return jsonify({"message": "已收藏"}), 200
        
        # 添加收藏
        cursor.execute("""
            INSERT INTO favorites (user_id, news_type, news_id, title)
            VALUES (%s, %s, %s, %s)
        """, (user_id, news_type, news_id, title))
        conn.commit()
        
        return jsonify({"message": "收藏成功"})
    except Exception as e:
        logger.error(f"Add favorite error: {e}")
        return jsonify({"error": "收藏失败"}), 500
    finally:
        cursor.close()
        conn.close()

# 取消收藏
@app.route('/user/favorite', methods=['DELETE'])
@handle_errors
def remove_favorite():
    """取消收藏"""
    user_id = request.args.get('user_id', type=int)
    news_type = request.args.get('news_type')
    news_id = request.args.get('news_id', type=int)
    
    if not all([user_id, news_type, news_id]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM favorites 
            WHERE user_id=%s AND news_type=%s AND news_id=%s
        """, (user_id, news_type, news_id))
        conn.commit()
        
        return jsonify({"message": "取消收藏成功"})
    except Exception as e:
        logger.error(f"Remove favorite error: {e}")
        return jsonify({"error": "取消收藏失败"}), 500
    finally:
        cursor.close()
        conn.close()

# 获取新闻评论
@app.route('/news/comments', methods=['GET'])
@handle_errors
def get_news_comments():
    """获取新闻评论"""
    news_type = request.args.get('news_type')
    news_id = request.args.get('news_id', type=int)
    
    if not all([news_type, news_id]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT c.*, u.nickname, u.avatar_url 
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.news_type=%s AND c.news_id=%s AND c.status=1
            ORDER BY c.created_at ASC
        """, (news_type, news_id))
        comments = cursor.fetchall()
        
        return jsonify({
            "comments": comments,
            "count": len(comments)
        })
    except Exception as e:
        logger.error(f"Get comments error: {e}")
        return jsonify({"error": "获取评论失败"}), 500
    finally:
        cursor.close()
        conn.close()

# 添加评论
@app.route('/news/comment', methods=['POST'])
@handle_errors
def add_comment():
    """添加评论"""
    data = request.get_json()
    user_id = data.get('user_id')
    news_type = data.get('news_type')
    news_id = data.get('news_id')
    content = data.get('content')
    parent_id = data.get('parent_id', 0)
    
    if not all([user_id, news_type, news_id, content]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO comments (user_id, news_type, news_id, content, parent_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, news_type, news_id, content, parent_id))
        conn.commit()
        
        return jsonify({"message": "评论成功"})
    except Exception as e:
        logger.error(f"Add comment error: {e}")
        return jsonify({"error": "评论失败"}), 500
    finally:
        cursor.close()
        conn.close()

# 提交反馈意见
@app.route('/feedback', methods=['POST'])
@handle_errors
def submit_feedback():
    """提交反馈意见"""
    data = request.get_json()
    user_id = data.get('user_id')
    content = data.get('content')
    contact = data.get('contact', '')
    
    if not content:
        return jsonify({"error": "Content is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO feedback (user_id, content, contact)
            VALUES (%s, %s, %s)
        """, (user_id, content, contact))
        conn.commit()
        
        return jsonify({"message": "反馈提交成功"})
    except Exception as e:
        logger.error(f"Submit feedback error: {e}")
        return jsonify({"error": "反馈提交失败"}), 500
    finally:
        cursor.close()
        conn.close()

# 记录新闻浏览
@app.route('/news/view', methods=['POST'])
@handle_errors
def record_news_view():
    """记录新闻浏览"""
    data = request.get_json()
    user_id = data.get('user_id')
    news_type = data.get('news_type')
    news_id = data.get('news_id')
    
    if not all([news_type, news_id]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    # 获取客户端IP和User-Agent
    ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 记录浏览
        cursor.execute("""
            INSERT INTO news_views (user_id, news_type, news_id, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, news_type, news_id, ip_address, user_agent))
        conn.commit()
        
        # 更新新闻浏览次数
        if news_type == 'tongzhigonggao':
            cursor.execute("""
                UPDATE tongzhigonggao SET view_count = view_count + 1 
                WHERE id = %s
            """, (news_id,))
        elif news_type == 'xiaoyuandongtai':
            cursor.execute("""
                UPDATE xiaoyuandongtai SET view_count = view_count + 1 
                WHERE id = %s
            """, (news_id,))
        
        conn.commit()
        
        return jsonify({"message": "浏览记录成功"})
    except Exception as e:
        logger.error(f"Record news view error: {e}")
        return jsonify({"error": "浏览记录失败"}), 500
    finally:
        cursor.close()
        conn.close()

# 获取热门新闻
@app.route('/news/hot', methods=['GET'])
@handle_errors
@cache_result(timeout=300)  # 缓存5分钟
def get_hot_news():
    """获取热门新闻（浏览量最高的新闻）"""
    limit = request.args.get('limit', 10, type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取热门通知公告
        cursor.execute("""
            SELECT *, 'tongzhigonggao' as type FROM tongzhigonggao 
            ORDER BY view_count DESC LIMIT %s
        """, (limit//2,))
        tongzhi_news = cursor.fetchall()
        
        # 获取热门校园动态
        cursor.execute("""
            SELECT *, 'xiaoyuandongtai' as type FROM xiaoyuandongtai 
            ORDER BY view_count DESC LIMIT %s
        """, (limit//2,))
        dongtai_news = cursor.fetchall()
        
        # 合并并按浏览量排序
        all_news = tongzhi_news + dongtai_news
        all_news.sort(key=lambda x: x['view_count'], reverse=True)
        hot_news = all_news[:limit]
        
        return jsonify({
            "hot_news": hot_news,
            "count": len(hot_news)
        })
    except Exception as e:
        logger.error(f"Get hot news error: {e}")
        return jsonify({"error": "获取热门新闻失败"}), 500
    finally:
        cursor.close()
        conn.close()

# 搜索历史记录
@app.route('/user/search/history', methods=['GET'])
@handle_errors
def get_search_history():
    """获取用户搜索历史"""
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT DISTINCT keyword FROM search_history 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 20
        """, (user_id,))
        history = cursor.fetchall()
        
        return jsonify({
            "history": [item['keyword'] for item in history]
        })
    except Exception as e:
        logger.error(f"Get search history error: {e}")
        return jsonify({"error": "获取搜索历史失败"}), 500
    finally:
        cursor.close()
        conn.close()

# 记录搜索历史
@app.route('/user/search/history', methods=['POST'])
@handle_errors
def add_search_history():
    """添加搜索历史"""
    data = request.get_json()
    user_id = data.get('user_id')
    keyword = data.get('keyword')
    
    if not all([user_id, keyword]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO search_history (user_id, keyword)
            VALUES (%s, %s)
        """, (user_id, keyword))
        conn.commit()
        
        return jsonify({"message": "搜索历史记录成功"})
    except Exception as e:
        logger.error(f"Add search history error: {e}")
        return jsonify({"error": "搜索历史记录失败"}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1001)