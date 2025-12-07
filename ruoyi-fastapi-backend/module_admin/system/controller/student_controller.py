from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_admin.system.service.student_service import StudentService
from module_admin.system.entity.vo.student_vo import DeleteStudentModel, StudentModel, StudentPageQueryModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


studentController = APIRouter(prefix='/student/info', dependencies=[Depends(LoginService.get_current_user)])


@studentController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('student:info:list'))]
)
async def get_system_student_list(
    request: Request,
student_page_query: StudentPageQueryModel = Depends(StudentPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    student_page_query_result = await StudentService.get_student_list_services(query_db, student_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=student_page_query_result)


@studentController.post('', dependencies=[Depends(CheckUserInterfaceAuth('student:info:add'))])
@ValidateFields(validate_model='add_student')
@Log(title='【请填写功能名称】', business_type=BusinessType.INSERT)
async def add_system_student(
    request: Request,
    add_student: StudentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_student.create_by = current_user.user.user_name
    add_student.create_time = datetime.now()
    add_student.update_by = current_user.user.user_name
    add_student.update_time = datetime.now()
    add_student_result = await StudentService.add_student_services(query_db, add_student)
    logger.info(add_student_result.message)

    return ResponseUtil.success(msg=add_student_result.message)


@studentController.put('', dependencies=[Depends(CheckUserInterfaceAuth('student:info:edit'))])
@ValidateFields(validate_model='edit_student')
@Log(title='【请填写功能名称】', business_type=BusinessType.UPDATE)
async def edit_system_student(
    request: Request,
    edit_student: StudentModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_student.update_by = current_user.user.user_name
    edit_student.update_time = datetime.now()
    edit_student_result = await StudentService.edit_student_services(query_db, edit_student)
    logger.info(edit_student_result.message)

    return ResponseUtil.success(msg=edit_student_result.message)


@studentController.delete('/{student_ids}', dependencies=[Depends(CheckUserInterfaceAuth('student:info:remove'))])
@Log(title='【请填写功能名称】', business_type=BusinessType.DELETE)
async def delete_system_student(request: Request, student_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_student = DeleteStudentModel(studentIds=student_ids)
    delete_student_result = await StudentService.delete_student_services(query_db, delete_student)
    logger.info(delete_student_result.message)

    return ResponseUtil.success(msg=delete_student_result.message)


@studentController.get(
    '/{student_id}', response_model=StudentModel, dependencies=[Depends(CheckUserInterfaceAuth('student:info:query'))]
)
async def query_detail_system_student(request: Request, student_id: int, query_db: AsyncSession = Depends(get_db)):
    student_detail_result = await StudentService.student_detail_services(query_db, student_id)
    logger.info(f'获取student_id为{student_id}的信息成功')

    return ResponseUtil.success(data=student_detail_result)


@studentController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('student:info:export'))])
@Log(title='【请填写功能名称】', business_type=BusinessType.EXPORT)
async def export_system_student_list(
    request: Request,
    student_page_query: StudentPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    student_query_result = await StudentService.get_student_list_services(query_db, student_page_query, is_page=False)
    student_export_result = await StudentService.export_student_list_services(student_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(student_export_result))
