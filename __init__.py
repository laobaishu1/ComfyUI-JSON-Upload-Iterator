from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 注册Web目录，用于加载前端JavaScript文件
WEB_DIRECTORY = "./web"

# 确保路由注册
try:
    from .nodes import register_routes
    register_routes()
except:
    pass

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

