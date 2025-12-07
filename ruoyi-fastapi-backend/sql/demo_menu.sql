-- 演示ID菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('演示ID', 0, 1, 'demo', 'system/demo/index', 1, 0, 'C', '0', '0', 'system:demo:list', '#', 'admin', NOW(), '', NULL, '演示ID菜单');

-- 按钮权限
SET @parentId = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('演示ID查询', @parentId, 1, '', '', 1, 0, 'F', '0', '0', 'system:demo:query', '#', 'admin', NOW(), '', NULL, ''),
('演示ID新增', @parentId, 2, '', '', 1, 0, 'F', '0', '0', 'system:demo:add', '#', 'admin', NOW(), '', NULL, ''),
('演示ID修改', @parentId, 3, '', '', 1, 0, 'F', '0', '0', 'system:demo:edit', '#', 'admin', NOW(), '', NULL, ''),
('演示ID删除', @parentId, 4, '', '', 1, 0, 'F', '0', '0', 'system:demo:remove', '#', 'admin', NOW(), '', NULL, ''),
('演示ID导出', @parentId, 5, '', '', 1, 0, 'F', '0', '0', 'system:demo:export', '#', 'admin', NOW(), '', NULL, '');
