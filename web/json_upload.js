import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ComfyUI.JSONUploadIterator",
    async nodeCreated(node) {
        // 确保只在正确的节点上执行
        if (!node || node.comfyClass !== "JSONUploadIterator") {
            return;
        }

        try {
            // 等待节点完全初始化
            const setupUploadButton = () => {
                const uploadWidget = node.widgets?.find(w => w.name === "upload_btn");
                if (!uploadWidget) {
                    // 如果widget还没创建，稍后重试
                    setTimeout(setupUploadButton, 100);
                    return;
                }

                // 创建隐藏 file input
                const fileInput = document.createElement("input");
                fileInput.type = "file";
                fileInput.accept = ".json";
                fileInput.style.display = "none";
                document.body.appendChild(fileInput);

                fileInput.addEventListener("change", async () => {
                    if (!fileInput.files || fileInput.files.length === 0) return;
                    
                    try {
                        const text = await fileInput.files[0].text();
                        const resp = await fetch("/json_upload", {
                            method: "POST",
                            headers: {"Content-Type": "application/json"},
                            body: JSON.stringify({json: text})
                        });
                        const j = await resp.json();
                        console.log("[JSONUploadIterator] 上传响应:", j);
                        if (j.status === "ok") {
                            uploadWidget.value = `已上传 ${j.total} 条`;
                            app.graph.setDirtyCanvas(true);
                            console.log("[JSONUploadIterator] 数据上传成功，等待下次节点执行");
                        } else {
                            alert("JSON 错误: " + j.msg);
                        }
                    } catch (error) {
                        console.error("[JSONUploadIterator] 上传失败:", error);
                        alert("上传失败: " + error.message);
                    }
                    fileInput.value = "";
                });

                // 按钮点击时打开文件选择器
                uploadWidget.callback = () => {
                    fileInput.click();
                };
            };

            // 延迟执行，确保节点完全初始化
            setTimeout(setupUploadButton, 50);
        } catch (error) {
            console.error("[JSONUploadIterator] 节点创建错误:", error);
        }
    }
});
