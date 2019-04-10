import datetime

from initializer.neo4j_queries import create_execution_node


def main():
    number_of_executions = 5
    execution_delta_time = datetime.timedelta(minutes=5)
    combinations = [["dockercompose_queue-master_1", "dockercompose_rabbitmq_1", "dockercompose_shipping_1"],
                    ["dockercompose_payment_1", "dockercompose_orders_1", "dockercompose_orders-db_1"],
                    ["dockercompose_carts_1", "dockercompose_carts-db_1"],
                    ["dockercompose_edge-router_1", "dockercompose_front-end_1", "dockercompose_catalogue_1", "dockercompose_catalogue-db_1"],
                    ["dockercompose_user_1", "dockercompose_user-db_1"]]
    now = datetime.datetime.now()
    create_execution_node(5, now-execution_delta_time, now, combinations)




if __name__ == '__main__':
    main()
