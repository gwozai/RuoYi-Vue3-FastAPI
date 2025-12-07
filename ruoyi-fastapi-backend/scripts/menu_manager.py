#!/usr/bin/env python3
"""
菜单管理命令行工具

使用方法:
    # 添加目录菜单
    python scripts/menu_manager.py add-dir --name "语音服务" --path voice --icon message --order 0
    
    # 添加页面菜单
    python scripts/menu_manager.py add-menu --name "音频生成" --parent "语音服务" --path audio --component "voice/audio/index" --perms "voice:audio:list"
    
    # 添加按钮权限
    python scripts/menu_manager.py add-button --name "新增" --parent "音频生成" --perms "voice:audio:add"
    
    # 列出所有菜单
    python scripts/menu_manager.py list
    
    # 删除菜单
    python scripts/menu_manager.py delete --name "测试菜单"
    
    # 移动菜单
    python scripts/menu_manager.py move --name "音频生成" --parent "语音服务"
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# 添加项目根目录到 Python 路径
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 必须在导入其他模块之前设置环境变量
os.environ.setdefault('APP_ENV', 'dev')


class MenuManager:
    """菜单管理器"""
    
    # 常用图标
    ICONS = {
        'system': 'system',
        'monitor': 'monitor',
        'tool': 'tool',
        'guide': 'guide',
        'user': 'user',
        'peoples': 'peoples',
        'tree': 'tree',
        'menu': 'tree-table',
        'message': 'message',
        'log': 'log',
        'dict': 'dict',
        'edit': 'edit',
        'list': 'list',
        'chart': 'chart',
        'form': 'form',
        'table': 'table',
        'code': 'code',
        'build': 'build',
        'server': 'server',
        'job': 'job',
        'online': 'online',
        'redis': 'redis',
        'download': 'download',
        'upload': 'upload',
        'star': 'star',
        'link': 'link',
        'example': 'example',
        'documentation': 'documentation',
    }
    
    def __init__(self):
        self.db = None
        
    async def _get_db(self):
        """获取数据库连接"""
        if self.db is None:
            from config.get_db import get_db
            async for db in get_db():
                self.db = db
                return db
        return self.db
    
    async def _close_db(self):
        """关闭数据库连接"""
        if self.db:
            await self.db.close()
            
    async def get_menu_by_name(self, name: str) -> Optional[Any]:
        """根据名称获取菜单"""
        from sqlalchemy import select
        from module_admin.entity.do.menu_do import SysMenu
        
        db = await self._get_db()
        result = await db.execute(
            select(SysMenu).where(SysMenu.menu_name == name)
        )
        return result.scalars().first()
    
    async def get_menu_by_id(self, menu_id: int) -> Optional[Any]:
        """根据ID获取菜单"""
        from sqlalchemy import select
        from module_admin.entity.do.menu_do import SysMenu
        
        db = await self._get_db()
        result = await db.execute(
            select(SysMenu).where(SysMenu.menu_id == menu_id)
        )
        return result.scalars().first()
    
    async def list_menus(self, parent_id: int = None) -> List[Dict]:
        """列出菜单"""
        from sqlalchemy import select
        from module_admin.entity.do.menu_do import SysMenu
        
        db = await self._get_db()
        query = select(SysMenu).order_by(SysMenu.parent_id, SysMenu.order_num)
        if parent_id is not None:
            query = query.where(SysMenu.parent_id == parent_id)
        
        result = await db.execute(query)
        menus = result.scalars().all()
        
        return [{
            'menu_id': m.menu_id,
            'menu_name': m.menu_name,
            'parent_id': m.parent_id,
            'order_num': m.order_num,
            'path': m.path,
            'component': m.component,
            'menu_type': m.menu_type,
            'perms': m.perms,
            'icon': m.icon,
            'status': m.status,
        } for m in menus]
    
    async def add_directory(
        self,
        name: str,
        path: str,
        icon: str = '#',
        order: int = 0,
        parent_id: int = 0,
        visible: str = '0',
        status: str = '0',
    ) -> int:
        """添加目录菜单"""
        from module_admin.entity.do.menu_do import SysMenu
        
        db = await self._get_db()
        
        # 检查是否已存在
        existing = await self.get_menu_by_name(name)
        if existing:
            print(f"⚠️  菜单 '{name}' 已存在 (ID: {existing.menu_id})")
            return existing.menu_id
        
        menu = SysMenu(
            menu_name=name,
            parent_id=parent_id,
            order_num=order,
            path=path,
            component='',
            is_frame=1,
            is_cache=0,
            menu_type='M',  # 目录
            visible=visible,
            status=status,
            perms='',
            icon=icon,
            create_by='admin',
            create_time=datetime.now(),
        )
        
        db.add(menu)
        await db.commit()
        await db.refresh(menu)
        
        print(f"✅ 目录菜单 '{name}' 创建成功 (ID: {menu.menu_id})")
        return menu.menu_id
    
    async def add_menu(
        self,
        name: str,
        path: str,
        component: str,
        perms: str,
        parent_name: str = None,
        parent_id: int = 0,
        icon: str = '#',
        order: int = 1,
        visible: str = '0',
        status: str = '0',
        is_cache: int = 0,
    ) -> int:
        """添加页面菜单"""
        from module_admin.entity.do.menu_do import SysMenu
        
        db = await self._get_db()
        
        # 获取父菜单ID
        if parent_name:
            parent = await self.get_menu_by_name(parent_name)
            if parent:
                parent_id = parent.menu_id
            else:
                print(f"⚠️  父菜单 '{parent_name}' 不存在")
                return -1
        
        # 检查是否已存在
        existing = await self.get_menu_by_name(name)
        if existing:
            print(f"⚠️  菜单 '{name}' 已存在 (ID: {existing.menu_id})")
            return existing.menu_id
        
        menu = SysMenu(
            menu_name=name,
            parent_id=parent_id,
            order_num=order,
            path=path,
            component=component,
            is_frame=1,
            is_cache=is_cache,
            menu_type='C',  # 菜单
            visible=visible,
            status=status,
            perms=perms,
            icon=icon,
            create_by='admin',
            create_time=datetime.now(),
        )
        
        db.add(menu)
        await db.commit()
        await db.refresh(menu)
        
        print(f"✅ 页面菜单 '{name}' 创建成功 (ID: {menu.menu_id})")
        return menu.menu_id
    
    async def add_button(
        self,
        name: str,
        perms: str,
        parent_name: str = None,
        parent_id: int = 0,
        order: int = 1,
    ) -> int:
        """添加按钮权限"""
        from module_admin.entity.do.menu_do import SysMenu
        
        db = await self._get_db()
        
        # 获取父菜单ID
        if parent_name:
            parent = await self.get_menu_by_name(parent_name)
            if parent:
                parent_id = parent.menu_id
            else:
                print(f"⚠️  父菜单 '{parent_name}' 不存在")
                return -1
        
        # 检查是否已存在
        from sqlalchemy import select, and_
        from module_admin.entity.do.menu_do import SysMenu as SM
        result = await db.execute(
            select(SM).where(and_(SM.menu_name == name, SM.parent_id == parent_id))
        )
        existing = result.scalars().first()
        if existing:
            print(f"⚠️  按钮 '{name}' 已存在 (ID: {existing.menu_id})")
            return existing.menu_id
        
        menu = SysMenu(
            menu_name=name,
            parent_id=parent_id,
            order_num=order,
            path='',
            component='',
            is_frame=1,
            is_cache=0,
            menu_type='F',  # 按钮
            visible='0',
            status='0',
            perms=perms,
            icon='#',
            create_by='admin',
            create_time=datetime.now(),
        )
        
        db.add(menu)
        await db.commit()
        await db.refresh(menu)
        
        print(f"✅ 按钮权限 '{name}' 创建成功 (ID: {menu.menu_id})")
        return menu.menu_id
    
    async def add_crud_buttons(self, parent_name: str, module: str, business: str) -> List[int]:
        """添加标准 CRUD 按钮权限"""
        buttons = [
            ('查询', f'{module}:{business}:query', 1),
            ('新增', f'{module}:{business}:add', 2),
            ('修改', f'{module}:{business}:edit', 3),
            ('删除', f'{module}:{business}:remove', 4),
            ('导出', f'{module}:{business}:export', 5),
        ]
        
        ids = []
        for name, perms, order in buttons:
            menu_id = await self.add_button(name, perms, parent_name, order=order)
            ids.append(menu_id)
        
        return ids
    
    async def delete_menu(self, name: str = None, menu_id: int = None, recursive: bool = False) -> bool:
        """删除菜单
        
        Args:
            name: 菜单名称
            menu_id: 菜单ID
            recursive: 是否递归删除子菜单
        """
        from sqlalchemy import delete, select
        from module_admin.entity.do.menu_do import SysMenu
        
        db = await self._get_db()
        
        if name:
            menu = await self.get_menu_by_name(name)
            if not menu:
                print(f"⚠️  菜单 '{name}' 不存在")
                return False
            menu_id = menu.menu_id
        
        if not menu_id:
            print("⚠️  请指定菜单名称或ID")
            return False
        
        # 收集所有要删除的菜单ID
        ids_to_delete = []
        
        async def collect_ids(parent_id: int):
            ids_to_delete.append(parent_id)
            result = await db.execute(
                select(SysMenu).where(SysMenu.parent_id == parent_id)
            )
            children = result.scalars().all()
            for child in children:
                await collect_ids(child.menu_id)
        
        # 检查是否有子菜单
        result = await db.execute(
            select(SysMenu).where(SysMenu.parent_id == menu_id)
        )
        children = result.scalars().all()
        
        if children:
            if recursive:
                # 收集所有子菜单ID
                await collect_ids(menu_id)
            else:
                print(f"⚠️  菜单下有 {len(children)} 个子菜单，使用 --recursive 递归删除")
                return False
        else:
            ids_to_delete.append(menu_id)
        
        # 批量删除（从子到父）
        for mid in reversed(ids_to_delete):
            await db.execute(delete(SysMenu).where(SysMenu.menu_id == mid))
            print(f"✅ 菜单删除成功 (ID: {mid})")
        
        await db.commit()
        return True
    
    async def move_menu(self, name: str, parent_name: str) -> bool:
        """移动菜单到新的父菜单下"""
        from sqlalchemy import update
        from module_admin.entity.do.menu_do import SysMenu
        
        db = await self._get_db()
        
        menu = await self.get_menu_by_name(name)
        if not menu:
            print(f"⚠️  菜单 '{name}' 不存在")
            return False
        
        parent = await self.get_menu_by_name(parent_name)
        if not parent:
            print(f"⚠️  父菜单 '{parent_name}' 不存在")
            return False
        
        await db.execute(
            update(SysMenu)
            .where(SysMenu.menu_id == menu.menu_id)
            .values(parent_id=parent.menu_id, update_time=datetime.now())
        )
        await db.commit()
        
        print(f"✅ 菜单 '{name}' 已移动到 '{parent_name}' 下")
        return True
    
    async def update_menu(
        self,
        name: str,
        new_name: str = None,
        path: str = None,
        component: str = None,
        perms: str = None,
        icon: str = None,
        order: int = None,
        visible: str = None,
        status: str = None,
    ) -> bool:
        """更新菜单"""
        from sqlalchemy import update
        from module_admin.entity.do.menu_do import SysMenu
        
        db = await self._get_db()
        
        menu = await self.get_menu_by_name(name)
        if not menu:
            print(f"⚠️  菜单 '{name}' 不存在")
            return False
        
        values = {'update_time': datetime.now()}
        if new_name:
            values['menu_name'] = new_name
        if path:
            values['path'] = path
        if component:
            values['component'] = component
        if perms:
            values['perms'] = perms
        if icon:
            values['icon'] = icon
        if order is not None:
            values['order_num'] = order
        if visible:
            values['visible'] = visible
        if status:
            values['status'] = status
        
        await db.execute(
            update(SysMenu)
            .where(SysMenu.menu_id == menu.menu_id)
            .values(**values)
        )
        await db.commit()
        
        print(f"✅ 菜单 '{name}' 更新成功")
        return True
    
    async def create_module_menus(
        self,
        module_name: str,
        module_path: str,
        business_name: str,
        business_path: str,
        component: str,
        icon: str = '#',
        parent_id: int = 0,
    ) -> Dict[str, int]:
        """创建完整的模块菜单（目录 + 页面 + CRUD按钮）"""
        perms_prefix = f"{module_path}:{business_path}"
        
        # 1. 创建目录（如果不存在）
        dir_menu = await self.get_menu_by_name(module_name)
        if dir_menu:
            dir_id = dir_menu.menu_id
            print(f"📁 目录 '{module_name}' 已存在 (ID: {dir_id})")
        else:
            dir_id = await self.add_directory(
                name=module_name,
                path=module_path,
                icon=icon,
                order=0,
                parent_id=parent_id,
            )
        
        # 2. 创建页面菜单
        page_id = await self.add_menu(
            name=business_name,
            path=business_path,
            component=component,
            perms=f"{perms_prefix}:list",
            parent_id=dir_id,
            order=1,
        )
        
        # 3. 创建 CRUD 按钮
        button_ids = await self.add_crud_buttons(business_name, module_path, business_path)
        
        return {
            'directory_id': dir_id,
            'page_id': page_id,
            'button_ids': button_ids,
        }


# ============ API 函数 ============

async def _run_async(coro):
    """运行异步函数"""
    return await coro


def add_directory(name: str, path: str, icon: str = '#', order: int = 0, parent: str = None) -> int:
    """
    添加目录菜单
    
    Args:
        name: 目录名称
        path: 路由路径
        icon: 图标
        order: 排序
        parent: 父菜单名称
    
    Returns:
        菜单ID
    """
    async def _add():
        manager = MenuManager()
        parent_id = 0
        if parent:
            p = await manager.get_menu_by_name(parent)
            if p:
                parent_id = p.menu_id
        result = await manager.add_directory(name, path, icon, order, parent_id)
        await manager._close_db()
        return result
    
    return asyncio.run(_add())


def add_menu(
    name: str,
    path: str,
    component: str,
    perms: str,
    parent: str = None,
    icon: str = '#',
    order: int = 1,
) -> int:
    """
    添加页面菜单
    
    Args:
        name: 菜单名称
        path: 路由路径
        component: 组件路径 (如 system/user/index)
        perms: 权限标识 (如 system:user:list)
        parent: 父菜单名称
        icon: 图标
        order: 排序
    
    Returns:
        菜单ID
    """
    async def _add():
        manager = MenuManager()
        result = await manager.add_menu(
            name=name,
            path=path,
            component=component,
            perms=perms,
            parent_name=parent,
            icon=icon,
            order=order,
        )
        await manager._close_db()
        return result
    
    return asyncio.run(_add())


def add_button(name: str, perms: str, parent: str, order: int = 1) -> int:
    """
    添加按钮权限
    
    Args:
        name: 按钮名称 (如 新增、修改、删除)
        perms: 权限标识 (如 system:user:add)
        parent: 父菜单名称
        order: 排序
    
    Returns:
        菜单ID
    """
    async def _add():
        manager = MenuManager()
        result = await manager.add_button(name, perms, parent, order=order)
        await manager._close_db()
        return result
    
    return asyncio.run(_add())


def add_crud_buttons(parent: str, module: str, business: str) -> List[int]:
    """
    添加标准 CRUD 按钮 (查询、新增、修改、删除、导出)
    
    Args:
        parent: 父菜单名称
        module: 模块名 (如 system)
        business: 业务名 (如 user)
    
    Returns:
        按钮ID列表
    """
    async def _add():
        manager = MenuManager()
        result = await manager.add_crud_buttons(parent, module, business)
        await manager._close_db()
        return result
    
    return asyncio.run(_add())


def create_module(
    module_name: str,
    module_path: str,
    business_name: str,
    business_path: str,
    component: str,
    icon: str = '#',
) -> Dict[str, int]:
    """
    创建完整模块菜单 (目录 + 页面 + CRUD按钮)
    
    Args:
        module_name: 模块名称 (如 "语音服务")
        module_path: 模块路径 (如 "voice")
        business_name: 业务名称 (如 "音频生成")
        business_path: 业务路径 (如 "audio")
        component: 组件路径 (如 "voice/audio/index")
        icon: 图标
    
    Returns:
        {'directory_id': int, 'page_id': int, 'button_ids': List[int]}
        
    Example:
        create_module(
            module_name="语音服务",
            module_path="voice",
            business_name="音频生成",
            business_path="audio",
            component="voice/audio/index",
            icon="message"
        )
    """
    async def _create():
        manager = MenuManager()
        result = await manager.create_module_menus(
            module_name=module_name,
            module_path=module_path,
            business_name=business_name,
            business_path=business_path,
            component=component,
            icon=icon,
        )
        await manager._close_db()
        return result
    
    return asyncio.run(_create())


def list_menus(parent: str = None) -> List[Dict]:
    """
    列出菜单
    
    Args:
        parent: 父菜单名称 (可选)
    
    Returns:
        菜单列表
    """
    async def _list():
        manager = MenuManager()
        parent_id = None
        if parent:
            p = await manager.get_menu_by_name(parent)
            if p:
                parent_id = p.menu_id
        result = await manager.list_menus(parent_id)
        await manager._close_db()
        return result
    
    return asyncio.run(_list())


def delete_menu(name: str) -> bool:
    """
    删除菜单
    
    Args:
        name: 菜单名称
    
    Returns:
        是否成功
    """
    async def _delete():
        manager = MenuManager()
        result = await manager.delete_menu(name=name)
        await manager._close_db()
        return result
    
    return asyncio.run(_delete())


def move_menu(name: str, parent: str) -> bool:
    """
    移动菜单
    
    Args:
        name: 菜单名称
        parent: 新的父菜单名称
    
    Returns:
        是否成功
    """
    async def _move():
        manager = MenuManager()
        result = await manager.move_menu(name, parent)
        await manager._close_db()
        return result
    
    return asyncio.run(_move())


async def print_menu_tree_async():
    """打印菜单树 (异步版本)"""
    manager = MenuManager()
    menus = await manager.list_menus()
    await manager._close_db()
    _print_tree(menus)


def _print_tree(menus):
    """打印菜单树"""
    
    # 构建树
    menu_map = {m['menu_id']: m for m in menus}
    roots = [m for m in menus if m['parent_id'] == 0]
    
    def print_node(menu, level=0):
        indent = "  " * level
        type_icon = {'M': '📁', 'C': '📄', 'F': '🔘'}.get(menu['menu_type'], '❓')
        print(f"{indent}{type_icon} {menu['menu_name']} (ID:{menu['menu_id']}, path:{menu['path']}, perms:{menu['perms']})")
        
        children = [m for m in menus if m['parent_id'] == menu['menu_id']]
        for child in sorted(children, key=lambda x: x['order_num']):
            print_node(child, level + 1)
    
    print("\n📋 菜单树:")
    print("=" * 60)
    for root in sorted(roots, key=lambda x: x['order_num']):
        print_node(root)


# ============ 命令行入口 ============

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='若依菜单管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # add-dir 命令
    add_dir_parser = subparsers.add_parser('add-dir', help='添加目录菜单')
    add_dir_parser.add_argument('--name', required=True, help='目录名称')
    add_dir_parser.add_argument('--path', required=True, help='路由路径')
    add_dir_parser.add_argument('--icon', default='#', help='图标')
    add_dir_parser.add_argument('--order', type=int, default=0, help='排序')
    add_dir_parser.add_argument('--parent', help='父菜单名称')
    
    # add-menu 命令
    add_menu_parser = subparsers.add_parser('add-menu', help='添加页面菜单')
    add_menu_parser.add_argument('--name', required=True, help='菜单名称')
    add_menu_parser.add_argument('--path', required=True, help='路由路径')
    add_menu_parser.add_argument('--component', required=True, help='组件路径')
    add_menu_parser.add_argument('--perms', required=True, help='权限标识')
    add_menu_parser.add_argument('--parent', help='父菜单名称')
    add_menu_parser.add_argument('--icon', default='#', help='图标')
    add_menu_parser.add_argument('--order', type=int, default=1, help='排序')
    
    # add-button 命令
    add_btn_parser = subparsers.add_parser('add-button', help='添加按钮权限')
    add_btn_parser.add_argument('--name', required=True, help='按钮名称')
    add_btn_parser.add_argument('--perms', required=True, help='权限标识')
    add_btn_parser.add_argument('--parent', required=True, help='父菜单名称')
    add_btn_parser.add_argument('--order', type=int, default=1, help='排序')
    
    # add-crud 命令
    add_crud_parser = subparsers.add_parser('add-crud', help='添加CRUD按钮')
    add_crud_parser.add_argument('--parent', required=True, help='父菜单名称')
    add_crud_parser.add_argument('--module', required=True, help='模块名')
    add_crud_parser.add_argument('--business', required=True, help='业务名')
    
    # create-module 命令
    create_parser = subparsers.add_parser('create-module', help='创建完整模块菜单')
    create_parser.add_argument('--module-name', required=True, help='模块名称')
    create_parser.add_argument('--module-path', required=True, help='模块路径')
    create_parser.add_argument('--business-name', required=True, help='业务名称')
    create_parser.add_argument('--business-path', required=True, help='业务路径')
    create_parser.add_argument('--component', required=True, help='组件路径')
    create_parser.add_argument('--icon', default='#', help='图标')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出菜单')
    list_parser.add_argument('--parent', help='父菜单名称')
    list_parser.add_argument('--tree', action='store_true', help='树形显示')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除菜单')
    delete_parser.add_argument('--name', required=True, help='菜单名称')
    delete_parser.add_argument('--recursive', '-r', action='store_true', help='递归删除子菜单')
    
    # move 命令
    move_parser = subparsers.add_parser('move', help='移动菜单')
    move_parser.add_argument('--name', required=True, help='菜单名称')
    move_parser.add_argument('--parent', required=True, help='新的父菜单名称')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = MenuManager()
    
    try:
        if args.command == 'add-dir':
            parent_id = 0
            if args.parent:
                p = await manager.get_menu_by_name(args.parent)
                if p:
                    parent_id = p.menu_id
            await manager.add_directory(args.name, args.path, args.icon, args.order, parent_id)
            
        elif args.command == 'add-menu':
            await manager.add_menu(
                name=args.name,
                path=args.path,
                component=args.component,
                perms=args.perms,
                parent_name=args.parent,
                icon=args.icon,
                order=args.order,
            )
            
        elif args.command == 'add-button':
            await manager.add_button(args.name, args.perms, args.parent, order=args.order)
            
        elif args.command == 'add-crud':
            await manager.add_crud_buttons(args.parent, args.module, args.business)
            
        elif args.command == 'create-module':
            await manager.create_module_menus(
                module_name=args.module_name,
                module_path=args.module_path,
                business_name=args.business_name,
                business_path=args.business_path,
                component=args.component,
                icon=args.icon,
            )
            
        elif args.command == 'list':
            if args.tree:
                menus = await manager.list_menus()
                _print_tree(menus)
            else:
                parent_id = None
                if args.parent:
                    p = await manager.get_menu_by_name(args.parent)
                    if p:
                        parent_id = p.menu_id
                menus = await manager.list_menus(parent_id)
                print(f"\n📋 菜单列表 (共 {len(menus)} 条):")
                print("-" * 80)
                for m in menus:
                    type_name = {'M': '目录', 'C': '菜单', 'F': '按钮'}.get(m['menu_type'], '未知')
                    print(f"  [{m['menu_id']:3d}] {m['menu_name']:20s} | {type_name} | {m['path'] or '-':15s} | {m['perms'] or '-'}")
                    
        elif args.command == 'delete':
            await manager.delete_menu(name=args.name, recursive=args.recursive)
            
        elif args.command == 'move':
            await manager.move_menu(args.name, args.parent)
            
    finally:
        await manager._close_db()


if __name__ == '__main__':
    asyncio.run(main())
