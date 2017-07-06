import glance_api.modules.models

def order_by(session):
    bla = [x for x in session.query(glance_api.modules.models.Tag).join(glance_api.modules.models.Tag.items).order_by(glance_api.modules.models.Item.id)]
    return bla
