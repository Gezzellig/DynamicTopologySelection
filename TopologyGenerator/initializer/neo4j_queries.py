from initializer import neo4j_driver


def retrieve_all_container_names_command(tx):
    return tx.run("MATCH (n:IMAGE) RETURN n.container_name AS container_name")


def retrieve_all_container_names():
    container_names = []
    with neo4j_driver.driver.session() as session:
        containers_holder = session.write_transaction(retrieve_all_container_names_command)
    for container_holder in containers_holder:
        container_names.append(container_holder["container_name"])
    return container_names
