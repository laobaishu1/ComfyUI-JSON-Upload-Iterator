# ComfyUI JSON Upload Iterator

一个用于ComfyUI的JSON上传和迭代器节点，支持上传JSON分镜文件并逐条输出字段。

## 功能特性

- ✅ Web界面文件上传（支持.json文件）
- ✅ 自动解析JSON分镜格式
- ✅ 逐条输出每个shot的字段
- ✅ 支持迭代器模式，可配合Queue Trigger实现自动批量处理
- ✅ **完全配置化设计**，所有字段映射、类型、路由等均可通过配置文件修改

## 安装

1. 将整个 `ComfyUI_JSONUploadIterator` 文件夹复制到 `ComfyUI/custom_nodes/` 目录下
2. 重启ComfyUI

## 使用方法

1. 在ComfyUI节点面板中找到 **"JSON Upload & Iterator"** 节点
2. 将节点拖入画布
3. 点击节点上的 **"Upload"** 按钮，选择JSON文件上传
4. 上传成功后，节点会显示已上传的条数
5. 连接节点的输出端口到下游节点使用

## JSON格式要求

```json
{
  "episode": "第1集·雨夜凶铃",
  "total_shots": 8,
  "shots": [
    {
      "shot_id": 1,
      "scene": "废弃医院走廊",
      "framing": "全景",
      "character_action": "女主举着手电筒，光束颤抖照向走廊尽头",
      "mood": "紧张",
      "narrator_text": "凌晨三点，废弃医院的走廊里，只有手电筒的光束在墙壁上摇晃……",
      "bgm_cue": "low"
    }
  ]
}
```

## 输出端口

默认配置下的输出端口（可通过`config.py`修改）：

- **SHOT_ID** (INT): 镜头序号
- **SCENE** (STRING): 场景描述
- **ACTION** (STRING): 角色动作
- **MOOD** (STRING): 情绪标签
- **NARRATOR** (STRING): 旁白文本
- **BGM_CUE** (STRING): BGM音量标记
- **ITERATOR** (INT): 迭代器索引（可用于触发下一轮处理）

## 配置化说明

所有配置集中在 `config.py` 文件中，便于自定义：

### 1. 修改字段映射

编辑 `config.py` 中的 `FIELD_MAPPINGS` 列表，可以：
- 添加/删除输出字段
- 修改JSON字段名到输出端口的映射
- 更改输出类型（INT/STRING/FLOAT/BOOLEAN）
- 设置默认值和转换函数

示例：添加新字段
```python
FIELD_MAPPINGS = [
    # ... 现有字段 ...
    {
        "json_key": "framing",           # JSON中的字段名
        "output_name": "FRAMING",        # 输出端口名
        "output_type": "STRING",          # 输出类型
        "default_value": "",              # 默认值
        "transform": "str",               # 转换函数
    },
]
```

### 2. 修改JSON结构键名

如果JSON使用不同的键名，修改 `JSON_CONFIG`：
```python
JSON_CONFIG = {
    "shots_key": "scenes",  # 如果JSON中用"scenes"而不是"shots"
    "episode_key": "title",  # 如果JSON中用"title"而不是"episode"
}
```

### 3. 修改API路由

修改 `ROUTE_CONFIG` 可以更改API路径：
```python
ROUTE_CONFIG = {
    "upload_path": "/custom_json_upload",  # 自定义路径
    "request_json_key": "data",            # 自定义请求体键名
}
```

### 4. 修改前端配置

编辑 `web/json_upload.js` 中的 `FRONTEND_CONFIG` 可以：
- 更改支持的文件类型
- 修改提示消息模板
- 调整错误提示格式

### 5. 修改节点配置

编辑 `NODE_CONFIG` 可以：
- 更改节点类别
- 修改按钮文本
- 调整节点显示名称

## API接口

### POST /json_upload（默认路径，可在config.py中修改）

上传JSON文件内容。

**请求体：**
```json
{
  "json": "{...JSON字符串...}"
}
```

**响应：**
```json
{
  "status": "ok",
  "total": 8,
  "episode": "第1集·雨夜凶铃"
}
```
或
```json
{
  "status": "error",
  "msg": "错误信息"
}
```

## 技术说明

- **配置化设计**：所有硬编码已提取到配置文件，易于扩展和修改
- **动态端口生成**：输出端口根据配置自动生成，无需手动修改代码
- **类型转换**：支持自动类型转换（int/float/str/bool）
- **节点使用类变量存储JSON数据**，支持多实例共享
- **每次执行`execute`方法会自动迭代到下一个shot**
- **迭代器会自动循环**（到达末尾后回到开头）

## 依赖

无需额外依赖，使用ComfyUI内置库。

## 扩展示例

### 示例1：添加新字段

在 `config.py` 的 `FIELD_MAPPINGS` 中添加：
```python
{
    "json_key": "duration",
    "output_name": "DURATION",
    "output_type": "FLOAT",
    "default_value": 0.0,
    "transform": "float",
}
```

### 示例2：修改为不同的JSON格式

如果JSON格式是：
```json
{
  "episodes": [
    {"id": 1, "text": "..."}
  ]
}
```

修改 `config.py`：
```python
JSON_CONFIG = {
    "shots_key": "episodes",  # 改为episodes
}
FIELD_MAPPINGS = [
    {
        "json_key": "id",
        "output_name": "EPISODE_ID",
        "output_type": "INT",
        "default_value": 0,
        "transform": "int",
    },
    {
        "json_key": "text",
        "output_name": "TEXT",
        "output_type": "STRING",
        "default_value": "",
        "transform": "str",
    },
]
```

