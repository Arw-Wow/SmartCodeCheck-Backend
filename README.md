# SmartCodeCheck-Backend

### 📂 项目结构

```
llm_code_eval_backend/
├── .env                 # 环境变量文件 (存放 API Key)
├── requirements.txt     # 依赖包
├── app/
│   ├── __init__.py
│   ├── main.py          # 入口
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── analysis.py
│   │       └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py    # 配置加载
│   │   └── models.py    # Pydantic 模型
│   └── services/
│       ├── __init__.py
│       └── llm_analyzer.py # 核心业务逻辑
```

### 🚀 运行后端

1.  **安装依赖**:

    ```bash
    conda create -n SCC-Backend python=3.11
    pip install -r requirements.txt
    ```

2.  **配置 API Key**:
    修改 `.env example` 文件，并将文件名改为 `.env`。如果没有 Key，可以在 `llm_analyzer.py` 中把 API 调用部分注释掉，直接返回 Mock 数据用于测试。

3.  **启动服务**:

    ```bash
    conda activate SCC-Backend
    uvicorn app.main:app --reload --port 8000
    ```

4.  **API 文档**:
    浏览器打开 `http://localhost:8000/docs`，你可以直接在这里测试接口。