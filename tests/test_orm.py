
def check_column_property(column, values):
    if  column.attribute_name != values['attribute_name'] or \
        column.strategy != values['strategy'] or \
        column.column.name != values['column']:
        return False
    
    return True


def check_relationship_property(relationship, values):
    if relationship.attribute_name != values['attribute_name'] or \
       relationship.strategy != values['strategy'] or \
       relationship.join_column.column.name != values['column'] or \
       relationship.mapping != values['mapping'] or \
       relationship.__class__.__name__ != values['type'] or \
       relationship.reference._class.__name__ != values['reference']:
        return False
    
    if values['type'] == 'ToMany' and \
       relationship.secondary_join_column is not None and \
       relationship.secondary_table is not None and \
       relationship.secondary_join_column.column.name != values['second_column'] and \
       relationship.secondary_table.name != values['second_table']:
        return False
    
    return True


def test_table_naming(model, table_name):
    assert model.table.name is table_name


def test_model_columns(model, columns):
    assert all(check_column_property(column, value) 
                for column, value in zip(
                    model.columns(with_base = False), 
                    columns, 
                    strict = True
                )
            )


def test_model_column_with_base(submodel, columns_with_base):
    assert all(check_column_property(column, value) 
                for column, value in zip(
                    submodel.columns(with_base = True), 
                    columns_with_base, 
                    strict = True
                )
            )


def test_model_relationships(model, relationships):
    assert all(check_relationship_property(relationship, value) 
                for relationship, value in zip(
                    model.relationships(with_base = False), 
                    relationships, 
                    strict = True
                )
            )


def test_table_columns(model, schema):
    columns = [column.name for column in model.table.columns]
    
    columns.sort()
    schema.sort()

    assert columns == schema







