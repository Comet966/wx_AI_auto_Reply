# 微信AI自动回复助手

基于OCR屏幕识别 + DeepSeek API的微信自动回复程序。

## 功能特点

- 自动定位微信窗口
- OCR识别对方消息
- DeepSeek API智能回复
- 支持手动确认/自动发送模式
- 防封延迟机制

## 环境要求

- Python 3.10+
- Windows 10/11

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Comet966/wx_AI_auto_Reply.git
cd wx_AI_auto_Reply
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API Key

编辑 `config.yaml`，将 `your-api-key` 替换为你的DeepSeek API Key:

```yaml
api:
  key: "sk-xxx-your-key-here"
```

### 4. 运行

```bash
python wx_auto/main_auto.py test
```

## 配置说明

`config.yaml` 主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `api.key` | DeepSeek API Key | - |
| `api.model` | 使用的模型 | deepseek-chat |
| `mode.auto_send` | 自动发送模式 | false |
| `safety.max_daily` | 每日最大回复数 | 200 |
| `interval.check` | 消息检测间隔(秒) | 3 |

手动确认模式：`mode.auto_send: false`
自动发送模式：`mode.auto_send: true`

## 使用Claude Code运行

```bash
claude --print "run python wx_auto/main_auto.py test" /path/to/wx_auto
```

或直接：

```bash
cd /path/to/wx_auto
claude -x "Bash(D:/python/python3.13.4/python.exe wx_auto/main_auto.py test)"
```

## 已知问题

以下是当前版本存在的已知问题，正在优化中：

### 1. OCR识别区域不稳定

- 微信窗口大小变化时，识别区域可能不准确
- 需要手动调整 `main_auto.py` 中的区域参数

**当前识别区域设定：**
```python
left = win["left"] + win["width"] // 4
top = win["top"] + int(win["height"] * 0.15)  # 从15%开始
width = win["width"] * 3 // 4
height = int(win["height"] * 0.40)  # 40%高度
```

如识别效果不好，可尝试调整 `top` 和 `height` 的百分比。

### 2. OCR识别效果问题

- 会识别到历史消息（不是当前对话的最新消息）
- 聊天窗口上方灰色区域（对方消息）和下方绿色区域（自己消息）可能有混淆
- 时间戳、UI元素（如"发送"、"图片"等）可能被误识别

**当前过滤规则：**
```python
# 排除时间戳格式 HH:MM
time_pat = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")
# 排除UI关键字
ui_kw = ["发送", "图片", "表情", "文件", "视频", "语音", "名片", "位置"]
```

### 3. 日志显示问题

- 运行日志只在终端显示
- 没有独立的日志文件
- 建议使用 `--debug` 参数查看详细日志

### 优化方向

- [ ] 实现更智能的新消息检测（通过图像对比）
- [ ] 区分自己和对方的聊天区域
- [ ] 添加日志文件输出
- [ ] 添加Tray托盘图标

## 免责声明

**本项目仅供学习交流使用，请勿用于：**

- 商业营销推广
- 批量自动回复
- 打扰他人正常聊天

**使用本项目造成的一切后果由使用者自行承担，**
**包括但不限于微信账号被封禁等风险。**

请合理合规使用，做文明的互联网公民。

## 技术栈

- Python 3.10+
- cnocr - 中文OCR识别
- DeepSeek API - AI对话
- pyautogui - 键鼠模拟
- mss - 屏幕截图
- win32gui - 窗口定位

## 许可证

MIT License