import xmlrpc.client
import csv
import os
import time
from dotenv import load_dotenv
from get_ids import get_country_id, get_state_id, get_existing_contacts
import logging

load_dotenv()

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Importa dados do CSV e retorna uma lista de contatos
def import_csv_contacts(file_name):
    logger.info(f"Diretório atual: {os.getcwd()}")

    if not os.path.isfile(file_name):
        logger.error(f"Arquivo '{file_name}' não encontrado no diretório atual.")
        return

    try:
        with open(file_name, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            contacts = []
            invalid_contacts = []

            # Controle para evitar duplicatas no CSV
            seen_names = set()
            seen_emails = set()

            logger.info("\nRegistros válidos do arquivo:")

            for row_index, row in enumerate(reader, start=1):
                contact_name = (row.get("Nome completo") or "").strip()
                contact_email = (row.get("E-mail") or "").strip()

                # Verifica duplicatas no CSV
                if contact_name in seen_names or contact_email in seen_emails:
                    continue

                seen_names.add(contact_name)
                seen_emails.add(contact_email)

                contact = {
                    "name": contact_name,
                    "email": contact_email,
                    "function": (row.get("Cargo") or "").strip(),
                    "company_name": (row.get("Nome da empresa") or "").strip(),
                    "city": (row.get("Cidade") or "").strip(),
                    "country_id": (row.get("País") or "").strip(),
                    "state_id": (row.get("Estado") or "").strip(),
                    "street": (row.get("Localização") or "").strip(),
                    "website": (row.get("LinkedIn") or "").strip(),
                    "x_redes_sociais": (
                        row.get("Usuário - redes sociais") or ""
                    ).strip(),
                    "x_setor": (row.get("Setor") or "").strip(),
                    "x_info_empresa": f"""
                        Nome: {(row.get("Nome da empresa") or "").strip()}
                        Localização: {(row.get("Localização da empresa") or "").strip()}
                        Telefone da sede: {(row.get("Telefone da sede") or "").strip()}
                        Setor: {(row.get("Setor da empresa") or "").strip()}
                        Tamanho: {(row.get("Tamanho da empresa") or "").strip()}
                        URL: {(row.get("URL da empresa") or "").strip()}
                        Redes Sociais: {(row.get("Empresa - redes sociais") or "").strip()}
                    """,
                }

                if not contact["name"] or not contact["email"]:
                    invalid_contacts.append(
                        f"Registro {row_index}, {contact['name']}, {contact['email']}"
                    )
                    continue

                logger.info(
                    f"Registro {row_index}, Nome: {contact['name']}, Email: {contact['email']}"
                )
                contacts.append(contact)

            if invalid_contacts:
                logger.warning("\nRegistros inválidos:")
                for i in invalid_contacts:
                    logger.warning(i)

            return contacts

    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo: {e}")


# Autentica o usuário no Odoo
def authenticate(url, db, username, password):
    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, username, password, {})

        if not uid:
            raise ValueError("Falha na autenticação. Verifique as credenciais.")
        return uid

    except Exception as e:
        logger.error(f"Erro ao autenticar: {e}")


# Verifica se o contato já existe no Odoo
def contact_exists_odoo(existing_contacts, contact):
    return contact["name"] in existing_contacts or contact["email"] in existing_contacts


# Cache para country_id e state_id
country_cache = {}
state_cache = {}


def get_country_id_cached(models, db, uid, password, country_name):
    if country_name in country_cache:
        return country_cache[country_name]

    country_id = get_country_id(models, db, uid, password, country_name)
    if country_id:
        country_cache[country_name] = country_id

    return country_id


def get_state_id_cached(models, db, uid, password, country_id, state_name):
    state_cache_key = (country_id, state_name)
    if state_cache_key in state_cache:
        return state_cache[state_cache_key]

    state_id = get_state_id(models, db, uid, password, country_id, state_name)
    if state_id:
        state_cache[state_cache_key] = state_id

    return state_id


# Divide os contatos em lotes menores
def create_contacts_in_batches(contacts, batch_size):
    for i in range(0, len(contacts), batch_size):
        yield contacts[i : i + batch_size]


# Cria os contatos no Odoo
def create_contacts(url, db, uid, password, contacts):
    try:
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        existing_contacts = get_existing_contacts(models, db, uid, password)
        existing_contacts_set = {(c["name"], c["email"]) for c in existing_contacts}

        batch_size = int(
            os.getenv("BATCH_SIZE", 50)
        )  # Default para 50 contatos por lote

        for batch in create_contacts_in_batches(contacts, batch_size):
            for contact in batch:
                try:
                    if contact_exists_odoo(existing_contacts_set, contact):
                        logger.info(
                            f"{contact['name']} ou o email {contact['email']} já existe no banco de dados."
                        )
                        continue

                    country_id = get_country_id_cached(
                        models, db, uid, password, contact["country_id"]
                    )
                    state_id = get_state_id_cached(
                        models, db, uid, password, country_id, contact["state_id"]
                    )

                    contact["state_id"] = state_id or ""
                    contact["country_id"] = country_id or ""

                    contact_id = models.execute_kw(
                        db, uid, password, "res.partner", "create", [contact]
                    )
                    logger.info(f"{contact['name']} criado com o ID: {contact_id}")

                except Exception as e:
                    logger.error(f"Erro ao criar contato {contact['name']}: {e}")

    except Exception as e:
        logger.error(f"Erro ao criar contatos: {e}")


def main():
    # Credenciais do Odoo
    odoo_url = os.getenv("ODOO_URL")
    odoo_db = os.getenv("ODOO_DB")
    odoo_username = os.getenv("ODOO_USERNAME")
    odoo_password = os.getenv("ODOO_PASSWORD")

    uid = authenticate(odoo_url, odoo_db, odoo_username, odoo_password)
    if uid:
        contacts = import_csv_contacts("test.csv")

        if contacts:
            logger.info(f"\nTotal de contatos para serem carregados: {len(contacts)}\n")
            create_contacts(odoo_url, odoo_db, uid, odoo_password, contacts)


if __name__ == "__main__":
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    logger.info(f"Tempo de execução: {elapsed_time:.2f} segundos")
