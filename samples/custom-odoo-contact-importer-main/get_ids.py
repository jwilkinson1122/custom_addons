# get the country id based on the country name
def get_country_id(models, db, uid, password, country_name):
    country_ids = models.execute_kw(db, uid, password, "res.country", "search", [[('name', '=', country_name)]])
    return country_ids[0] if country_ids else False

# get the state id based on the state name
def get_state_id(models, db, uid, password, country_id, state_name):
    state_ids = models.execute_kw(db, uid, password, "res.country.state", "search", [[("name", "=", state_name), ("country_id", "=", country_id)]])
    return state_ids[0] if state_ids else False 

# get all the contacts  
def get_existing_contacts(models, db, uid, password):
    try:
        existing_contacts = models.execute_kw(db, uid, password, 'res.partner', 'search_read', 
            [[('name', '!=', False), ('email', '!=', False)]], 
            {'fields': ['name', 'email']}
        )
        return existing_contacts

    except Exception as e:
        print(f"Erro ao buscar contatos existentes: {e}")
        return []