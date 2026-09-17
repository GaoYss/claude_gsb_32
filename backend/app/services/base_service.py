"""Service 基类：统一编号生成、事务提交与冲突处理。"""

from sqlalchemy.exc import IntegrityError

from ..errors import ConflictError, NotFoundError
from ..extensions import db
from .code_generator import next_code


class BaseService:
    """所有业务 service 的公共骨架。"""

    model = None
    label = "记录"
    code_field = None          # 业务编号字段名，None 表示无编号
    code_width = 4
    MAX_CODE_RETRY = 5

    # ------------------------------------------------------------ 编号
    @classmethod
    def code_prefix(cls):
        """编号前缀，子类按业务规则覆盖。"""

        return ""

    @classmethod
    def generate_code(cls):
        return next_code(
            cls.model, getattr(cls.model, cls.code_field), cls.code_prefix(), cls.code_width
        )

    # ------------------------------------------------------------ 查询
    @classmethod
    def get(cls, obj_id):
        instance = db.session.get(cls.model, obj_id)
        if instance is None:
            raise NotFoundError(f"{cls.label}不存在或已被删除")
        return instance

    # ------------------------------------------------------------ 写入
    @classmethod
    def prepare_instance(cls, instance, payload):
        """入库前校验关联对象并补齐派生字段，子类覆盖。"""

    @classmethod
    def prepare_update(cls, instance, payload):
        """更新前校验，子类覆盖。"""

        cls.prepare_instance(instance, payload)

    @classmethod
    def apply_derived(cls, instance):
        """字段全部赋值后做派生计算（金额、完成时间等），子类覆盖。"""

    @classmethod
    def after_create(cls, instance, payload):
        """同一事务内的跨模块联动，子类覆盖。"""

    @classmethod
    def after_update(cls, instance, payload):
        """更新后的联动，子类覆盖。"""

    @classmethod
    def after_delete(cls, instance):
        """删除后的联动，子类覆盖。"""

    @classmethod
    def create(cls, data):
        data = dict(data)
        provided_code = bool(data.get(cls.code_field)) if cls.code_field else False
        attempts = 1 if provided_code else cls.MAX_CODE_RETRY
        last_error = None

        for _ in range(attempts):
            payload = dict(data)
            if cls.code_field and not payload.get(cls.code_field):
                payload[cls.code_field] = cls.generate_code()

            instance = cls.model(**payload)
            cls.prepare_instance(instance, payload)
            cls.apply_derived(instance)
            db.session.add(instance)
            try:
                db.session.flush()
            except IntegrityError as exc:
                db.session.rollback()
                last_error = exc
                if provided_code:
                    raise ConflictError(
                        f"{cls.label}编号 {payload[cls.code_field]} 已存在，请更换后重试"
                    ) from exc
                continue

            cls.after_create(instance, payload)
            db.session.commit()
            return instance

        raise ConflictError(f"{cls.label}编号生成冲突，请稍后重试") from last_error

    @classmethod
    def update(cls, obj_id, data):
        instance = cls.get(obj_id)
        payload = dict(data)
        if cls.code_field:
            # 业务编号是外部引用依据，创建后不允许修改
            payload.pop(cls.code_field, None)

        cls.prepare_update(instance, payload)
        for field, value in payload.items():
            setattr(instance, field, value)
        cls.apply_derived(instance)
        try:
            db.session.flush()
        except IntegrityError as exc:
            db.session.rollback()
            raise ConflictError(f"{cls.label}数据与已有记录冲突") from exc
        cls.after_update(instance, payload)
        db.session.commit()
        return instance

    @classmethod
    def delete(cls, obj_id):
        instance = cls.get(obj_id)
        db.session.delete(instance)
        db.session.flush()
        cls.after_delete(instance)
        db.session.commit()
        return instance
