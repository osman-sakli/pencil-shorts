"""Send SNS email notification after each pipeline run."""
from __future__ import annotations
import os


def send(subject: str, message: str) -> None:
    topic = os.getenv("SNS_TOPIC_ARN", "")
    if not topic:
        return
    try:
        import boto3
        boto3.client("sns", region_name="us-east-1").publish(
            TopicArn=topic,
            Subject=subject[:100],
            Message=message,
        )
    except Exception as e:
        print(f"[notify] email gönderilemedi: {e}")
