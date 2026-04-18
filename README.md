# 项目名称 

一个基于 Flask + MySQL + TypeScript 的个人知识管理系统，支持实验记录和技术文档的 Markdown 存储与展示。

## 功能特性  

- 用户注册/登录（密码哈希、会话管理）
- 实验记录：增删改查、搜索、Markdown 报告、用户数据隔离
- 技术文档：独立的文档管理模块，同样支持 Markdown 渲染
- 现代化前端：TypeScript 实现删除确认、表单验证、Flash 消息自动消失
- 响应式布局，适配手机和桌面

## 技术栈  

-后端：python + Flask  + Werlzeug
-数据库：MySQL  
-前端：HTML/CSS/JavaScript + Markdown 渲染（marked.js）  
-版本控制：Git + Github
-部署：ubuntu 虚拟机 + Nginx

## 安装与运行  
1.克隆仓库：  
```bash  
    git clone https://github.com/divde-b/Flask_experiment_recorder.git  
    cd Flask_experiment_recoreder  
```  
2.创建并激活虚拟环境：  
```bash  
    python -m venv venv  
    source venv/bin/activate  #Linux/macOS  
    venv\Scripts\activate  #Windows
```  
3.安装依赖：  
```bash  
    pip install -r requirements.txt
```  
4.配置数据库：  
- 创建MySQL数据库experiment_db  
- 导入表结构（见database.sql,如未提供可手动创建）
- 修改config.py中数据库连接信息（参考config.example.py）  

5.运行应用：  
```bash
    python app.py
```  
6.访问http://127.0.0.1:5000即可使用。  
## 项目结构  
flask_mysql_demo/  
├── logs/                          # 应用日志文件  
├── routes/                        # Flask 蓝图模块  
│   ├── __init__.py  
│   ├── auth.py                    # 用户注册、登录、登出  
│   ├── docs.py                    # 技术文档管理  
│   └── experiments.py             # 实验记录管理  
├── static/                        # 静态资源  
│   ├── images/                    # 项目截图或报告中的图片  
│   ├── css/                       # 样式文件  
│   │   └── style.css  
│   ├── js/                        # JavaScript / TypeScript  
│   │   ├── ts/                    # TypeScript 源码  
│   │   │   └── main.ts  
│   │   └── compiled/              # 编译后的 JS  
│   │       └── main.js  
│   └── style.css                  # 主样式  
├── templates/                     # Jinja2 模板  
│   ├── auth/                      # 认证相关页面  
│   │   ├── login.html  
│   │   └── register.html  
│   ├── docs/                      # 文档模块模板  
│   │   ├── index.html  
│   │   ├── add.html  
│   │   ├── edit.html  
│   │   └── detail.html  
│   ├── add.html                   # 添加实验记录  
│   ├── edit.html                  # 编辑实验记录  
│   ├── detail.html                # 实验记录详情  
│   └── index.html                 # 实验记录列表  
├── .gitignore  
├── app.py                         # Flask 应用入口  
├── config.py                      # 配置文件  
├── config.example.py              # 配置示例  
├── database.py                    # 数据库连接工具  
├── requirements.txt               # Python 依赖  
├── package.json                   # Node.js 依赖  
├── package-lock.json              # 依赖锁文件  
├── tsconfig.json                  # TypeScript 编译配置  
├── README.md                      # 项目说明  
└── TODO.md                        # 开发待办  
## 作者  
- Github：divde-b  
## 许可证  
本项目采用 [MIT 许可证](https://opensource.org/licenses/MIT)。  
Copyright (c) 2026 divde-b  
