"""
预热式LLM连接池
在应用启动时为每个Agent预创建LLM实例，提供高效的连接复用
"""
import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from queue import Queue, Empty
import threading
from .logger import logger


@dataclass
class LLMConnection:
    """LLM连接包装器"""
    llm: ChatOpenAI
    agent_id: str
    agent_type: str
    created_at: float
    last_used: float
    usage_count: int = 0
    is_busy: bool = False
    connection_id: str = ""


class PrewarmLLMPool:
    """预热式LLM连接池"""
    
    def __init__(self, pool_size_per_agent: int = 5, max_idle_time: int = 600):
        """
        初始化连接池
        
        Args:
            pool_size_per_agent: 每个Agent的连接池大小
            max_idle_time: 最大闲置时间（秒）
        """
        self.pool_size_per_agent = pool_size_per_agent
        self.max_idle_time = max_idle_time
        
        # 连接池：agent_id -> Queue[LLMConnection]
        self.pools: Dict[str, Queue] = {}
        
        # 活跃连接：connection_id -> LLMConnection
        self.active_connections: Dict[str, LLMConnection] = {}

        # Agent配置缓存：agent_id -> config (用于配置变更检测)
        self.agent_configs: Dict[str, Dict[str, Any]] = {}

        # 统计信息
        self.stats = {
            "total_created": 0,
            "total_reused": 0,
            "total_released": 0,
            "total_recycled": 0,
            "current_active": 0,
            "current_idle": 0
        }
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 清理任务
        self._cleanup_task = None
        self._start_cleanup_task()
        
        logger.info(f"LLM连接池初始化完成 - 每Agent连接数: {pool_size_per_agent}, 最大闲置时间: {max_idle_time}秒")

    def _config_changed(self, agent_id: str, new_config: Dict[str, Any]) -> bool:
        """检测Agent配置是否发生变化"""
        if agent_id not in self.agent_configs:
            return True  # 首次配置

        old_config = self.agent_configs[agent_id]

        # 比较关键配置项
        key_fields = ["model_name", "api_key", "base_url", "temperature", "max_tokens"]
        for field in key_fields:
            if old_config.get(field) != new_config.get(field):
                logger.info(f"检测到Agent {agent_id} 配置变更: {field} 从 '{old_config.get(field)}' 变为 '{new_config.get(field)}'")
                return True

        return False

    def _clear_agent_pool(self, agent_id: str):
        """清理指定Agent的连接池"""
        if agent_id in self.pools:
            pool = self.pools[agent_id]

            # 清理池中的所有连接
            cleared_count = 0
            while not pool.empty():
                try:
                    connection = pool.get_nowait()
                    self._recycle_connection(connection)
                    cleared_count += 1
                except Empty:
                    break

            # 删除连接池
            del self.pools[agent_id]
            logger.info(f"清理Agent {agent_id} 的连接池，清理了 {cleared_count} 个连接")

        # 清理相关的活跃连接
        connections_to_remove = []
        for conn_id, connection in self.active_connections.items():
            if connection.agent_id == agent_id:
                connections_to_remove.append(conn_id)

        for conn_id in connections_to_remove:
            self._recycle_connection(self.active_connections[conn_id])
            del self.active_connections[conn_id]

        if connections_to_remove:
            logger.info(f"清理Agent {agent_id} 的活跃连接，清理了 {len(connections_to_remove)} 个连接")

    def clear_agent_connections(self, agent_id: str, agent_type: str = None):
        """公共方法：清理指定Agent的所有连接（用于配置更新）"""
        logger.info(f"开始清理Agent {agent_id} 的连接池和缓存")

        with self.lock:
            # 对于头脑风暴Agent，需要清理两个模型的连接
            if agent_type == "brainstorm_agent":
                model_a_id = f"{agent_id}_model_a"
                model_b_id = f"{agent_id}_model_b"

                self._clear_agent_pool(model_a_id)
                self._clear_agent_pool(model_b_id)

                # 清理配置缓存
                if model_a_id in self.agent_configs:
                    del self.agent_configs[model_a_id]
                if model_b_id in self.agent_configs:
                    del self.agent_configs[model_b_id]

                logger.info(f"清理头脑风暴Agent {agent_id} 的双模型连接完成")
            else:
                # 单模型Agent
                self._clear_agent_pool(agent_id)

                # 清理配置缓存
                if agent_id in self.agent_configs:
                    del self.agent_configs[agent_id]

                logger.info(f"清理单模型Agent {agent_id} 的连接完成")

    def _start_cleanup_task(self):
        """启动清理任务"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(60)  # 每分钟检查一次
                    self._cleanup_idle_connections()
                except Exception as e:
                    logger.error(f"连接池清理任务异常: {e}")
        
        self._cleanup_task = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_task.start()
        logger.info("连接池清理任务已启动")
    
    def prewarm_agent_pool(self, agent_id: str, agent_type: str, config: Dict[str, Any]):
        """为指定Agent预热连接池"""
        if agent_type == "brainstorm_agent":
            # 双模型Agent需要为两个模型分别预热连接池
            model_a_config = {
                "model_name": config.get("model_a_name"),
                "temperature": config.get("model_a_temperature", 0.7),
                "api_key": config.get("model_a_api_key"),
                "base_url": config.get("model_a_base_url", "https://api.openai.com/v1"),
                "max_tokens": config.get("max_tokens")
            }

            model_b_config = {
                "model_name": config.get("model_b_name"),
                "temperature": config.get("model_b_temperature", 0.7),
                "api_key": config.get("model_b_api_key"),
                "base_url": config.get("model_b_base_url", "https://api.openai.com/v1"),
                "max_tokens": config.get("max_tokens")
            }

            # 为模型A预热连接池
            self._prewarm_single_model(f"{agent_id}_model_a", agent_type, model_a_config)
            # 为模型B预热连接池
            self._prewarm_single_model(f"{agent_id}_model_b", agent_type, model_b_config)

            # 缓存双模型配置
            self.agent_configs[f"{agent_id}_model_a"] = model_a_config.copy()
            self.agent_configs[f"{agent_id}_model_b"] = model_b_config.copy()
        else:
            # 单模型Agent的原有逻辑
            self._prewarm_single_model(agent_id, agent_type, config)
            # 缓存单模型配置
            self.agent_configs[agent_id] = config.copy()

    def _prewarm_single_model(self, agent_id: str, agent_type: str, config: Dict[str, Any]):
        """为单个模型预热连接池"""
        with self.lock:
            if agent_id in self.pools:
                logger.warning(f"Agent {agent_id} 的连接池已存在，跳过预热")
                return

            logger.info(f"开始为Agent预热连接池 - agent_id: {agent_id}, agent_type: {agent_type}")

            # 创建连接队列
            pool = Queue(maxsize=self.pool_size_per_agent)

            # 预创建连接
            for i in range(self.pool_size_per_agent):
                try:
                    connection_id = f"{agent_id}_{agent_type}_{i}_{int(time.time())}"
                    logger.debug(f"正在创建LLM实例 - connection_id: {connection_id}, 配置: {config}")

                    llm = self._create_llm(config)
                    logger.debug(f"LLM实例创建成功 - connection_id: {connection_id}")

                    connection = LLMConnection(
                        llm=llm,
                        agent_id=agent_id,
                        agent_type=agent_type,
                        created_at=time.time(),
                        last_used=time.time(),
                        connection_id=connection_id
                    )

                    pool.put(connection)
                    self.stats["total_created"] += 1
                    self.stats["current_idle"] += 1

                    logger.debug(f"预创建LLM连接成功 - connection_id: {connection_id}")

                except Exception as e:
                    logger.error(f"预创建LLM连接失败 - agent_id: {agent_id}, connection_id: {connection_id}, 错误: {e}")
                    logger.exception("预创建LLM连接异常详情")

            self.pools[agent_id] = pool
            logger.info(f"Agent连接池预热完成 - agent_id: {agent_id}, 连接数: {pool.qsize()}")
    
    def get_llm_connection(self, agent_id: str, agent_type: str, config: Dict[str, Any]) -> Optional[LLMConnection]:
        """获取LLM连接"""
        with self.lock:
            # 检查配置是否发生变化
            if self._config_changed(agent_id, config):
                logger.info(f"Agent {agent_id} 配置发生变化，清理旧连接池")
                self._clear_agent_pool(agent_id)
                # 更新配置缓存
                self.agent_configs[agent_id] = config.copy()

            # 检查是否有预热的连接池
            if agent_id not in self.pools:
                logger.warning(f"Agent {agent_id} 没有预热连接池，动态创建")

                # 对于头脑风暴Agent的子模型，需要特殊处理
                if agent_type == "brainstorm_agent" and ("_model_a" in agent_id or "_model_b" in agent_id):
                    # 这是头脑风暴Agent的子模型，直接创建单个模型的连接池
                    logger.info(f"为头脑风暴Agent子模型 {agent_id} 动态创建连接池")
                    self._prewarm_single_model(agent_id, agent_type, config)
                    # 缓存子模型配置
                    self.agent_configs[agent_id] = config.copy()
                else:
                    # 普通Agent或完整的头脑风暴Agent
                    self.prewarm_agent_pool(agent_id, agent_type, config)

            pool = self.pools[agent_id]
            
            try:
                # 尝试从池中获取连接
                connection = pool.get_nowait()
                connection.last_used = time.time()
                connection.usage_count += 1
                connection.is_busy = True
                
                # 移动到活跃连接
                self.active_connections[connection.connection_id] = connection
                
                # 更新统计
                self.stats["total_reused"] += 1
                self.stats["current_active"] += 1
                self.stats["current_idle"] -= 1
                
                logger.info(f"复用LLM连接 - connection_id: {connection.connection_id}, "
                          f"使用次数: {connection.usage_count}, agent_id: {agent_id}, "
                          f"池状态: 活跃{self.stats['current_active']}/空闲{self.stats['current_idle']}")

                return connection
                
            except Empty:
                # 池中没有可用连接，创建新连接
                logger.warning(f"连接池已空，创建临时连接 - agent_id: {agent_id}")
                return self._create_temporary_connection(agent_id, agent_type, config)
    
    def release_llm_connection(self, connection_id: str):
        """释放LLM连接回池中"""
        with self.lock:
            if connection_id not in self.active_connections:
                logger.warning(f"尝试释放不存在的连接 - connection_id: {connection_id}")
                return
            
            connection = self.active_connections[connection_id]
            connection.is_busy = False
            connection.last_used = time.time()
            
            # 从活跃连接中移除
            del self.active_connections[connection_id]
            
            # 检查连接是否还有效
            if self._is_connection_valid(connection):
                # 放回连接池
                agent_id = connection.agent_id
                if agent_id in self.pools:
                    try:
                        self.pools[agent_id].put_nowait(connection)
                        
                        # 更新统计
                        self.stats["total_released"] += 1
                        self.stats["current_active"] -= 1
                        self.stats["current_idle"] += 1
                        
                        logger.info(f"释放LLM连接回池 - connection_id: {connection_id}, agent_id: {agent_id}, "
                                   f"池状态: 活跃{self.stats['current_active']}/空闲{self.stats['current_idle']}")

                    except Exception as e:
                        logger.error(f"释放连接回池失败 - connection_id: {connection_id}, 错误: {e}")
                        self._recycle_connection(connection)
                else:
                    logger.warning(f"Agent池不存在，回收连接 - agent_id: {agent_id}")
                    self._recycle_connection(connection)
            else:
                logger.info(f"连接已失效，回收连接 - connection_id: {connection_id}")
                self._recycle_connection(connection)
    
    def _create_llm(self, config: Dict[str, Any]) -> ChatOpenAI:
        """创建LLM实例"""
        return ChatOpenAI(
            model=config["model_name"],
            temperature=config["temperature"],
            max_tokens=config.get("max_tokens"),
            api_key=config["api_key"],
            base_url=config["base_url"],
            streaming=True
        )
    
    def _create_temporary_connection(self, agent_id: str, agent_type: str, config: Dict[str, Any]) -> LLMConnection:
        """创建临时连接（当池中没有可用连接时）"""
        connection_id = f"{agent_id}_{agent_type}_temp_{int(time.time())}"
        
        try:
            llm = self._create_llm(config)
            
            connection = LLMConnection(
                llm=llm,
                agent_id=agent_id,
                agent_type=agent_type,
                created_at=time.time(),
                last_used=time.time(),
                usage_count=1,
                is_busy=True,
                connection_id=connection_id
            )
            
            # 添加到活跃连接
            self.active_connections[connection_id] = connection
            
            # 更新统计
            self.stats["total_created"] += 1
            self.stats["current_active"] += 1
            
            logger.warning(f"创建临时LLM连接 - connection_id: {connection_id}, agent_id: {agent_id}")
            
            return connection
            
        except Exception as e:
            logger.error(f"创建临时连接失败 - agent_id: {agent_id}, 错误: {e}")
            raise
    
    def _is_connection_valid(self, connection: LLMConnection) -> bool:
        """检查连接是否有效"""
        # 检查连接年龄
        age = time.time() - connection.created_at
        if age > self.max_idle_time:
            return False
        
        # 可以添加更多有效性检查
        return True
    
    def _recycle_connection(self, connection: LLMConnection):
        """回收连接"""
        try:
            # 这里可以添加连接清理逻辑
            # 例如关闭网络连接等
            
            self.stats["total_recycled"] += 1
            self.stats["current_active"] = max(0, self.stats["current_active"] - 1)
            
            logger.debug(f"回收LLM连接 - connection_id: {connection.connection_id}")
            
        except Exception as e:
            logger.error(f"回收连接失败 - connection_id: {connection.connection_id}, 错误: {e}")
    
    def _cleanup_idle_connections(self):
        """清理闲置连接"""
        with self.lock:
            current_time = time.time()
            cleaned_count = 0
            
            for agent_id, pool in self.pools.items():
                # 临时存储有效连接
                valid_connections = []
                
                # 检查池中的所有连接
                while not pool.empty():
                    try:
                        connection = pool.get_nowait()
                        
                        if current_time - connection.last_used <= self.max_idle_time:
                            valid_connections.append(connection)
                        else:
                            self._recycle_connection(connection)
                            cleaned_count += 1
                            self.stats["current_idle"] -= 1
                            
                    except Empty:
                        break
                
                # 将有效连接放回池中
                for connection in valid_connections:
                    try:
                        pool.put_nowait(connection)
                    except Exception as e:
                        logger.error(f"放回有效连接失败: {e}")
                        self._recycle_connection(connection)
            
            if cleaned_count > 0:
                logger.info(f"清理闲置连接完成 - 清理数量: {cleaned_count}")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        with self.lock:
            pool_details = {}
            for agent_id, pool in self.pools.items():
                pool_details[agent_id] = {
                    "idle_connections": pool.qsize(),
                    "pool_size": self.pool_size_per_agent
                }
            
            return {
                "stats": self.stats.copy(),
                "pool_details": pool_details,
                "active_connections": len(self.active_connections),
                "total_pools": len(self.pools)
            }
    
    def shutdown(self):
        """关闭连接池"""
        with self.lock:
            logger.info("开始关闭LLM连接池...")
            
            # 回收所有活跃连接
            for connection in list(self.active_connections.values()):
                self._recycle_connection(connection)
            self.active_connections.clear()
            
            # 回收所有池中的连接
            for agent_id, pool in self.pools.items():
                while not pool.empty():
                    try:
                        connection = pool.get_nowait()
                        self._recycle_connection(connection)
                    except Empty:
                        break
            
            self.pools.clear()
            logger.info("LLM连接池关闭完成")


# 全局连接池实例
llm_pool = PrewarmLLMPool(pool_size_per_agent=5, max_idle_time=600)
