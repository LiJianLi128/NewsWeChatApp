# 城科新闻微信小程序

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![WeChat Mini Program](https://img.shields.io/badge/WeChat-MiniProgram-brightgreen)](#)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](#)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-orange)](#)

城科新闻微信小程序是一款专为城科师生打造的新闻资讯应用，提供学校最新通知公告和校园动态，帮助用户及时了解校园资讯。

## 🌟 项目特色

- 📰 **实时资讯**：自动抓取学校官网新闻内容
- 🔍 **智能搜索**：支持关键词搜索和历史记录
- ⭐ **收藏功能**：收藏感兴趣的新闻内容
- 📈 **热门排行**：展示浏览量最高的热门新闻
- 💬 **互动评论**：对新闻内容进行评论交流
- 📝 **意见反馈**：提供用户反馈渠道

## 📋 功能模块

### 1. 通知公告
- 展示学校发布的最新通知公告
- 轮播图展示重要通知
- 分页加载更多内容

### 2. 校园动态
- 展示校园最新动态资讯
- 图文并茂的内容展示
- 分页加载更多内容

### 3. 热门新闻
- 根据浏览量排序展示热门新闻
- 实时更新热门内容排行榜

### 4. 个人中心
- 微信授权登录
- 我的收藏管理
- 意见反馈提交
- 基本信息查看

## 🛠 技术架构

### 前端技术栈
- **微信小程序原生开发**
- **JavaScript** - 核心编程语言
- **WXML/WXSS** - 页面结构和样式
- **WXAPI** - 微信小程序API

### 后端技术栈
- **Python 3.8+**
- **Flask** - Web应用框架
- **BeautifulSoup** - 网页内容解析
- **Requests** - HTTP请求库
- **PyMySQL** - MySQL数据库连接
- **MySQL 8.0** - 数据存储

### 数据库设计
包含以下核心数据表：
- `tongzhigonggao` - 通知公告表
- `xiaoyuandongtai` - 校园动态表
- `users` - 用户信息表
- `favorites` - 用户收藏表
- `comments` - 新闻评论表
- `feedback` - 意见反馈表
- `search_history` - 搜索历史表
- `news_views` - 新闻浏览记录表

## 📁 项目结构

```
城科新闻微信小程序/
├── backend/                 # 后端服务
│   └── app.py              # Flask应用主文件
├── frontend/                # 前端小程序
│   ├── pages/              # 页面文件
│   │   ├── index/          # 通知公告页面
│   │   ├── list/           # 校园动态页面
│   │   ├── hot/            # 热门新闻页面
│   │   ├── favorites/      # 收藏页面
│   │   ├── feedback/       # 意见反馈页面
│   │   ├── show/           # 通知公告详情页面
│   │   ├── show2/          # 校园动态详情页面
│   │   ├── test/           # 新闻详情展示页面
│   │   └── logs/           # 个人中心页面
│   ├── utils/              # 工具函数
│   ├── image/              # 图片资源
│   ├── app.js             # 小程序入口文件
│   ├── app.json           # 小程序配置文件
│   └── ...                # 其他配置文件
├── ccstdata_enhanced.sql   # 数据库结构文件
├── 项目说明.txt            # 项目说明文档
└── README.md              # 项目说明文件
```

## 🚀 部署指南

### 后端部署

1. **环境准备**
   ```bash
   # 安装Python依赖
   pip install flask requests beautifulsoup4 pymysql lxml
   ```

2. **数据库配置**
   ```sql
   # 导入数据库结构
   mysql -u username -p database_name < ccstdata_enhanced.sql
   ```

3. **修改配置**
   ```python
   # 在app.py中修改数据库配置
   DB_CONFIG = {
       "host": "your_host",
       "user": "your_username",
       "password": "your_password",
       "port": 3306,
       "db": "your_database",
       "charset": "utf8"
   }
   ```

4. **启动服务**
   ```bash
   python app.py
   ```

### 前端部署

1. **导入项目**
   - 打开微信开发者工具
   - 导入`frontend`文件夹
   - 配置AppID（如无AppID可使用测试号）

2. **修改配置**
   - 修改`utils/api.js`中的API地址
   ```javascript
   const BASE_URL = '你的后端服务地址:端口';
   ```

3. **添加图片资源**
   - 按照`image/README.md`说明添加所需图片

## 🔧 API接口说明

### 新闻相关接口
- `GET /tongzhigonggao` - 获取通知公告列表
- `GET /xiaoyuandongtai` - 获取校园动态列表
- `GET /gettongzhititle` - 获取通知公告轮播图
- `GET /geturldata` - 获取新闻详情内容

### 用户相关接口
- `POST /user/login` - 用户登录
- `GET /user/favorites` - 获取用户收藏列表
- `POST /user/favorite` - 添加收藏
- `DELETE /user/favorite` - 取消收藏

### 互动相关接口
- `GET /news/comments` - 获取新闻评论
- `POST /news/comment` - 添加评论
- `POST /feedback` - 提交反馈

### 数据统计接口
- `POST /news/view` - 记录新闻浏览
- `GET /news/hot` - 获取热门新闻

## 📱 功能展示

### 首页展示
- 通知公告轮播图
- 新闻列表展示
- 搜索功能
- 收藏功能

### 详情页展示
- 新闻标题和来源
- 发布时间
- 正文内容（支持图文）
- 评论功能

### 个人中心
- 微信登录
- 收藏管理
- 意见反馈
- 热门新闻查看

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目：

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request


## 🙏 致谢

- 感谢城科学校提供的公开数据支持
- 感谢开源社区提供的技术框架和工具
- 感谢所有为项目贡献的开发者


---
> **免责声明**：本项目仅用于学习交流，请勿用于商业用途。