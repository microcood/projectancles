from apistar import typesystem


class ModelType(typesystem.Object):
    render_fields = []

    def render(self):
        return {k: self[k] for k in self.render_fields}
