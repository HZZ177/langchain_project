"""
双模型头脑风暴Agent实现
"""
from typing import AsyncIterator, Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .base_agent import BaseAgent, AgentMessage, AgentResponse
from backend.core.llm_pool import llm_pool, LLMConnection
from backend.core.logger import logger
import asyncio
import json


class BrainstormAgent(BaseAgent):
    """
    双模型头脑风暴Agent
    使用两个不同的AI模型进行协作讨论，为用户提供多角度的思考和洞察
    """

    def __init__(self, config: Dict[str, Any], agent_id: str = None):
        super().__init__(config)
        self.agent_id = agent_id
        self.config_dict = config
        self.current_connections: Dict[str, Optional[LLMConnection]] = {
            "model_a": None,
            "model_b": None
        }
        logger.info(f"BrainstormAgent初始化 - agent_id: {agent_id}")

    def update_config(self, new_config: Dict[str, Any]):
        """更新Agent配置"""
        logger.info(f"更新BrainstormAgent配置 - agent_id: {self.agent_id}")
        self.config_dict = new_config
        # 清除当前连接，强制重新获取
        self.current_connections = {
            "model_a": None,
            "model_b": None
        }

    def _get_llm_connection(self, model_key: str) -> LLMConnection:
        """从连接池获取指定模型的LLM连接"""
        if not self.agent_id:
            raise ValueError("Agent ID不能为空")

        # 验证模型配置
        model_name_key = f"{model_key}_name"
        api_key_key = f"{model_key}_api_key"
        
        if not self.config_dict.get(model_name_key):
            raise ValueError(f"模型{model_key}名称不能为空")
        
        if not self.config_dict.get(api_key_key):
            raise ValueError(f"模型{model_key}的API密钥不能为空")

        # 构建模型特定配置
        model_config = {
            "model_name": self.config_dict[model_name_key],
            "temperature": self.config_dict.get(f"{model_key}_temperature", 0.7),
            "api_key": self.config_dict[api_key_key],
            "base_url": self.config_dict.get(f"{model_key}_base_url", "https://api.openai.com/v1"),
            "max_tokens": self.config_dict.get("max_tokens")
        }

        # 从连接池获取连接
        connection = llm_pool.get_llm_connection(
            agent_id=f"{self.agent_id}_{model_key}",
            agent_type="brainstorm_agent",
            config=model_config
        )

        if not connection:
            raise RuntimeError(f"无法从连接池获取{model_key}的LLM连接")

        self.current_connections[model_key] = connection
        logger.info(f"获取{model_key}连接成功 - connection_id: {connection.connection_id}")
        return connection

    def _release_llm_connections(self):
        """释放所有LLM连接回连接池"""
        for model_key, connection in self.current_connections.items():
            if connection:
                llm_pool.release_llm_connection(connection.connection_id)
                logger.info(f"释放{model_key}连接 - connection_id: {connection.connection_id}")
                self.current_connections[model_key] = None

    async def process_message(
        self,
        message: AgentMessage,
        context: Dict[str, Any]
    ) -> AsyncIterator[AgentResponse]:
        """
        处理用户消息并返回双模型讨论的流式响应
        """
        try:
            # 获取双模型连接
            connection_a = self._get_llm_connection("model_a")
            connection_b = self._get_llm_connection("model_b")
            
            llm_a = connection_a.llm
            llm_b = connection_b.llm

            # 获取配置参数
            max_rounds = self.config_dict.get("max_discussion_rounds", 5)
            discussion_style = self.config_dict.get("discussion_style", "collaborative")
            enable_summary = self.config_dict.get("enable_summary", True)

            logger.info(f"开始双模型讨论 - topic: {message.content[:50]}...")

            # 发送讨论开始信号
            yield AgentResponse(
                content=f"🎯 **讨论主题**: {message.content}\n\n",
                is_final=False,
                metadata={
                    "discussion_phase": "start",
                    "model_a": self.config_dict.get("model_a_name"),
                    "model_b": self.config_dict.get("model_b_name"),
                    "max_rounds": max_rounds,
                    "style": discussion_style
                }
            )

            # 进行多轮讨论
            discussion_history = []
            for round_num in range(1, max_rounds + 1):
                logger.info(f"开始第{round_num}轮讨论")
                
                # 模型A发言
                yield AgentResponse(
                    content=f"## 🤖 模型A ({self.config_dict.get('model_a_name')}) - 第{round_num}轮\n\n",
                    is_final=False,
                    metadata={"discussion_phase": "model_a_start", "round": round_num}
                )
                
                full_response_a = ""
                async for chunk in self._get_model_response(
                    llm_a, message.content, discussion_history, "model_a", round_num, discussion_style
                ):
                    full_response_a += chunk
                    yield AgentResponse(
                        content=chunk,
                        is_final=False,
                        metadata={"discussion_phase": "model_a_speaking", "round": round_num}
                    )
                
                # 记录模型A的完整响应
                discussion_history.append({
                    "round": round_num,
                    "speaker": "model_a",
                    "content": full_response_a
                })

                yield AgentResponse(content="\n\n", is_final=False)

                # 模型B发言
                yield AgentResponse(
                    content=f"## 🤖 模型B ({self.config_dict.get('model_b_name')}) - 第{round_num}轮\n\n",
                    is_final=False,
                    metadata={"discussion_phase": "model_b_start", "round": round_num}
                )
                
                full_response_b = ""
                async for chunk in self._get_model_response(
                    llm_b, message.content, discussion_history, "model_b", round_num, discussion_style
                ):
                    full_response_b += chunk
                    yield AgentResponse(
                        content=chunk,
                        is_final=False,
                        metadata={"discussion_phase": "model_b_speaking", "round": round_num}
                    )
                
                # 记录模型B的完整响应
                discussion_history.append({
                    "round": round_num,
                    "speaker": "model_b", 
                    "content": full_response_b
                })

                yield AgentResponse(content="\n\n---\n\n", is_final=False)

                # 检查是否应该提前结束讨论
                if await self._should_end_discussion(discussion_history, round_num):
                    logger.info(f"讨论在第{round_num}轮后自然结束")
                    break

            # 生成讨论总结
            summary_content = ""
            if enable_summary:
                yield AgentResponse(
                    content="## 讨论总结\n\n",
                    is_final=False,
                    metadata={"discussion_phase": "summary_start"}
                )

                async for chunk in self._generate_summary(llm_a, message.content, discussion_history):
                    summary_content += chunk
                    yield AgentResponse(
                        content=chunk,
                        is_final=False,
                        metadata={"discussion_phase": "summary"}
                    )

            # 发送最终响应标记
            yield AgentResponse(
                content="",
                is_final=True,
                metadata={
                    "discussion_phase": "complete",
                    "total_rounds": len(discussion_history) // 2,
                    "discussion_history": discussion_history,
                    "summary_content": summary_content  # 添加完整的总结内容
                }
            )

            logger.info("双模型讨论完成")

        except Exception as e:
            logger.error(f"双模型讨论失败 - agent_id: {self.agent_id}, 错误: {e}")
            yield AgentResponse(
                content=f"抱歉，讨论过程中发生错误: {str(e)}",
                is_final=True,
                metadata={"error": str(e)}
            )
        finally:
            # 确保释放所有连接
            self._release_llm_connections()

    async def _get_model_response(
        self,
        llm: ChatOpenAI,
        topic: str,
        history: List[Dict],
        model_role: str,
        round_num: int,
        style: str
    ) -> AsyncIterator[str]:
        """获取指定模型的响应"""
        import time

        messages = self._build_discussion_messages(topic, history, model_role, round_num, style)

        # 记录开始时间和基本信息
        start_time = time.time()
        total_length = 0
        chunk_count = 0

        logger.info(f"🤖 开始调用LLM - 模型: {model_role}, 轮次: {round_num}, "
                   f"agent_id: {self.agent_id}, 消息数: {len(messages)}")

        async for chunk in llm.astream(messages):
            if chunk.content:
                chunk_count += 1
                total_length += len(chunk.content)

                # 每10个chunk或每100个字符记录一次进度
                if chunk_count % 10 == 0 or total_length % 100 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"📝 LLM响应进度 - 模型: {model_role}, 轮次: {round_num}, "
                               f"chunk数: {chunk_count}, 累计长度: {total_length}, "
                               f"耗时: {elapsed:.2f}s")

                yield chunk.content

        # 记录完成信息
        total_time = time.time() - start_time
        logger.info(f"✅ LLM响应完成 - 模型: {model_role}, 轮次: {round_num}, "
                   f"总chunk数: {chunk_count}, 总长度: {total_length}, "
                   f"总耗时: {total_time:.2f}s, 平均速度: {total_length/total_time:.1f}字符/秒")

    def _build_discussion_messages(
        self,
        topic: str,
        history: List[Dict],
        model_role: str,
        round_num: int,
        style: str
    ) -> List:
        """构建讨论消息列表"""
        messages = []

        # 获取模型特定的系统提示
        system_prompt_key = f"{model_role}_system_prompt"
        custom_prompt = self.config_dict.get(system_prompt_key)

        if custom_prompt:
            system_prompt = custom_prompt
        else:
            # 默认系统提示
            if style == "collaborative":
                system_prompt = f"""你是一个智能的讨论参与者，正在与另一个AI模型就特定话题进行协作式讨论。

讨论规则：
1. 保持建设性和协作的态度
2. 基于对方的观点进行深入思考和补充
3. 提供新的视角和见解
4. 避免简单重复，要有创新性思考
5. 保持逻辑清晰，论证有力

当前是第{round_num}轮讨论，请针对话题提供你的观点和分析。"""
            else:  # debate
                system_prompt = f"""你是一个善于辩论的智能参与者，正在与另一个AI模型就特定话题进行辩论式讨论。

辩论规则：
1. 可以质疑对方的观点，但要保持尊重
2. 提供有力的反驳论据和证据
3. 坚持自己的立场，但也要承认合理的观点
4. 逻辑严密，避免人身攻击
5. 追求真理，而非单纯的胜负

当前是第{round_num}轮辩论，请针对话题和对方观点进行回应。"""

        messages.append(SystemMessage(content=system_prompt))

        # 添加讨论历史
        for item in history:
            speaker = "模型A" if item["speaker"] == "model_a" else "模型B"
            if item["speaker"] == model_role:
                messages.append(AIMessage(content=f"[第{item['round']}轮] {item['content']}"))
            else:
                messages.append(HumanMessage(content=f"[第{item['round']}轮 {speaker}] {item['content']}"))

        # 添加当前讨论主题
        if round_num == 1:
            messages.append(HumanMessage(content=f"讨论主题：{topic}"))
        else:
            messages.append(HumanMessage(content=f"请继续就「{topic}」这个主题进行第{round_num}轮讨论"))

        return messages

    async def _should_end_discussion(self, history: List[Dict], current_round: int) -> bool:
        """判断是否应该提前结束讨论"""
        # 简单的结束条件：如果连续两轮讨论内容相似度很高，则结束
        if len(history) >= 4:  # 至少需要两轮完整讨论
            # 这里可以实现更复杂的相似度检测逻辑
            # 暂时返回False，让讨论进行到最大轮数
            pass
        return False

    async def _generate_summary(
        self,
        llm: ChatOpenAI,
        topic: str,
        history: List[Dict]
    ) -> AsyncIterator[str]:
        """生成讨论总结"""
        import time

        summary_prompt = self.config_dict.get("summary_prompt") or """请对以下讨论进行总结：

1. 总结双方的主要观点
2. 指出讨论中的共识和分歧
3. 提供综合性的结论和建议
4. 指出可能的后续讨论方向

请保持客观和全面。"""

        messages = [
            SystemMessage(content=summary_prompt),
            HumanMessage(content=f"讨论主题：{topic}\n\n讨论内容：\n" +
                        "\n".join([f"第{item['round']}轮 {'模型A' if item['speaker'] == 'model_a' else '模型B'}：{item['content']}"
                                 for item in history]))
        ]

        # 记录开始时间和基本信息
        start_time = time.time()
        total_length = 0
        chunk_count = 0

        logger.info(f"📝 开始生成讨论总结 - agent_id: {self.agent_id}, "
                   f"讨论轮数: {len(history)//2}, 历史长度: {sum(len(item['content']) for item in history)}")

        async for chunk in llm.astream(messages):
            if chunk.content:
                chunk_count += 1
                total_length += len(chunk.content)

                # 每5个chunk记录一次进度
                if chunk_count % 5 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"📄 总结生成进度 - chunk数: {chunk_count}, "
                               f"累计长度: {total_length}, 耗时: {elapsed:.2f}s")

                yield chunk.content

        # 记录完成信息
        total_time = time.time() - start_time
        logger.info(f"✅ 讨论总结完成 - 总chunk数: {chunk_count}, 总长度: {total_length}, "
                   f"总耗时: {total_time:.2f}s")

    def get_config_schema(self) -> Dict[str, Any]:
        """返回配置模式定义"""
        return {
            "type": "object",
            "properties": {
                # 模型A配置
                "model_a_name": {
                    "type": "string",
                    "default": "gemini-2.5-flash-preview-05-20",
                    "description": "模型A的名称"
                },
                "model_a_temperature": {
                    "type": "number",
                    "default": 0.7,
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "description": "模型A的随机性控制"
                },
                "model_a_api_key": {
                    "type": "string",
                    "description": "模型A的API密钥"
                },
                "model_a_base_url": {
                    "type": "string",
                    "default": "https://api.openai.com/v1",
                    "description": "模型A的API基础URL"
                },
                "model_a_system_prompt": {
                    "type": "string",
                    "description": "模型A的系统提示词"
                },

                # 模型B配置
                "model_b_name": {
                    "type": "string",
                    "default": "claude-3-sonnet",
                    "description": "模型B的名称"
                },
                "model_b_temperature": {
                    "type": "number",
                    "default": 0.7,
                    "minimum": 0.0,
                    "maximum": 2.0,
                    "description": "模型B的随机性控制"
                },
                "model_b_api_key": {
                    "type": "string",
                    "description": "模型B的API密钥"
                },
                "model_b_base_url": {
                    "type": "string",
                    "default": "https://api.anthropic.com/v1",
                    "description": "模型B的API基础URL"
                },
                "model_b_system_prompt": {
                    "type": "string",
                    "description": "模型B的系统提示词"
                },

                # 讨论配置
                "max_discussion_rounds": {
                    "type": "integer",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10,
                    "description": "最大讨论轮数"
                },
                "discussion_style": {
                    "type": "string",
                    "enum": ["collaborative", "debate"],
                    "default": "collaborative",
                    "description": "讨论风格：协作式或辩论式"
                },
                "enable_summary": {
                    "type": "boolean",
                    "default": True,
                    "description": "是否启用讨论总结"
                },
                "summary_prompt": {
                    "type": "string",
                    "description": "总结提示词（可选）"
                }
            },
            "required": [
                "model_a_name", "model_a_api_key",
                "model_b_name", "model_b_api_key"
            ]
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置参数"""
        required_fields = [
            "model_a_name", "model_a_api_key",
            "model_b_name", "model_b_api_key"
        ]

        # 检查必需字段
        for field in required_fields:
            if field not in config or not config[field]:
                return False

        # 检查temperature范围
        for temp_field in ["model_a_temperature", "model_b_temperature"]:
            if temp_field in config:
                temp = config[temp_field]
                if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                    return False

        # 检查讨论轮数
        if "max_discussion_rounds" in config:
            rounds = config["max_discussion_rounds"]
            if not isinstance(rounds, int) or rounds < 1 or rounds > 10:
                return False

        # 检查讨论风格
        if "discussion_style" in config:
            style = config["discussion_style"]
            if style not in ["collaborative", "debate"]:
                return False

        return True

    def get_supported_features(self) -> List[str]:
        """返回支持的功能特性"""
        return [
            "dual_model_discussion",
            "streaming_response",
            "configurable_models",
            "discussion_summary",
            "collaborative_mode",
            "debate_mode"
        ]
