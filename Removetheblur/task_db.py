"""
任务数据库管理模块 - 使用SQLite持久化任务日志
"""
import sqlite3
import os
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import json


# 任务状态枚举
class TaskStatus:
    PENDING = 'PENDING'
    SUBMITTED = 'SUBMITTED'
    RUNNING = 'RUNNING'
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'
    ORPHANED = 'ORPHANED'  # 孤儿任务（进程丢失）
    CANCELED = 'CANCELED'


class TaskDB:
    """任务数据库管理器"""
    
    def __init__(self, db_path: str = "tasks.db"):
        """
        初始化数据库
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构（优化版）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建任务表（优化结构）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                idempotency_key TEXT UNIQUE,
                status TEXT NOT NULL,
                input_path TEXT NOT NULL,
                input_sha256 TEXT,
                output_path TEXT,
                output_sha256 TEXT,
                output_size INTEGER,
                prompt TEXT,
                model TEXT,
                params_json TEXT,
                request_id TEXT,
                response_id TEXT,
                attempt_count INTEGER DEFAULT 0,
                last_heartbeat_at DATETIME,
                failure_type TEXT,
                error_code TEXT,
                error_message TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                started_at DATETIME,
                finished_at DATETIME,
                -- 兼容旧字段
                session_id TEXT,
                input_folder TEXT,
                output_folder TEXT,
                temp_folder TEXT,
                total_files INTEGER DEFAULT 0,
                processed_files INTEGER DEFAULT 0,
                completed_at DATETIME
            )
        ''')
        
        # 创建任务项表（每张图片的处理记录）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                original_image TEXT NOT NULL,
                original_sha256 TEXT,
                modified_image TEXT,
                modified_sha256 TEXT,
                output_size INTEGER,
                status TEXT NOT NULL,
                error_reason TEXT,
                error_code TEXT,
                attempt_count INTEGER DEFAULT 0,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                started_at DATETIME,
                finished_at DATETIME,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        ''')
        
        # 创建索引（优化查询性能）
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_idempotency ON tasks(idempotency_key)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_heartbeat ON tasks(last_heartbeat_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_session ON tasks(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_created ON tasks(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_task ON task_items(task_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_status ON task_items(status)')
        
        # 迁移旧数据（如果存在）
        try:
            # 检查是否有旧表结构
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
            if cursor.fetchone():
                # 检查是否有新字段
                cursor.execute("PRAGMA table_info(tasks)")
                columns = [row[1] for row in cursor.fetchall()]
                
                # 如果缺少新字段，添加兼容字段
                if 'idempotency_key' not in columns:
                    # 表已存在但结构较旧，添加兼容字段
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN idempotency_key TEXT UNIQUE')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN input_sha256 TEXT')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN output_sha256 TEXT')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN output_size INTEGER')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN model TEXT')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN params_json TEXT')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN request_id TEXT')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN response_id TEXT')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN attempt_count INTEGER DEFAULT 0')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN last_heartbeat_at DATETIME')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN failure_type TEXT')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN error_code TEXT')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN started_at DATETIME')
                    except:
                        pass
                    try:
                        cursor.execute('ALTER TABLE tasks ADD COLUMN finished_at DATETIME')
                    except:
                        pass
        except Exception as e:
            print(f"迁移数据时出错（可忽略）: {e}")
        
        conn.commit()
        conn.close()
    
    def _calculate_sha256(self, file_path: str) -> Optional[str]:
        """计算文件的SHA256哈希值"""
        try:
            if not os.path.exists(file_path):
                return None
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None
    
    def _calculate_folder_hash(self, folder_path: str) -> str:
        """计算文件夹的SHA256哈希（基于文件夹路径和文件列表）"""
        try:
            folder = Path(folder_path)
            if not folder.exists():
                return hashlib.sha256(folder_path.encode()).hexdigest()
            
            # 获取文件夹中所有图片文件的路径和大小
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
            file_info = []
            for file in sorted(folder.iterdir()):
                if file.is_file() and file.suffix.lower() in image_extensions:
                    file_info.append(f"{file.name}:{file.stat().st_size}")
            
            # 计算哈希
            info_str = f"{folder_path}|{'|'.join(file_info)}"
            return hashlib.sha256(info_str.encode()).hexdigest()
        except Exception:
            return hashlib.sha256(folder_path.encode()).hexdigest()
    
    def _generate_idempotency_key(
        self,
        input_sha256: str,
        prompt: Optional[str] = None,
        params: Optional[Dict] = None
    ) -> str:
        """生成幂等性键（基于input_sha256 + prompt_hash + params_hash）"""
        prompt_hash = hashlib.sha256((prompt or '').encode()).hexdigest()[:16]
        params_hash = hashlib.sha256(json.dumps(params or {}, sort_keys=True).encode()).hexdigest()[:16]
        key_str = f"{input_sha256}|{prompt_hash}|{params_hash}"
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def find_task_by_idempotency_key(self, idempotency_key: str) -> Optional[Dict]:
        """
        根据幂等性键查找任务（Phase 2：检查是否已有相同任务）
        
        Args:
            idempotency_key: 幂等性键
        
        Returns:
            任务信息，如果不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM tasks WHERE idempotency_key = ? ORDER BY created_at DESC LIMIT 1', (idempotency_key,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"查找任务失败: {e}")
            return None
        finally:
            conn.close()
    
    def create_task(
        self,
        task_id: str,
        session_id: str,
        input_folder: str,
        output_folder: str,
        temp_folder: str,
        prompt: Optional[str] = None,
        model: str = 'gpt-image-1.5',
        params: Optional[Dict] = None,
        idempotency_key: Optional[str] = None,
        check_idempotency: bool = True
    ) -> Dict:
        """
        创建新任务（Phase 2优化版：扣费前的关键步骤）
        
        Args:
            task_id: 任务ID
            session_id: 会话ID
            input_folder: 输入文件夹
            output_folder: 输出文件夹
            temp_folder: 临时文件夹
            prompt: 提示词
            model: 使用的模型
            params: 额外参数（字典）
            idempotency_key: 幂等性键（如果为None则自动生成）
            check_idempotency: 是否检查幂等性
        
        Returns:
            {
                'created': bool,  # 是否创建了新任务
                'task_id': str,    # 任务ID（可能是新创建的或已存在的）
                'existing': bool,  # 是否是已存在的任务
                'status': str,     # 任务状态
                'result_available': bool  # 如果任务已成功，结果是否可用
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now()
            now_str = now.isoformat()
            
            # Phase 2: 计算哈希值
            input_sha256 = self._calculate_folder_hash(input_folder)
            
            # 生成幂等性键
            if not idempotency_key:
                idempotency_key = self._generate_idempotency_key(input_sha256, prompt, params)
            
            # 转换params为JSON
            params_json = json.dumps(params) if params else None
            
            # Phase 2: 查询数据库，检查是否已有相同任务
            if check_idempotency:
                existing_task = self.find_task_by_idempotency_key(idempotency_key)
                
                if existing_task:
                    existing_status = existing_task['status']
                    existing_id = existing_task['id']
                    
                    # 如果任务已成功，直接返回结果
                    if existing_status == TaskStatus.SUCCEEDED:
                        print(f"✓ 发现已成功的相同任务: {existing_id}，直接返回结果")
                        return {
                            'created': False,
                            'task_id': existing_id,
                            'existing': True,
                            'status': existing_status,
                            'result_available': True,
                            'task': existing_task
                        }
                    
                    # 如果任务正在运行或已提交，返回任务ID供订阅状态
                    if existing_status in (TaskStatus.RUNNING, TaskStatus.SUBMITTED, TaskStatus.PENDING):
                        print(f"✓ 发现相同任务正在处理: {existing_id}，状态: {existing_status}")
                        # 更新最后访问时间
                        cursor.execute('UPDATE tasks SET updated_at = ? WHERE id = ?', (now_str, existing_id))
                        conn.commit()
                        return {
                            'created': False,
                            'task_id': existing_id,
                            'existing': True,
                            'status': existing_status,
                            'result_available': False,
                            'task': existing_task
                        }
            
            # Phase 2: 插入新任务，设置status=PENDING
            cursor.execute('''
                INSERT INTO tasks (
                    id, idempotency_key, status, input_path, input_sha256,
                    output_path, prompt, model, params_json,
                    session_id, input_folder, output_folder, temp_folder,
                    total_files, processed_files,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                task_id, idempotency_key, TaskStatus.PENDING, input_folder, input_sha256,
                output_folder, prompt or '', model, params_json,
                session_id, input_folder, output_folder, temp_folder,
                0, 0,
                now_str, now_str
            ))
            conn.commit()
            
            return {
                'created': True,
                'task_id': task_id,
                'existing': False,
                'status': TaskStatus.PENDING,
                'result_available': False
            }
        except sqlite3.IntegrityError as e:
            # 任务已存在（task_id冲突），更新信息
            try:
                cursor.execute('''
                    UPDATE tasks SET
                        session_id = ?,
                        input_folder = ?,
                        output_folder = ?,
                        temp_folder = ?,
                        prompt = ?,
                        model = ?,
                        params_json = ?,
                        updated_at = ?
                    WHERE id = ?
                ''', (
                    session_id, input_folder, output_folder, temp_folder,
                    prompt or '', model, params_json, now_str, task_id
                ))
                conn.commit()
                return {
                    'created': False,
                    'task_id': task_id,
                    'existing': True,
                    'status': TaskStatus.PENDING,
                    'result_available': False
                }
            except Exception as e2:
                print(f"更新任务失败: {e2}")
                conn.rollback()
                return {
                    'created': False,
                    'task_id': task_id,
                    'existing': False,
                    'status': None,
                    'result_available': False,
                    'error': str(e2)
                }
        except Exception as e:
            print(f"创建任务失败: {e}")
            conn.rollback()
            return {
                'created': False,
                'task_id': task_id,
                'existing': False,
                'status': None,
                'result_available': False,
                'error': str(e)
            }
        finally:
            conn.close()
    
    def update_task_heartbeat(self, task_id: str):
        """更新任务心跳时间"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE tasks SET
                    last_heartbeat_at = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), datetime.now().isoformat(), task_id))
            conn.commit()
        except Exception as e:
            print(f"更新心跳失败: {e}")
        finally:
            conn.close()
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        total_files: Optional[int] = None,
        processed_files: Optional[int] = None,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None,
        failure_type: Optional[str] = None,
        output_path: Optional[str] = None,
        output_size: Optional[int] = None,
        response_id: Optional[str] = None
    ):
        """
        更新任务状态（优化版）
        
        Args:
            task_id: 任务ID
            status: 状态
            total_files: 总文件数
            processed_files: 已处理文件数
            error_message: 错误消息
            error_code: 错误代码
            failure_type: 失败类型
            output_path: 输出路径
            output_size: 输出文件大小
            response_id: 响应ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            updates = ['status = ?', 'updated_at = ?', 'last_heartbeat_at = ?']
            values = [status, now, now]
            
            # 设置开始时间
            if status == TaskStatus.RUNNING:
                updates.append('started_at = COALESCE(started_at, ?)')
                values.append(now)
            
            # 设置结束时间
            if status in (TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.CANCELED):
                updates.append('finished_at = ?')
                updates.append('completed_at = ?')  # 兼容旧字段
                values.extend([now, now])
            
            if total_files is not None:
                updates.append('total_files = ?')
                values.append(total_files)
            
            if processed_files is not None:
                updates.append('processed_files = ?')
                values.append(processed_files)
            
            if error_message is not None:
                updates.append('error_message = ?')
                values.append(error_message)
            
            if error_code is not None:
                updates.append('error_code = ?')
                values.append(error_code)
            
            if failure_type is not None:
                updates.append('failure_type = ?')
                values.append(failure_type)
            
            if output_path is not None:
                updates.append('output_path = ?')
                values.append(output_path)
            
            if output_size is not None:
                updates.append('output_size = ?')
                values.append(output_size)
            
            if response_id is not None:
                updates.append('response_id = ?')
                values.append(response_id)
            
            values.append(task_id)
            
            cursor.execute(f'''
                UPDATE tasks SET {', '.join(updates)}
                WHERE id = ?
            ''', values)
            conn.commit()
        except Exception as e:
            print(f"更新任务状态失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def add_task_item(
        self,
        task_id: str,
        original_image: str,
        modified_image: Optional[str] = None,
        status: str = 'pending',
        error_reason: Optional[str] = None
    ) -> int:
        """
        添加任务项（图片处理记录）
        
        Args:
            task_id: 任务ID
            original_image: 原图路径
            modified_image: 修改后图片路径
            status: 状态
            error_reason: 失败原因
        
        Returns:
            插入的记录ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            cursor.execute('''
                INSERT INTO task_items (
                    task_id, original_image, modified_image, status,
                    error_reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task_id, original_image, modified_image or '', status, error_reason or '', now, now))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"添加任务项失败: {e}")
            conn.rollback()
            return -1
        finally:
            conn.close()
    
    def update_task_item(
        self,
        task_id: str,
        original_image: str,
        modified_image: Optional[str] = None,
        status: str = 'completed',
        error_reason: Optional[str] = None,
        output_size: Optional[int] = None,
        modified_sha256: Optional[str] = None,
        error_code: Optional[str] = None
    ):
        """
        更新任务项状态（Phase 5优化版）
        
        Args:
            task_id: 任务ID
            original_image: 原图路径
            modified_image: 修改后图片路径
            status: 状态
            error_reason: 失败原因
            output_size: 输出文件大小
            modified_sha256: 修改后图片的SHA256
            error_code: 错误代码
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            now = datetime.now().isoformat()
            updates = ['modified_image = ?', 'status = ?', 'updated_at = ?']
            values = [modified_image or '', status, now]
            
            if output_size is not None:
                updates.append('output_size = ?')
                values.append(output_size)
            
            if modified_sha256 is not None:
                updates.append('modified_sha256 = ?')
                values.append(modified_sha256)
            
            if error_reason is not None:
                updates.append('error_reason = ?')
                values.append(error_reason)
            
            if error_code is not None:
                updates.append('error_code = ?')
                values.append(error_code)
            
            if status == 'completed':
                updates.append('finished_at = ?')
                values.append(now)
            elif status == 'failed':
                updates.append('finished_at = ?')
                values.append(now)
            
            values.extend([task_id, original_image])
            
            cursor.execute(f'''
                UPDATE task_items SET {', '.join(updates)}
                WHERE task_id = ? AND original_image = ?
            ''', values)
            conn.commit()
        except Exception as e:
            print(f"更新任务项失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def get_unfinished_tasks(self) -> List[Dict]:
        """
        获取未完成的任务列表
        
        Returns:
            未完成任务列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM tasks
                WHERE status IN (?, ?, ?)
                ORDER BY created_at ASC
            ''', (TaskStatus.PENDING, TaskStatus.SUBMITTED, TaskStatus.RUNNING))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"获取未完成任务失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_orphaned_tasks(self, heartbeat_timeout_minutes: int = 30) -> List[Dict]:
        """
        获取孤儿任务（心跳超时的运行中任务）
        
        Args:
            heartbeat_timeout_minutes: 心跳超时时间（分钟）
        
        Returns:
            孤儿任务列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            timeout_threshold = (datetime.now() - timedelta(minutes=heartbeat_timeout_minutes)).isoformat()
            cursor.execute('''
                SELECT * FROM tasks
                WHERE status = ? 
                AND (last_heartbeat_at IS NULL OR last_heartbeat_at < ?)
                ORDER BY created_at ASC
            ''', (TaskStatus.RUNNING, timeout_threshold))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"获取孤儿任务失败: {e}")
            return []
        finally:
            conn.close()
    
    def mark_task_orphaned(self, task_id: str):
        """标记任务为孤儿状态"""
        self.update_task_status(
            task_id=task_id,
            status=TaskStatus.ORPHANED,
            failure_type='heartbeat_timeout',
            error_message='任务心跳超时，可能进程已丢失'
        )
    
    def get_task_items(self, task_id: str) -> List[Dict]:
        """
        获取任务的所有任务项
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务项列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM task_items
                WHERE task_id = ?
                ORDER BY id ASC
            ''', (task_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"获取任务项失败: {e}")
            return []
        finally:
            conn.close()
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务信息字典，如果不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"获取任务失败: {e}")
            return None
        finally:
            conn.close()
    
    def increment_attempt_count(self, task_id: str):
        """增加任务尝试次数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE tasks SET
                    attempt_count = attempt_count + 1,
                    updated_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), task_id))
            conn.commit()
        except Exception as e:
            print(f"增加尝试次数失败: {e}")
        finally:
            conn.close()
    
    def get_pending_items(self, task_id: str) -> List[Dict]:
        """
        获取待处理的任务项
        
        Args:
            task_id: 任务ID
        
        Returns:
            待处理的任务项列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM task_items
                WHERE task_id = ? AND status IN ('pending', 'processing')
                ORDER BY id ASC
            ''', (task_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"获取待处理任务项失败: {e}")
            return []
        finally:
            conn.close()

