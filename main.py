import os
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# --- 1. 模型配置 ---
BASE_URL = "https://x666.me/v1"  # 示例: Ollama 默认地址
API_KEY = "sk-cvqWUuYL0c6Nw3gK9UH3TtGzfnUWyntiFtolbzw7sgFSWQQ2"  # 示例: Ollama 的 key (通常就是模型名或任意字符串)
MODEL_NAME = "gemini-2.5-flash-preview-05-20"  # 示例: 你想要使用的模型名称

# --- 2. 初始化 ---
def initialize_conversation():
    """初始化大模型、记忆和对话链"""
    print("正在初始化模型和对话链...")

    # 初始化大语言模型
    # temperature 控制模型输出的创造性, 0 表示更确定性, 1 表示更随机
    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=0.7,
        streaming=True,  # 开启流式输出以获得更好的体验
    )

    # 初始化对话记忆
    # ConversationBufferMemory 会存储整个对话历史
    # return_messages=True 确保记忆以消息对象列表的形式返回, 这是更现代的做法
    memory = ConversationBufferMemory(return_messages=True)

    # 创建对话链
    # ConversationChain 将 LLM 和 Memory 链接在一起
    # verbose=True 会打印出每次发送给 LLM 的完整提示, 非常适合学习和调试
    conversation = ConversationChain(llm=llm, memory=memory, verbose=True)

    print("初始化完成！可以开始对话了。")
    return conversation


# --- 3. 主对话循环 ---
def main():
    """运行主对话循环"""
    # 获取初始化好的对话链实例
    conversation = initialize_conversation()

    print("\n--- 对话开始 ---")
    print("输入 'exit' 或 '退出' 来结束对话。")

    while True:
        try:
            # 获取用户输入
            user_input = input("\n你: ")

            # 检查退出条件
            if user_input.lower() in ["exit", "退出"]:
                print("AI: 感谢使用，再见！")
                break

            # 调用对话链进行预测
            # .invoke 是 LangChain 的标准调用方法
            # 它会自动处理:
            # 1. 从 memory 中加载历史记录
            # 2. 将历史记录和新输入组合成一个 prompt
            # 3. 将 prompt 发送给 LLM
            # 4. 获取 LLM 的回复
            # 5. 将新输入和 LLM 的回复存入 memory
            result = conversation.invoke({"input": user_input})

            # 打印 AI 的回复
            ai_response = result['response']
            print(f"AI: {ai_response}")

        except KeyboardInterrupt:
            # 允许用户通过 Ctrl+C 优雅地退出
            print("\nAI: 对话已中断，再见！")
            break
        except Exception as e:
            print(f"\n发生了一个错误: {e}")
            print("请检查你的 Base URL 和 API Key 是否正确, 以及模型服务是否正在运行。")
            break


# --- 4. 运行程序 ---
if __name__ == "__main__":
    main()
