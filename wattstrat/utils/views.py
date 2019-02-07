
class MenuMixin(object):
    menus = []

    def get_context_data(self, **kwargs):
        return super().get_context_data(active_menus=self.menus, **kwargs)
