"""字段校验器：链式调用，一次性收集所有字段错误。"""

import re
from decimal import Decimal

from ..constants import EnumGroup
from ..errors import ValidationError
from ..utils.dates import parse_date
from ..utils.numbers import to_decimal

PHONE_PATTERN = re.compile(r"^[0-9+\-() ]{6,24}$")


class PayloadValidator:
    """按字段校验请求体。

    用法::

        data = (
            PayloadValidator(payload)
            .string("name", "绿地名称", required=True, max_length=128)
            .enum("green_type", "绿地类型", group=GREEN_SPACE_TYPE, required=True)
            .done()
        )

    只有请求体中出现的字段才会写入结果字典，便于覆盖式更新。
    """

    def __init__(self, data):
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise ValidationError("请求体必须是 JSON 对象")
        self.raw = data
        self.clean = {}
        self.errors = {}

    # ------------------------------------------------------------ 内部工具
    def _fail(self, field, message):
        self.errors.setdefault(field, message)

    def _provided(self, field):
        return field in self.raw

    @staticmethod
    def _blank(value):
        return value is None or (isinstance(value, str) and not value.strip())

    def _skip(self, field, label, required, default):
        """字段未出现在请求体中的处理。"""

        if required:
            self._fail(field, f"{label}不能为空")
        elif default is not None:
            self.clean[field] = default
        return self

    # ------------------------------------------------------------ 字段类型
    def string(self, field, label, *, required=False, max_length=255, default=None,
               pattern=None, pattern_message=None):
        if not self._provided(field):
            return self._skip(field, label, required, default)
        value = self.raw[field]
        if self._blank(value):
            if required:
                self._fail(field, f"{label}不能为空")
            else:
                self.clean[field] = None
            return self
        if not isinstance(value, str):
            value = str(value)
        value = value.strip()
        if len(value) > max_length:
            self._fail(field, f"{label}长度不能超过 {max_length} 个字符")
        if pattern is not None and not pattern.match(value):
            self._fail(field, pattern_message or f"{label}格式不正确")
        self.clean[field] = value
        return self

    def text(self, field, label, *, required=False, max_length=4000, default=None):
        return self.string(field, label, required=required, max_length=max_length, default=default)

    def enum(self, field, label, *, group: EnumGroup, required=False, default=None):
        if not self._provided(field):
            return self._skip(field, label, required, default)
        value = self.raw[field]
        if self._blank(value):
            if required:
                self._fail(field, f"{label}不能为空")
            else:
                self.clean[field] = None
            return self
        value = str(value).strip()
        if not group.has(value):
            self._fail(field, f"{label}取值不合法，可选值：{'、'.join(group.values)}")
            return self
        self.clean[field] = value
        return self

    def date(self, field, label, *, required=False, default=None):
        if not self._provided(field):
            return self._skip(field, label, required, default)
        value = self.raw[field]
        if self._blank(value):
            if required:
                self._fail(field, f"{label}不能为空")
            else:
                self.clean[field] = None
            return self
        try:
            self.clean[field] = parse_date(value, label)
        except ValueError as exc:
            self._fail(field, str(exc))
        return self

    def number(self, field, label, *, required=False, default=None, min_value=None, max_value=None,
               digits=2):
        if not self._provided(field):
            return self._skip(field, label, required, default)
        value = self.raw[field]
        if self._blank(value):
            if required:
                self._fail(field, f"{label}不能为空")
            else:
                self.clean[field] = None
            return self
        try:
            number = to_decimal(value, label)
        except ValueError as exc:
            self._fail(field, str(exc))
            return self
        if min_value is not None and number < Decimal(str(min_value)):
            self._fail(field, f"{label}不能小于 {min_value}")
        if max_value is not None and number > Decimal(str(max_value)):
            self._fail(field, f"{label}不能大于 {max_value}")
        self.clean[field] = number.quantize(Decimal(1).scaleb(-digits))
        return self

    def integer(self, field, label, *, required=False, default=None, min_value=None, max_value=None):
        if not self._provided(field):
            return self._skip(field, label, required, default)
        value = self.raw[field]
        if self._blank(value):
            if required:
                self._fail(field, f"{label}不能为空")
            else:
                self.clean[field] = None
            return self
        try:
            number = int(str(value).strip())
        except (TypeError, ValueError):
            self._fail(field, f"{label}必须是整数")
            return self
        if min_value is not None and number < min_value:
            self._fail(field, f"{label}不能小于 {min_value}")
        if max_value is not None and number > max_value:
            self._fail(field, f"{label}不能大于 {max_value}")
        self.clean[field] = number
        return self

    def done(self):
        if self.errors:
            raise ValidationError("提交的数据未通过校验", details=self.errors)
        return self.clean
