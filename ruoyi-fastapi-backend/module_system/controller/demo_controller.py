from datetime import datetime
from fastapi import APIRouter, Depends, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_system.service.demo_service import DemoService
from module_system.entity.vo.demo_vo import DemoModel, DemoPageQueryModel, DeleteDemoModel
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


demoController = APIRouter(prefix='/system/demo', dependencies=[Depends(LoginService.get_current_user)])


@demoController.get('/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('system:demo:list'))])
async def get_demo_list(
    request: Request,
    query: DemoPageQueryModel = Depends(DemoPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """获取演示ID列表"""
    result = await DemoService.get_demo_list_services(query_db, query, is_page=True)
    return ResponseUtil.success(model_content=result)


@demoController.post('', dependencies=[Depends(CheckUserInterfaceAuth('system:demo:add'))])
@Log(title='演示ID', business_type=BusinessType.INSERT)
async def add_demo(
    request: Request,
    obj: DemoModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增演示ID"""
    obj.create_by = current_user.user.user_name
    obj.create_time = datetime.now()
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await DemoService.add_demo_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@demoController.put('', dependencies=[Depends(CheckUserInterfaceAuth('system:demo:edit'))])
@Log(title='演示ID', business_type=BusinessType.UPDATE)
async def update_demo(
    request: Request,
    obj: DemoModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新演示ID"""
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await DemoService.update_demo_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@demoController.delete('/{ids}', dependencies=[Depends(CheckUserInterfaceAuth('system:demo:remove'))])
@Log(title='演示ID', business_type=BusinessType.DELETE)
async def delete_demo(request: Request, ids: str, query_db: AsyncSession = Depends(get_db)):
    """删除演示ID"""
    result = await DemoService.delete_demo_services(query_db, DeleteDemoModel(idIds=ids))
    return ResponseUtil.success(msg=result.message)


@demoController.get('/{id}', dependencies=[Depends(CheckUserInterfaceAuth('system:demo:query'))])
async def get_demo_by_id(request: Request, id: int, query_db: AsyncSession = Depends(get_db)):
    """获取演示ID详情"""
    result = await DemoService.get_demo_by_id_services(query_db, id)
    return ResponseUtil.success(data=result)
