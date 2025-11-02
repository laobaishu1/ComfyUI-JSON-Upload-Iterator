import json
from server import PromptServer
from aiohttp import web

# 字段映射配置：如需修改字段，只需修改这里
FIELD_MAPPING = [
    ("shot_id", "SHOT_ID", int, 0),
    ("scene", "SCENE", str, ""),
    ("character_action", "ACTION", str, ""),
    ("mood", "MOOD", str, ""),
    ("narrator_text", "NARRATOR", str, ""),
    ("bgm_cue", "BGM_CUE", str, ""),
]

class JSONUploadIterator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "upload_btn": ("BUTTON", {"default": "Upload"}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("INT", "STRING", "STRING", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("SHOT_ID", "SCENE", "ACTION", "MOOD", "NARRATOR", "BGM_CUE", "ITERATOR")
    FUNCTION = "execute"
    CATEGORY = "utils/json"

    data = []          # 类变量，保存 shots[]
    index = 0          # 当前迭代指针

    def execute(self, upload_btn=None):
        print(f"[JSONUploadIterator] execute被调用，当前数据长度: {len(JSONUploadIterator.data)}, 当前索引: {JSONUploadIterator.index}")
        if not JSONUploadIterator.data:
            # 返回默认值
            defaults = [field[3] for field in FIELD_MAPPING] + [-1]
            return tuple(defaults)
        
        item = JSONUploadIterator.data[JSONUploadIterator.index]
        print(f"[JSONUploadIterator] 处理第 {JSONUploadIterator.index} 条数据: {item.get('shot_id', 'N/A')}")
        JSONUploadIterator.index = (JSONUploadIterator.index + 1) % len(JSONUploadIterator.data)
        
        # 根据配置提取字段
        result = []
        for json_key, _, transform_func, default_value in FIELD_MAPPING:
            value = item.get(json_key, default_value)
            try:
                result.append(transform_func(value))
            except (ValueError, TypeError):
                result.append(default_value)
        
        result.append(JSONUploadIterator.index)
        print(f"[JSONUploadIterator] 返回结果: SHOT_ID={result[0]}, SCENE={result[1][:20] if result[1] else ''}...")
        return tuple(result)

    @staticmethod
    def upload_json(json_data):
        """接收前端上传内容"""
        try:
            obj = json.loads(json_data)
            JSONUploadIterator.data = obj["shots"]
            JSONUploadIterator.index = 0
            print(f"[JSONUploadIterator] 数据上传成功，共 {len(JSONUploadIterator.data)} 条记录")
            return {"status": "ok", "total": len(JSONUploadIterator.data)}
        except Exception as e:
            print(f"[JSONUploadIterator] 数据上传失败: {str(e)}")
            return {"status": "error", "msg": str(e)}

# 注册路由：/json_upload
def register_routes():
    def create_route():
        try:
            @PromptServer.instance.routes.post("/json_upload")
            async def upload_handler(request):
                post = await request.json()
                return web.json_response(JSONUploadIterator.upload_json(post.get("json")))
            return True
        except AttributeError:
            return False
    
    # 尝试立即注册
    if not create_route():
        # PromptServer还未初始化，延迟注册
        import threading
        def delayed_register():
            import time
            max_retries = 5
            for i in range(max_retries):
                time.sleep(0.5)
                if create_route():
                    break
        threading.Thread(target=delayed_register, daemon=True).start()

NODE_CLASS_MAPPINGS = {
    "JSONUploadIterator": JSONUploadIterator,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "JSONUploadIterator": "JSON Upload & Iterator",
}
