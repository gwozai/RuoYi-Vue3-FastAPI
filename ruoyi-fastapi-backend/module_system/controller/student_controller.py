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
from module_system.service.student_service import StudentService
from module_system.entity.vo.student_vo import StudentModel, StudentPageQueryModel, DeleteStudentModel
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


studentController = APIRouter(prefix='/system/student', dependencies=[Depends(LoginService.get_current_user)])


@studentController.get('/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('system:student:list'))])
async def get_student_list(
    request: Request,
    query: StudentPageQueryModel = Depends(StudentPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """获取学生信息列表"""
    result = await StudentService.get_student_list_services(query_db, query, is_page=True)
    return ResponseUtil.success(model_content=result)


@studentController.post('', dependencies=[Depends(CheckUserInterfaceAuth('system:student:add'))])
@Log(title='学生信息', business_type=BusinessType.INSERT)
async def add_student(
    request: Request,
    obj: StudentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增学生信息"""
    obj.create_by = current_user.user.user_name
    obj.create_time = datetime.now()
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await StudentService.add_student_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@studentController.put('', dependencies=[Depends(CheckUserInterfaceAuth('system:student:edit'))])
@Log(title='学生信息', business_type=BusinessType.UPDATE)
async def update_student(
    request: Request,
    obj: StudentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新学生信息"""
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await StudentService.update_student_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@studentController.delete('/{ids}', dependencies=[Depends(CheckUserInterfaceAuth('system:student:remove'))])
@Log(title='学生信息', business_type=BusinessType.DELETE)
async def delete_student(request: Request, ids: str, query_db: AsyncSession = Depends(get_db)):
    """删除学生信息"""
    result = await StudentService.delete_student_services(query_db, DeleteStudentModel(studentIds=ids))
    return ResponseUtil.success(msg=result.message)


@studentController.get('/{student_id}', dependencies=[Depends(CheckUserInterfaceAuth('system:student:query'))])
async def get_student_by_id(request: Request, student_id: int, query_db: AsyncSession = Depends(get_db)):
    """获取学生信息详情"""
    result = await StudentService.get_student_by_id_services(query_db, student_id)
    return ResponseUtil.success(data=result)
