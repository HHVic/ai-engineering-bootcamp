"""命令行入口"""
import sys
from app.chain.core import MultiTaskAssistant


def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("欢迎使用多任务问答助手")
    print("=" * 60)
    print("可用功能：")
    print("  • 天气查询（例：'帮我查一下今天的天气'）")
    print("  • 新闻获取（例：'最近的新闻有哪些'）")
    print("  • 一般问答（例：'什么是人工智能'）")
    print("-" * 60)
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'history' 查看对话历史")
    print("输入 'clear' 清空对话历史")
    print("=" * 60)


def print_response(result: dict):
    """格式化输出回答"""
    from_cache = " [缓存]" if result.get("from_cache") else ""
    
    print("\n🤖 助手:")
    print(result["answer"])
    
    if result.get("tools_used"):
        print(f"\n🛠️  使用的工具：{', '.join(result['tools_used'])}{from_cache}")
    
    if result.get("error"):
        print(f"\n⚠️  错误：{result['error']}")


def main():
    """主函数"""
    try:
        assistant = MultiTaskAssistant()
    except Exception as e:
        print(f"初始化失败：{e}")
        print("请检查 .env 文件中的 API 密钥配置")
        sys.exit(1)
    
    print_welcome()
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n💬 你：").strip()
            
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ("quit", "exit", "q"):
                print("\n👋 再见！")
                break
            
            if user_input.lower() == "history":
                history = assistant.get_history()
                if not history:
                    print("\n📜 暂无对话历史")
                else:
                    print("\n📜 对话历史:")
                    for msg in history:
                        role = "👤 你" if msg["role"] == "user" else "🤖 助手"
                        print(f"{role}: {msg['content']}")
                continue
            
            if user_input.lower() == "clear":
                assistant.clear_history()
                print("\n✅ 对话历史已清空")
                continue
            
            # 处理用户查询
            print("\n⏳ 正在思考...")
            result = assistant.chat(user_input)
            print_response(result)
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except EOFError:
            print("\n👋 再见！")
            break


if __name__ == "__main__":
    main()
