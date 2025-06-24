import asyncio
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import time
import uuid
import re
import json
import os
from datetime import datetime, timedelta
import pickle
import threading
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import (
    AgentWorkflow,
    FunctionAgent,
)
from llama_index.core.workflow import (
    HumanResponseEvent,
    InputRequiredEvent,
    Context
)


@dataclass
class EmailConfig:
    """邮件配置类"""
    smtp_server: str
    smtp_port: int
    imap_server: str
    imap_port: int
    username: str
    password: str
    from_email: str
    to_email: str
    use_ssl: bool = True


@dataclass
class PendingRequest:
    """待处理请求类"""
    request_id: str
    user_name: str
    task_name: str
    question: str
    created_at: datetime
    expires_at: datetime
    context_data: Dict[str, Any]
    workflow_state: bytes  # 序列化的工作流状态
    status: str = "pending"  # pending, completed, expired, cancelled


class PersistentStorage:
    """持久化存储管理器"""

    def __init__(self, storage_dir: str = "email_requests"):
        self.storage_dir = storage_dir
        self.requests_file = os.path.join(storage_dir, "pending_requests.json")
        self.contexts_dir = os.path.join(storage_dir, "contexts")

        # 创建存储目录
        os.makedirs(storage_dir, exist_ok=True)
        os.makedirs(self.contexts_dir, exist_ok=True)

    def save_request(self, request: PendingRequest) -> bool:
        """保存待处理请求"""
        try:
            # 加载现有请求
            requests = self.load_all_requests()

            # 添加新请求
            requests[request.request_id] = {
                "request_id": request.request_id,
                "user_name": request.user_name,
                "task_name": request.task_name,
                "question": request.question,
                "created_at": request.created_at.isoformat(),
                "expires_at": request.expires_at.isoformat(),
                "context_data": request.context_data,
                "status": request.status
            }

            # 保存工作流状态到单独文件
            context_file = os.path.join(
                self.contexts_dir, f"{request.request_id}.pkl")
            with open(context_file, 'wb') as f:
                f.write(request.workflow_state)

            # 保存请求列表
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, ensure_ascii=False, indent=2)

            print(f"✅ 请求已保存: {request.request_id}")
            return True

        except Exception as e:
            print(f"❌ 保存请求失败: {e}")
            return False

    def load_request(self, request_id: str) -> Optional[PendingRequest]:
        """加载指定请求"""
        try:
            requests = self.load_all_requests()
            if request_id not in requests:
                return None

            req_data = requests[request_id]

            # 加载工作流状态
            context_file = os.path.join(self.contexts_dir, f"{request_id}.pkl")
            if not os.path.exists(context_file):
                return None

            with open(context_file, 'rb') as f:
                workflow_state = f.read()

            return PendingRequest(
                request_id=req_data["request_id"],
                user_name=req_data["user_name"],
                task_name=req_data["task_name"],
                question=req_data["question"],
                created_at=datetime.fromisoformat(req_data["created_at"]),
                expires_at=datetime.fromisoformat(req_data["expires_at"]),
                context_data=req_data["context_data"],
                workflow_state=workflow_state,
                status=req_data["status"]
            )

        except Exception as e:
            print(f"❌ 加载请求失败: {e}")
            return None

    def load_all_requests(self) -> Dict[str, Any]:
        """加载所有请求"""
        try:
            if os.path.exists(self.requests_file):
                with open(self.requests_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"❌ 加载请求列表失败: {e}")
            return {}

    def update_request_status(self, request_id: str, status: str) -> bool:
        """更新请求状态"""
        try:
            requests = self.load_all_requests()
            if request_id in requests:
                requests[request_id]["status"] = status
                with open(self.requests_file, 'w', encoding='utf-8') as f:
                    json.dump(requests, f, ensure_ascii=False, indent=2)
                return True
            return False
        except Exception as e:
            print(f"❌ 更新请求状态失败: {e}")
            return False

    def cleanup_expired_requests(self) -> int:
        """清理过期请求"""
        try:
            requests = self.load_all_requests()
            current_time = datetime.now()
            expired_count = 0

            for request_id, req_data in list(requests.items()):
                expires_at = datetime.fromisoformat(req_data["expires_at"])
                if current_time > expires_at and req_data["status"] == "pending":
                    # 标记为过期
                    requests[request_id]["status"] = "expired"
                    expired_count += 1

                    # 删除上下文文件
                    context_file = os.path.join(
                        self.contexts_dir, f"{request_id}.pkl")
                    if os.path.exists(context_file):
                        os.remove(context_file)

            # 保存更新后的请求列表
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, ensure_ascii=False, indent=2)

            if expired_count > 0:
                print(f"🗑️ 清理了 {expired_count} 个过期请求")

            return expired_count

        except Exception as e:
            print(f"❌ 清理过期请求失败: {e}")
            return 0


class EmailHandler:
    """邮件处理器类"""

    def __init__(self, config: EmailConfig, storage: PersistentStorage):
        self.config = config
        self.storage = storage

    async def send_email(self, subject: str, body: str, request_id: str) -> bool:
        """发送邮件"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.from_email
            msg['To'] = self.config.to_email
            msg['Subject'] = f"{subject} [RequestID: {request_id}]"

            # 添加请求ID到邮件正文
            full_body = f"{body}\n\n" \
                f"📧 请在回复中包含 RequestID: {request_id}\n" \
                f"✅ 回复 'yes' 确认执行\n" \
                f"❌ 回复 'no' 取消执行\n\n" \
                f"⏰ 此请求将在24小时后自动过期"

            msg.attach(MIMEText(full_body, 'plain', 'utf-8'))

            # 发送邮件
            if self.config.use_ssl:
                server = smtplib.SMTP_SSL(
                    self.config.smtp_server, self.config.smtp_port)
            else:
                server = smtplib.SMTP(
                    self.config.smtp_server, self.config.smtp_port)
                server.starttls()

            server.login(self.config.username, self.config.password)
            server.send_message(msg)
            server.quit()

            print(f"✅ 邮件已发送到 {self.config.to_email}")
            return True

        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False

    async def check_email_replies(self) -> Optional[tuple]:
        """检查邮件回复"""
        try:
            if self.config.use_ssl:
                mail = imaplib.IMAP4_SSL(
                    self.config.imap_server, self.config.imap_port)
            else:
                mail = imaplib.IMAP4(
                    self.config.imap_server, self.config.imap_port)

            mail.login(self.config.username, self.config.password)
            mail.select('inbox')

            # 搜索未读邮件
            status, messages = mail.search(None, 'UNSEEN')

            if status == 'OK' and messages[0]:
                message_ids = messages[0].split()

                for msg_id in message_ids:
                    # 获取邮件
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)

                        # 解析邮件内容
                        subject = decode_header(email_message['Subject'])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode()

                        # 获取邮件正文
                        body = self._get_email_body(email_message)

                        # 提取RequestID
                        request_id_match = re.search(
                            r'RequestID:\s*(\w+)', body)
                        if request_id_match:
                            request_id = request_id_match.group(1)

                            # 提取回复内容
                            response = self._extract_response(body)
                            if response:
                                # 标记邮件为已读
                                mail.store(msg_id, '+FLAGS', '\\Seen')
                                mail.close()
                                mail.logout()
                                return request_id, response

            mail.close()
            mail.logout()
            return None

        except Exception as e:
            print(f"❌ 检查邮件失败: {e}")
            return None

    def _get_email_body(self, email_message) -> str:
        """提取邮件正文"""
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            body = email_message.get_payload(decode=True).decode('utf-8')
        return body

    def _extract_response(self, body: str) -> Optional[str]:
        """从邮件正文中提取用户回复"""
        body_lower = body.lower()
        if 'yes' in body_lower:
            return 'yes'
        elif 'no' in body_lower:
            return 'no'
        return None


# 常见邮件服务提供商配置模板
EMAIL_PROVIDERS = {
    "gmail": {
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_server": "imap.gmail.com",
        "imap_port": 993,
        "use_ssl": True,
        "note": "需要开启两步验证并使用应用专用密码"
    },
    "outlook": {
        "smtp_server": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "imap_server": "outlook.office365.com",
        "imap_port": 993,
        "use_ssl": True,
        "note": "支持Microsoft账户"
    },
    "qq": {
        "smtp_server": "smtp.qq.com",
        "smtp_port": 587,
        "imap_server": "imap.qq.com",
        "imap_port": 993,
        "use_ssl": True,
        "note": "需要在QQ邮箱设置中开启IMAP/SMTP服务"
    },
    "163": {
        "smtp_server": "smtp.163.com",
        "smtp_port": 587,
        "imap_server": "imap.163.com",
        "imap_port": 993,
        "use_ssl": True,
        "note": "需要在网易邮箱设置中开启IMAP/SMTP服务"
    }
}


def create_email_config(
    provider: str = "gmail",
    username: str = None,
    password: str = None,
    to_email: str = None
) -> EmailConfig:
    """创建邮件配置"""
    if provider not in EMAIL_PROVIDERS:
        raise ValueError(f"不支持的邮件提供商: {provider}")

    provider_config = EMAIL_PROVIDERS[provider]

    # 从环境变量获取配置（如果未直接提供）
    import os
    username = username or os.getenv("EMAIL_USERNAME")
    password = password or os.getenv("EMAIL_PASSWORD")
    to_email = to_email or os.getenv("EMAIL_TO")

    if not all([username, password, to_email]):
        missing = []
        if not username:
            missing.append("username")
        if not password:
            missing.append("password")
        if not to_email:
            missing.append("to_email")
        raise ValueError(f"缺少必要的邮件配置: {', '.join(missing)}")

    return EmailConfig(
        smtp_server=provider_config["smtp_server"],
        smtp_port=provider_config["smtp_port"],
        imap_server=provider_config["imap_server"],
        imap_port=provider_config["imap_port"],
        username=username,
        password=password,
        from_email=username,
        to_email=to_email,
        use_ssl=provider_config["use_ssl"]
    )


# 全局实例
email_handler = None
storage = None


async def dangerous_task(context: Context, name: str):
    """
    危险任务函数 - 通过邮件获取用户确认（支持持久化）
    """
    global email_handler, storage

    if not email_handler or not storage:
        print("❌ 邮件处理器或存储未初始化")
        return "系统未配置，无法执行任务"

    question = f"你确定要执行危险任务吗？用户：{name}"
    request_id = str(uuid.uuid4())[:8]

    # 创建待处理请求
    pending_request = PendingRequest(
        request_id=request_id,
        user_name=name,
        task_name="dangerous_task",
        question=question,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=24),  # 24小时后过期
        context_data={"name": name},
        workflow_state=pickle.dumps(context),  # 序列化上下文
    )

    # 保存请求到持久化存储
    if not storage.save_request(pending_request):
        return "保存请求失败，无法执行任务"

    # 发送询问邮件
    email_sent = await email_handler.send_email(
        subject="危险任务执行确认",
        body=question,
        request_id=request_id
    )

    if not email_sent:
        return "邮件发送失败，无法执行任务"

    print(f"📤 已发送确认邮件 (RequestID: {request_id})")
    print(f"⏳ 请求已保存，等待用户邮件回复...")

    # 返回pending状态，不阻塞等待
    return f"📧 已发送确认邮件到用户，RequestID: {request_id}。请等待用户回复。"


def resume_task_execution(request_id: str, user_response: str) -> str:
    """恢复任务执行"""
    global storage

    try:
        # 加载保存的请求
        pending_request = storage.load_request(request_id)
        if not pending_request:
            return f"❌ 找不到RequestID: {request_id}"

        if pending_request.status != "pending":
            return f"❌ 请求状态不正确: {pending_request.status}"

        # 检查是否过期
        if datetime.now() > pending_request.expires_at:
            storage.update_request_status(request_id, "expired")
            return f"❌ 请求已过期: {request_id}"

        # 恢复上下文（这里简化处理，实际场景可能需要更复杂的恢复逻辑）
        # context = pickle.loads(pending_request.workflow_state)

        # 处理用户回复
        if user_response.lower() == "yes":
            result = "✅ 任务执行成功"
            storage.update_request_status(request_id, "completed")
        else:
            result = "❌ 用户取消执行任务"
            storage.update_request_status(request_id, "cancelled")

        print(f"🎯 任务执行完成: {request_id} -> {result}")
        return result

    except Exception as e:
        print(f"❌ 恢复任务执行失败: {e}")
        return f"❌ 任务执行失败: {str(e)}"


async def email_monitor_service():
    """邮件监控服务 - 独立运行"""
    global email_handler, storage

    print("🔄 邮件监控服务启动...")

    while True:
        try:
            # 清理过期请求
            storage.cleanup_expired_requests()

            # 检查邮件回复
            reply = await email_handler.check_email_replies()
            if reply:
                request_id, response = reply
                print(f"📧 收到邮件回复: RequestID={request_id}, Response={response}")

                # 恢复并执行任务
                result = resume_task_execution(request_id, response)

                # 发送结果通知邮件
                await email_handler.send_email(
                    subject="任务执行结果",
                    body=f"您的任务 (RequestID: {request_id}) 执行结果：\n{result}",
                    request_id=f"{request_id}_result"
                )

            # 等待30秒后再次检查
            await asyncio.sleep(30)

        except Exception as e:
            print(f"❌ 邮件监控服务错误: {e}")
            await asyncio.sleep(60)


def print_email_setup_guide():
    """打印邮件设置指南"""
    print("📧 持久化邮件Human-in-the-Loop系统")
    print("=" * 60)

    print("\n🔹 支持的邮件服务商:")
    for provider, config in EMAIL_PROVIDERS.items():
        print(f"   • {provider.upper()}: {config['note']}")

    print("\n🔹 配置方式:")
    print("   环境变量方式 (推荐):")
    print("      export EMAIL_USERNAME='your_email@gmail.com'")
    print("      export EMAIL_PASSWORD='your_app_password'")
    print("      export EMAIL_TO='recipient@gmail.com'")

    print("\n🔹 系统特性:")
    print("   • 持久化存储 - 支持程序重启")
    print("   • 事件驱动 - 非阻塞处理")
    print("   • 自动过期 - 24小时后清理")
    print("   • 状态追踪 - 完整生命周期管理")


# 初始化LLM和工作流
llm = OpenAI(model="gpt-4o-mini")
workflow = FunctionAgent(
    tools=[dangerous_task],
    llm=llm,
    system_prompt="你是一个助手，擅长执行危险任务。你会通过邮件向用户确认，支持异步处理用户回复。",
    name="危险任务助手",
    description="支持持久化的危险任务助手，通过邮件获取用户确认",
)


async def run_workflow_once():
    """运行一次工作流"""
    context = Context(workflow)
    handler = workflow.run(user_msg="请执行危险任务", ctx=context)

    try:
        async for event in handler.stream_events():
            if isinstance(event, InputRequiredEvent):
                print(f"📤 {event.prefix}")

        response = await handler
        print(f"🎯 工作流结果: {response}")

    except Exception as e:
        print(f"❌ 工作流执行错误: {e}")


async def main():
    """主函数"""
    global email_handler, storage

    # 打印设置指南
    print_email_setup_guide()

    # 初始化持久化存储
    storage = PersistentStorage()

    # 尝试创建邮件配置
    try:
        email_config = create_email_config("gmail")
        print("\n✅ 成功从环境变量加载邮件配置")
    except ValueError as e:
        print(f"\n⚠️  环境变量配置失败: {e}")
        print("使用示例配置，请手动修改代码中的邮件配置")

        # 示例配置
        email_config = EmailConfig(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            imap_server="imap.gmail.com",
            imap_port=993,
            username="your_email@gmail.com",
            password="your_app_password",
            from_email="your_email@gmail.com",
            to_email="recipient@gmail.com",
            use_ssl=True
        )

    # 初始化邮件处理器
    email_handler = EmailHandler(email_config, storage)

    print("\n🚀 系统启动选项:")
    print("1. 运行一次工作流 (发送邮件请求)")
    print("2. 启动邮件监控服务 (处理用户回复)")
    print("3. 查看待处理请求")

    choice = input("\n请选择 (1/2/3): ").strip()

    if choice == "1":
        print("\n📤 执行工作流...")
        await run_workflow_once()

    elif choice == "2":
        print("\n🔄 启动邮件监控服务...")
        await email_monitor_service()

    elif choice == "3":
        print("\n📋 待处理请求:")
        requests = storage.load_all_requests()
        if not requests:
            print("   暂无待处理请求")
        else:
            for req_id, req_data in requests.items():
                print(
                    f"   • {req_id}: {req_data['status']} - {req_data['question']}")

    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    print("🚀 启动持久化邮件Human-in-the-Loop系统...")
    print("\n💡 主要特性:")
    print("   • 持久化存储上下文")
    print("   • 事件驱动非阻塞处理")
    print("   • 支持程序重启后继续处理")
    print("   • 24小时自动过期机制")
    print("   • 完整的请求生命周期管理")
    print()
    asyncio.run(main())
