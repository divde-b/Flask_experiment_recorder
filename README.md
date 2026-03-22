# 项目名称 

基于python，flask，mysql的网络试验记录与文档管理平台。

## 功能特性  

- ✅ 用户注册、登录、登出（密码哈希存储）
- ✅ 实验记录的增删改查，支持 Markdown 格式的实验报告
- ✅ 技术文档管理（独立模块，同样支持 Markdown）
- ✅ 搜索实验记录（模糊匹配标题、备注、报告内容）
- ✅ 删除操作需管理员密码二次验证
- ✅ 响应式界面，适配移动端
- ✅ 完整的日志记录（文件轮转）
- ✅ 基于蓝图的模块化架构
- ⏳ 集成 AI 助手（计划中）
- ⏳ 使用 C++ 优化核心逻辑（计划中） 

## 技术栈  

-后端：python + Flask  
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
├── logs/                   # 日志文件  
├── routes/                 # 蓝图模块  
│   ├── auth.py             # 用户认证  
│   ├── docs.py             # 文档管理  
│   └── experiments.py      # 实验记录  
├── static/                 # 静态文件  
│   ├── images/             # 截图  
│   └── style.css           # 样式  
├── templates/              # HTML 模板  
│   ├── auth/               # 登录注册页面  
│   ├── docs/               # 文档模板  
│   └── *.html              # 实验记录模板  
├── .gitignore  
├── app.py                  # 应用入口  
├── config.py               # 配置文件（需自行创建，参考 config.example.py）  
├── database.py             # 数据库连接  
├── requirements.txt        # 依赖列表  
├── README.md  
└── TODO.md  
## 作者  
- Github：divde-b  
## 许可证  
本项目采用 [MIT 许可证](https://opensource.org/licenses/MIT)。  
Copyright (c) 2026 divde-b  
