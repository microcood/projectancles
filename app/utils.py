from apistar import Component


def get_component(component_type: Component):
    from app import app

    def get(c: component_type):
        return c

    return app.http_injector.run(get)
