from rest_framework.permissions import BasePermission


class IsRegionAdmin(BasePermission):
    message = "需要区域管理员权限"

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "role", None) != "region_admin":
            return False
        # 必须绑定区县
        return hasattr(user, "managed_region") and user.managed_region is not None
