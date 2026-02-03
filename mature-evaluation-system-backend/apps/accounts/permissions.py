from rest_framework.permissions import BasePermission


class IsRegionAdmin(BasePermission):
    message = "仅区域管理员可访问"

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "role", None) == "region_admin")


def get_user_region(user):
    # 你 Region 模型里 related_name='managed_region'
    return getattr(user, "managed_region", None)
