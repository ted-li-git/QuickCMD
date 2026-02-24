# 项目集合 / Project Collection

[中文](#中文) | [English](#english)

---

## 中文

### 📋 项目简介

这是一个包含多个独立项目的代码仓库，涵盖了游戏开发、系统工具、Minecraft 服务器等多个领域。

### 🎮 主要项目

#### 1. 贪吃蛇游戏（多版本实现）

经典贪吃蛇游戏的三种不同实现方式：

- **snake_game.cpp** - 使用 Windows API 实现
  - 纯 Win32 API 开发
  - 双缓冲绘制，流畅无闪烁
  - 支持方向键控制
  - 实时分数显示

- **snake_sfml.cpp** - 使用 SFML 图形库实现
  - 跨平台支持
  - 精美的粒子效果
  - 主菜单和游戏结束界面
  - 日间/夜间主题切换
  - 最高分记录

- **snake_easyx.cpp** - 使用 EasyX 图形库实现
  - 简单易学的图形接口
  - 渐变色蛇身效果
  - 圆角矩形绘制
  - 批量绘图优化

**编译说明：**
```bash
# Windows API 版本
g++ snake_game.cpp -o snake_game.exe -lgdi32 -mwindows

# SFML 版本（需要安装 SFML）
g++ snake_sfml.cpp -o snake_sfml.exe -lsfml-graphics -lsfml-window -lsfml-system

# EasyX 版本（需要安装 EasyX）
# 使用 Visual Studio 或其他支持 EasyX 的 IDE 编译
```

#### 2. QuickCmd 一键命令工具

一个功能强大的跨平台命令执行工具，使用 Python + PyQt6 开发。

**主要特性：**
- 🪟 支持 Windows、Linux、macOS 三大平台
- ⚡ 预置常用系统命令（系统信息、网络管理、文件管理等）
- 🔧 自定义命令功能，支持变量参数
- 🌙 日间/夜间主题切换
- 📋 实时命令输出显示
- 💾 命令配置持久化存储

**运行方式：**
```bash
cd let_you_hand
pip install PyQt6
python main.py
# 或
python QuickCMD.py
```

**功能模块：**
- 系统信息查询（CPU、内存、磁盘等）
- 网络管理（ping、DNS、路由等）
- 进程管理（进程列表、端口占用等）
- 文件管理（目录浏览、清理缓存等）
- 自定义命令（支持变量替换）

#### 3. Minecraft 服务器

位于 `1.2.1/服务器` 目录，包含完整的 Minecraft 1.2.1 服务器文件。

### 📁 项目结构

```
.
├── snake_game.cpp          # 贪吃蛇游戏 - Windows API 版
├── snake_sfml.cpp          # 贪吃蛇游戏 - SFML 版
├── snake_easyx.cpp         # 贪吃蛇游戏 - EasyX 版
├── let_you_hand/           # QuickCmd 一键命令工具
│   ├── main.py            # 主程序入口
│   ├── QuickCMD.py        # 命令工具实现
│   └── custom_commands.json  # 自定义命令配置
├── 1.2.1/                  # Minecraft 服务器
│   └── 服务器/
└── [其他项目目录...]
```

### 🛠️ 技术栈

- **C++**: Windows API, SFML, EasyX
- **Python**: PyQt6, subprocess
- **工具**: Git, Visual Studio, GCC

### 📝 开发环境

- **操作系统**: Windows 10/11, Linux, macOS
- **编译器**: GCC 9.0+, MSVC 2019+
- **Python**: 3.8+
- **依赖库**: 
  - SFML 2.5+
  - EasyX (Windows)
  - PyQt6

### 🚀 快速开始

1. **克隆仓库**
```bash
git clone [repository-url]
cd [repository-name]
```

2. **运行贪吃蛇游戏**
```bash
# 直接运行编译好的可执行文件
./snake_game.exe
# 或
./snake_sfml.exe
```

3. **运行 QuickCmd 工具**
```bash
cd let_you_hand
python main.py
```

### 📄 许可证

本项目仅供学习和研究使用。

### 👤 作者

个人项目集合

---

## English

### 📋 Project Overview

This is a code repository containing multiple independent projects, covering game development, system tools, Minecraft servers, and more.

### 🎮 Main Projects

#### 1. Snake Game (Multiple Implementations)

Three different implementations of the classic Snake game:

- **snake_game.cpp** - Windows API Implementation
  - Pure Win32 API development
  - Double buffering for smooth rendering
  - Arrow key controls
  - Real-time score display

- **snake_sfml.cpp** - SFML Graphics Library Implementation
  - Cross-platform support
  - Beautiful particle effects
  - Main menu and game over screens
  - Day/night theme switching
  - High score tracking

- **snake_easyx.cpp** - EasyX Graphics Library Implementation
  - Simple and easy-to-learn graphics interface
  - Gradient snake body effects
  - Rounded rectangle rendering
  - Batch drawing optimization

**Compilation Instructions:**
```bash
# Windows API version
g++ snake_game.cpp -o snake_game.exe -lgdi32 -mwindows

# SFML version (requires SFML installation)
g++ snake_sfml.cpp -o snake_sfml.exe -lsfml-graphics -lsfml-window -lsfml-system

# EasyX version (requires EasyX installation)
# Compile using Visual Studio or other EasyX-compatible IDE
```

#### 2. QuickCmd One-Click Command Tool

A powerful cross-platform command execution tool developed with Python + PyQt6.

**Key Features:**
- 🪟 Supports Windows, Linux, and macOS
- ⚡ Pre-configured common system commands (system info, network management, file management, etc.)
- 🔧 Custom command functionality with variable parameters
- 🌙 Day/night theme switching
- 📋 Real-time command output display
- 💾 Persistent command configuration storage

**How to Run:**
```bash
cd let_you_hand
pip install PyQt6
python main.py
# or
python QuickCMD.py
```

**Feature Modules:**
- System information queries (CPU, memory, disk, etc.)
- Network management (ping, DNS, routing, etc.)
- Process management (process list, port usage, etc.)
- File management (directory browsing, cache cleaning, etc.)
- Custom commands (with variable substitution support)

#### 3. Minecraft Server

Located in the `1.2.1/服务器` directory, contains complete Minecraft 1.2.1 server files.

### 📁 Project Structure

```
.
├── snake_game.cpp          # Snake Game - Windows API version
├── snake_sfml.cpp          # Snake Game - SFML version
├── snake_easyx.cpp         # Snake Game - EasyX version
├── let_you_hand/           # QuickCmd one-click command tool
│   ├── main.py            # Main program entry
│   ├── QuickCMD.py        # Command tool implementation
│   └── custom_commands.json  # Custom command configuration
├── 1.2.1/                  # Minecraft server
│   └── 服务器/
└── [Other project directories...]
```

### 🛠️ Tech Stack

- **C++**: Windows API, SFML, EasyX
- **Python**: PyQt6, subprocess
- **Tools**: Git, Visual Studio, GCC

### 📝 Development Environment

- **Operating System**: Windows 10/11, Linux, macOS
- **Compiler**: GCC 9.0+, MSVC 2019+
- **Python**: 3.8+
- **Dependencies**: 
  - SFML 2.5+
  - EasyX (Windows)
  - PyQt6

### 🚀 Quick Start

1. **Clone the Repository**
```bash
git clone [repository-url]
cd [repository-name]
```

2. **Run Snake Game**
```bash
# Run the compiled executable directly
./snake_game.exe
# or
./snake_sfml.exe
```

3. **Run QuickCmd Tool**
```bash
cd let_you_hand
python main.py
```

### 📄 License

This project is for learning and research purposes only.

### 👤 Author

Personal Project Collection

---

## 📸 Screenshots / 截图

### Snake Game / 贪吃蛇游戏
- Classic gameplay with modern graphics
- 经典玩法，现代图形

### QuickCmd Tool / 一键命令工具
- Intuitive user interface
- 直观的用户界面
- One-click command execution
- 一键执行命令

---

## 🤝 Contributing / 贡献

欢迎提交 Issue 和 Pull Request！

Welcome to submit Issues and Pull Requests!

---

## 📮 Contact / 联系方式

如有问题或建议，欢迎通过 Issue 联系。

For questions or suggestions, feel free to contact via Issues.
