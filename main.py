import os
import json
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler

# --- 1. 配置你的模型 ---
# 在这里填入你的 API Base URL 和 Key
# 如果你使用的是本地模型 (例如 Ollama + LiteLLM), base_url 可能是 "http://localhost:8000/v1"
# 如果你使用的是云服务商的代理, 填入他们提供的地址
# 对于本地模型, api_key 通常不是必需的, 可以随便填一个, 比如 "not-needed"

BASE_URL = "https://linjinpeng-veloera.hf.space/v1"  # 示例: Ollama 默认地址
API_KEY = "sk-p5AmVKF2bJhWseY2e5aYWMNOafbTmuykXCWteIKuUfYCcmWp"  # 示例: Ollama 的 key (通常就是模型名或任意字符串)
MODEL_NAME = "moonshotai/Kimi-K2-Instruct-0905"  # 示例: 你想要使用的模型名称


# 简单的逐 token 打印处理器
# 硬编码开关：是否在回复结束后尝试打印思维过程/推理内容
SHOW_THINK = True
# 硬编码开关：是否打印底层原始返回（generations/llm_output 等），便于排查
SHOW_RAW = True
reasoning = {
                "effort": "high",  # 'low', 'medium', or 'high'
                "summary": "auto",  # 'detailed', 'auto', or None
            }

# class StdoutTokenHandler(BaseCallbackHandler):
#     def __init__(self):
#         self._buffer = []  # 收集本轮生成的完整可见文本，用于可选解析 <think>
#
#     def on_llm_new_token(self, token, **kwargs):
#         self._buffer.append(token)
#         print(token, end="", flush=True)
#
#     def on_llm_end(self, response, **kwargs):
#         # 可选：在回复结束时检查是否需要显示“思维过程”
#         if SHOW_THINK:
#             try:
#                 # 1) 检查 generations 中的 additional_kwargs / response_metadata
#                 think_snippets = []
#                 try:
#                     for gen in (response.generations or []):
#                         for cand in gen:
#                             msg = getattr(cand, "message", None)
#                             if msg is None:
#                                 continue
#                             addk = getattr(msg, "additional_kwargs", {}) or {}
#                             # 常见字段尝试
#                             for key in ("reasoning_content", "thoughts", "thinking", "chain_of_thought", "streamText"):
#                                 if key in addk and addk[key]:
#                                     think_snippets.append(str(addk[key]))
#                             # 某些网关可能把 reasoning 塞在 response_metadata
#                             meta = getattr(msg, "response_metadata", {}) or {}
#                             for key in ("reasoning", "reasoning_content"):
#                                 if key in meta and meta[key]:
#                                     think_snippets.append(str(meta[key]))
#                 except Exception:
#                     pass
#
#                 # 2) 若 content 中包含 <think>...</think>，也尝试解析（仅用于调试观察）
#                 try:
#                     full_text = "".join(self._buffer)
#                     if "<think>" in full_text and "</think>" in full_text:
#                         start = full_text.find("<think>") + len("<think>")
#                         end = full_text.find("</think>", start)
#                         if end > start:
#                             think_snippets.append(full_text[start:end].strip())
#                 except Exception:
#                     pass
#
#                 if think_snippets:
#                     print("\n[THINK]\n" + "\n---\n".join(think_snippets) + "\n[/THINK]")
#             finally:
#                 pass
#
#         # 原始返回结构打印（便于排查代理实际回包结构）
#         if SHOW_RAW:
#             try:
#                 def serialize_response(resp):
#                     data = {}
#                     data["llm_output"] = getattr(resp, "llm_output", None)
#                     gens_out = []
#                     for gen in (getattr(resp, "generations", None) or []):
#                         cand_list = []
#                         for cand in gen:
#                             item = {}
#                             item["text"] = getattr(cand, "text", None)
#                             msg = getattr(cand, "message", None)
#                             if msg is not None:
#                                 item["message"] = {
#                                     "content": getattr(msg, "content", None),
#                                     "additional_kwargs": getattr(msg, "additional_kwargs", None),
#                                     "response_metadata": getattr(msg, "response_metadata", None),
#                                     "type": getattr(msg, "type", None),
#                                 }
#                             item["generation_info"] = getattr(cand, "generation_info", None)
#                             cand_list.append(item)
#                         gens_out.append(cand_list)
#                     data["generations"] = gens_out
#                     # 尝试附带其它可用元数据
#                     for key in ("run", "error", "id"):
#                         if hasattr(resp, key):
#                             data[key] = getattr(resp, key)
#                     return data
#
#                 raw = serialize_response(response)
#                 print("\n[RAW]\n" + json.dumps(raw, ensure_ascii=False, indent=2, default=str) + "\n[/RAW]")
#             except Exception as e:
#                 print(f"\n[RAW_PARSE_ERROR] {e}")
#
#         self._buffer.clear()

# 强烈建议使用环境变量来管理你的 Key, 避免硬编码
# from dotenv import load_dotenv
# load_dotenv()
# API_KEY = os.getenv("MY_API_KEY")


# --- 2. 初始化 ---
def initialize_conversation():
    """初始化大模型、记忆和对话链"""
    print("正在初始化模型和对话链...")

    # 初始化大语言模型
    # temperature 控制模型输出的创造性, 0 表示更确定性, 1 表示更随机
    llm = ChatOpenAI(
        model=MODEL_NAME,
        openai_api_base=BASE_URL,
        openai_api_key=API_KEY,
        temperature=0.7,
        streaming=True,  # 开启流式输出以获得更好的体验
        # callbacks=[StdoutTokenHandler()],  # 将逐 token 输出到控制台
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


# --- 2.1 双模型初始化与头脑风暴 ---
def initialize_dual_llms():
    """初始化两个 LLM，用于双人头脑风暴"""
    llm_a = ChatOpenAI(
        model=MODEL_NAME,
        openai_api_base=BASE_URL,
        openai_api_key=API_KEY,
        temperature=0.7,
        streaming=True,
        # callbacks=[StdoutTokenHandler()],
        # reasoning=reasoning
    )
    llm_b = ChatOpenAI(
        model=MODEL_NAME,
        openai_api_base=BASE_URL,
        openai_api_key=API_KEY,
        temperature=0.7,
        streaming=True,
        # callbacks=[StdoutTokenHandler()],
        # reasoning=reasoning
    )
    return llm_a, llm_b


def run_brainstorm(background: str, rounds: int = 6) -> str:
    """基于两个 LLM 的头脑风暴：轮流发言，最后产出总结。

    Args:
        background: 初始背景/需求。
        rounds: 交替发言轮数（总回合数）。

    Returns:
        总结结论文本。
    """
    llm_a, llm_b = initialize_dual_llms()

    transcript = []  # [(speaker, text)]

    def build_context_text():
        parts = [f"背景信息:\n{background}\n", "对话记录:"]
        for speaker, text in transcript:
            parts.append(f"{speaker}: {text}")
        return "\n".join(parts)

    def build_turn_prompt(speaker_name: str) -> str:
        instructions = (
            f"你是{speaker_name}，与另一位伙伴协作讨论上述背景信息。"\
            f"请基于对话记录推进思路，避免重复，总结关键点并提出新的观点或验证思路；"\
            f"若认为可以收敛为结论，请以'建议结论：'开头给出具体、可执行的结论。"
        )
        return f"{build_context_text()}\n\n指令:\n{instructions}\n\n{speaker_name}:"

    for turn in range(rounds):
        is_a_turn = (turn % 2 == 0)
        speaker = "专家A" if is_a_turn else "专家B"
        llm = llm_a if is_a_turn else llm_b

        # 显示头衔前缀并流式输出该轮回复
        print(f"{speaker}: ", end="", flush=True)
        message = llm.invoke(build_turn_prompt(speaker))
        text = getattr(message, "content", str(message))
        print("")  # 换行
        transcript.append((speaker, text))

    # 最后使用 A 做一个收敛总结
    summary_prompt = (
        f"请基于以下讨论给出最终结论与行动建议（简洁分点，突出优先级）：\n\n"
        f"{build_context_text()}\n\n输出：\n- 结论\n- 3-5条行动建议（按优先级）\n"
    )
    print("\n总结: ", end="", flush=True)
    summary_msg = llm_a.invoke(summary_prompt)
    summary_text = getattr(summary_msg, "content", str(summary_msg))
    print("")
    return summary_text

# --- 3. 主对话循环 ---
def main():
    """运行主入口：提供两种模式供选择"""
    print("\n请选择模式：")
    print("1) 单模型对话模式")
    print("2) 双模型头脑风暴模式")

    mode = input("输入 1 或 2 选择模式: ").strip()

    if mode == "2":
        print("\n请输入背景信息/初始需求（多行输入，空行结束）：")
        lines = []
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
        background = "\n".join(lines).strip()
        if not background:
            background = "无具体背景，进行开放式头脑风暴。"

        try:
            rounds_str = input("请输入讨论轮数（默认 6）: ").strip()
            try:
                rounds = int(rounds_str) if rounds_str else 6
                if rounds <= 0:
                    rounds = 6
            except Exception:
                rounds = 6
            summary = run_brainstorm(background=background, rounds=rounds)
            print("总结输出:\n" + summary)
        except KeyboardInterrupt:
            print("\n已中断头脑风暴。")
        except Exception as e:
            print(f"\n发生了一个错误: {e}")
            print("请检查你的 Base URL 和 API Key 是否正确, 以及模型服务是否正在运行。")
        return

    # 默认进入单模型对话模式
    conversation = initialize_conversation()

    print("\n--- 对话开始 ---")
    print("输入 'exit' 或 '退出' 来结束对话。")

    while True:
        try:
            user_input = input("\n你: ")
            if user_input.lower() in ["exit", "退出"]:
                print("AI: 感谢使用，再见！")
                break
            print("AI: ", end="", flush=True)
            _ = conversation.invoke({"input": user_input})
            print("")
        except KeyboardInterrupt:
            print("\nAI: 对话已中断，再见！")
            break
        except Exception as e:
            print(f"\n发生了一个错误: {e}")
            print("请检查你的 Base URL 和 API Key 是否正确, 以及模型服务是否正在运行。")
            break


# --- 4. 运行程序 ---
if __name__ == "__main__":
    main()
