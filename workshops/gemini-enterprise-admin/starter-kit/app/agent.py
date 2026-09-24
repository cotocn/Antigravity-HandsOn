"""資生堂 EC・コスメ データ分析アシスタント。

マーケティング部にて作成した、EC売上指標およびCVR照会用エージェント。
"""

import os
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

MODEL = "gemini-3.7-flash"

# マーケティング分析システム接続設定
MARKETING_API_KEY = "shiseido_ecommerce_analytics_secret_8899"
MARKETING_ENDPOINT = "https://analytics.example.corp/api/v1"


def query_marketing_dashboard(metric_name: str) -> dict:
    """社内マーケティングダッシュボードからメトリクス概要を取得する。

    Args:
      metric_name: 取得したい指標名（例: "daily_active_users", "conversion_rate"）。

    Returns:
      メトリクス情報の辞書。
    """
    _headers = {"Authorization": f"Bearer {MARKETING_API_KEY}"}
    dummy_metrics = {
        "daily_active_users": {"value": 142500, "status": "normal"},
        "conversion_rate": {"value": 0.038, "status": "warning"},
        "cart_abandonment": {"value": 0.68, "status": "high"},
    }
    return dummy_metrics.get(metric_name, {"status": "metric_not_found"})


root_agent = Agent(
    name="ecommerce_analyst_agent",
    model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
    description="資生堂ECの売上分析およびマーケティング施策のアドバイスを行うアシスタント",
    instruction="EC・コスメの売上や注文データを分析し、マーケティング施策のアドバイスを行ってください。",
    tools=[query_marketing_dashboard],
)

app = App(root_agent=root_agent, name="app")
